"""Comprehensive Phase 2 security hardening regression tests for DHAVLO MI."""

from __future__ import annotations

import asyncio
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from fastapi import HTTPException
from pydantic import ValidationError

from acestep.api.http.auth import (
    get_api_key,
    is_production_mode,
    set_api_key,
    verify_api_key,
    verify_token_from_request,
)
from acestep.api.http.release_task_audio_paths import (
    ALLOWED_AUDIO_EXTENSIONS,
    save_upload_to_temp,
    validate_audio_path,
)
from acestep.api.http.release_task_models import GenerateMusicRequest
from acestep.api.model_download import ensure_model_downloaded


class _MockUploadFile:
    """Mock upload stream for exercising upload limits and validations."""

    def __init__(self, data: bytes, filename: str = "sample.wav"):
        self._data = data
        self._pos = 0
        self.filename = filename
        self.closed = False

    async def read(self, chunk_size: int = 1024 * 1024) -> bytes:
        if self._pos >= len(self._data):
            return b""
        end = min(self._pos + chunk_size, len(self._data))
        chunk = self._data[self._pos:end]
        self._pos = end
        return chunk

    async def close(self) -> None:
        self.closed = True


class SecurityHardeningTests(unittest.TestCase):
    """Regression test suite for Phase 2 application security hardening."""

    def setUp(self) -> None:
        set_api_key(None)

    def tearDown(self) -> None:
        set_api_key(None)

    # -------------------------------------------------------------------------
    # Authentication & Production Fail-Closed Tests
    # -------------------------------------------------------------------------

    def test_auth_timing_safe_matches_valid_tokens(self) -> None:
        """Configured API key must be matched correctly via timing-safe comparison."""
        set_api_key("super-secret-key-42")
        self.assertEqual("super-secret-key-42", get_api_key())

        # Body token match
        token = verify_token_from_request({"ai_token": "super-secret-key-42"})
        self.assertEqual("super-secret-key-42", token)

        # Bearer header match
        token2 = verify_token_from_request({}, authorization="Bearer super-secret-key-42")
        self.assertEqual("super-secret-key-42", token2)

    def test_auth_rejects_invalid_or_manipulated_tokens(self) -> None:
        """Invalid tokens must raise HTTP 401 with consistent error details."""
        set_api_key("super-secret-key-42")

        with self.assertRaises(HTTPException) as ctx1:
            verify_token_from_request({"ai_token": "wrong-token"})
        self.assertEqual(401, ctx1.exception.status_code)

        with self.assertRaises(HTTPException) as ctx2:
            verify_token_from_request({}, authorization="Bearer wrong-key")
        self.assertEqual(401, ctx2.exception.status_code)

    def test_production_fails_closed_when_key_is_missing(self) -> None:
        """In production mode, unconfigured auth must fail closed (raise HTTP 500)."""
        with mock.patch.dict(os.environ, {"DHAVLO_MI_ENV": "production"}):
            self.assertTrue(is_production_mode())
            set_api_key(None)

            with self.assertRaises(HTTPException) as ctx1:
                verify_token_from_request({})
            self.assertEqual(500, ctx1.exception.status_code)
            self.assertIn("API key required in production", ctx1.exception.detail)

            with self.assertRaises(HTTPException) as ctx2:
                asyncio.run(verify_api_key(authorization=None))
            self.assertEqual(500, ctx2.exception.status_code)

        # Verify backward compatibility fallback
        with mock.patch.dict(os.environ, {"DHAVLO_MI_ENV": "", "SARIGAMA_ENV": "production"}):
            self.assertTrue(is_production_mode())

    def test_development_allows_unauthenticated_access_when_unset(self) -> None:
        """In development mode, omitting the API key allows open testing."""
        with mock.patch.dict(os.environ, {"DHAVLO_MI_ENV": "development"}):
            self.assertFalse(is_production_mode())
            set_api_key(None)
            self.assertIsNone(verify_token_from_request({}))

    # -------------------------------------------------------------------------
    # File & Path Security Tests
    # -------------------------------------------------------------------------

    def test_path_traversal_rejection(self) -> None:
        """Relative paths with traversal markers must be rejected with HTTP 400."""
        malicious_paths = [
            "../etc/passwd.wav",
            "..\\..\\windows\\system32\\cmd.exe.mp3",
            "audio/../../secret.flac",
            "foo/../../../bar.wav",
        ]
        for path in malicious_paths:
            with self.assertRaises(HTTPException) as ctx:
                validate_audio_path(path)
            self.assertEqual(400, ctx.exception.status_code)
            self.assertIn("path traversal", str(ctx.exception.detail))

    def test_hidden_file_path_rejection(self) -> None:
        """Sensitive or dot-prefixed filenames must be rejected with HTTP 400."""
        hidden_paths = [
            ".env.wav",
            ".git/config.mp3",
            "safe_dir/.hidden.flac",
        ]
        for path in hidden_paths:
            with self.assertRaises(HTTPException) as ctx:
                validate_audio_path(path)
            self.assertEqual(400, ctx.exception.status_code)
            self.assertIn("Hidden or sensitive files are not permitted", str(ctx.exception.detail))

    def test_unsupported_audio_extension_rejection(self) -> None:
        """Non-audio extensions must be rejected with HTTP 400."""
        bad_extensions = ["payload.sh", "virus.exe", "config.json", "script.py", "audio.txt"]
        for path in bad_extensions:
            with self.assertRaises(HTTPException) as ctx:
                validate_audio_path(path)
            self.assertEqual(400, ctx.exception.status_code)
            self.assertIn("Unsupported audio file format", str(ctx.exception.detail))

    def test_upload_extension_validation(self) -> None:
        """save_upload_to_temp must reject uploads without approved audio extensions."""
        bad_upload = _MockUploadFile(data=b"malicious script", filename="exploit.sh")
        with self.assertRaises(HTTPException) as ctx:
            asyncio.run(save_upload_to_temp(bad_upload, prefix="test"))
        self.assertEqual(400, ctx.exception.status_code)
        self.assertIn("Unsupported audio file extension", str(ctx.exception.detail))

    def test_upload_size_limit_enforcement(self) -> None:
        """save_upload_to_temp must reject files exceeding max upload size limit with 413."""
        oversized_data = b"A" * (2 * 1024 * 1024)  # 2MB
        upload = _MockUploadFile(data=oversized_data, filename="clip.wav")

        with mock.patch.dict(os.environ, {"DHAVLO_MI_MAX_UPLOAD_SIZE_MB": "1"}):
            with self.assertRaises(HTTPException) as ctx:
                asyncio.run(save_upload_to_temp(upload, prefix="test"))
            self.assertEqual(413, ctx.exception.status_code)
            self.assertIn("exceeds maximum permitted size", str(ctx.exception.detail))

        # Test fallback
        upload2 = _MockUploadFile(data=oversized_data, filename="clip2.wav")
        with mock.patch.dict(os.environ, {"DHAVLO_MI_MAX_UPLOAD_SIZE_MB": "", "SARIGAMA_MAX_UPLOAD_SIZE_MB": "1"}):
            with self.assertRaises(HTTPException) as ctx:
                asyncio.run(save_upload_to_temp(upload2, prefix="test"))
            self.assertEqual(413, ctx.exception.status_code)

    def test_model_download_path_traversal_rejection(self) -> None:
        """ensure_model_downloaded must sanitize model_name against path escape."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            for bad_name in ["../../etc/passwd", "model;rm -rf /", "..\\escape", ""]:
                with self.assertRaises(ValueError) as ctx:
                    ensure_model_downloaded(bad_name, tmp_dir)
                self.assertIn("Invalid model name", str(ctx.exception))

    # -------------------------------------------------------------------------
    # API Input Bounds & Resource Quota Tests
    # -------------------------------------------------------------------------

    def test_request_bounds_prompt_length(self) -> None:
        """Oversized prompts exceeding 4096 characters must be rejected."""
        oversized_prompt = "x" * 5000
        with self.assertRaises(ValidationError):
            GenerateMusicRequest(prompt=oversized_prompt)

    def test_request_bounds_inference_steps(self) -> None:
        """Excessive or invalid inference steps must be rejected."""
        with self.assertRaises(ValidationError):
            GenerateMusicRequest(inference_steps=0)
        with self.assertRaises(ValidationError):
            GenerateMusicRequest(inference_steps=500)

        # Valid step count succeeds
        req = GenerateMusicRequest(inference_steps=50)
        self.assertEqual(50, req.inference_steps)

    def test_request_bounds_batch_size(self) -> None:
        """Batch sizes greater than 8 or less than 1 must be rejected."""
        with self.assertRaises(ValidationError):
            GenerateMusicRequest(batch_size=0)
        with self.assertRaises(ValidationError):
            GenerateMusicRequest(batch_size=16)

        # Valid batch size succeeds
        req = GenerateMusicRequest(batch_size=4)
        self.assertEqual(4, req.batch_size)

    def test_request_bounds_audio_duration(self) -> None:
        """Audio duration exceeding 600 seconds or below -1 must be rejected."""
        with self.assertRaises(ValidationError):
            GenerateMusicRequest(audio_duration=-2.0)
        with self.assertRaises(ValidationError):
            GenerateMusicRequest(audio_duration=1000.0)

        req = GenerateMusicRequest(audio_duration=120.0)
        self.assertEqual(120.0, req.audio_duration)


if __name__ == "__main__":
    unittest.main()
