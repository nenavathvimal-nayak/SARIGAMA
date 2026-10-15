"""Audio-path validation and upload persistence helpers for release-task flow."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import HTTPException
from starlette.datastructures import UploadFile as StarletteUploadFile

ALLOWED_AUDIO_EXTENSIONS: set[str] = {
    ".wav",
    ".mp3",
    ".flac",
    ".ogg",
    ".m4a",
    ".aac",
    ".opus",
    ".wma",
}

DEFAULT_MAX_UPLOAD_SIZE_MB: int = 50


def validate_audio_path(path: Optional[str]) -> Optional[str]:
    """Validate user-supplied audio path and block unsafe filesystem traversal.

    Args:
        path: User-supplied path value from request payload.

    Returns:
        Normalized path string for accepted values, or ``None`` for empty input.

    Raises:
        HTTPException: If absolute paths outside temp, traversal markers, or
            unsupported audio formats are detected.
    """

    if not path:
        return None

    ext = Path(path).suffix.lower()
    if ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio file format: '{ext}'",
        )

    system_temp = os.path.realpath(tempfile.gettempdir())
    requested_path = os.path.realpath(path)
    try:
        is_in_temp = os.path.commonpath([system_temp, requested_path]) == system_temp
    except ValueError:
        is_in_temp = False

    if is_in_temp:
        return requested_path

    if os.path.isabs(path):
        raise HTTPException(status_code=400, detail="absolute audio file paths are not allowed")

    normalized = os.path.normpath(path.replace("\\", "/"))
    parts = normalized.replace("\\", "/").split("/")
    if ".." in parts or ".." in path:
        raise HTTPException(status_code=400, detail="path traversal in audio file paths is not allowed")

    if any(part.startswith(".") for part in parts if part):
        raise HTTPException(status_code=400, detail="Hidden or sensitive files are not permitted as audio paths")

    return path


async def save_upload_to_temp(upload: StarletteUploadFile, *, prefix: str) -> str:
    """Persist uploaded audio file to a temporary location with size and extension limits.

    Args:
        upload: Uploaded file wrapper from Starlette/FastAPI.
        prefix: Filename prefix used for the temporary file.

    Returns:
        Path to the stored temporary file.

    Raises:
        HTTPException: On unsupported extension or oversized payload.
        Exception: Re-raises write errors after cleaning up partial files.
    """

    raw_suffix = Path(upload.filename or "").suffix.lower()
    if not raw_suffix or raw_suffix not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio file extension: '{raw_suffix}'",
        )

    max_mb_str = (
        os.getenv("DHAVLO_MI_MAX_UPLOAD_SIZE_MB")
        or os.getenv("SARIGAMA_MAX_UPLOAD_SIZE_MB")
        or os.getenv("ACESTEP_MAX_UPLOAD_SIZE_MB", str(DEFAULT_MAX_UPLOAD_SIZE_MB))
    )
    try:
        max_mb = int(max_mb_str)
    except ValueError:
        max_mb = DEFAULT_MAX_UPLOAD_SIZE_MB
    max_bytes = max_mb * 1024 * 1024

    fd, path = tempfile.mkstemp(prefix=f"{prefix}_", suffix=raw_suffix)
    try:
        try:
            os.close(fd)
        except OSError:
            try:
                os.remove(path)
            except OSError:
                pass
            raise

        total_bytes = 0
        with open(path, "wb") as file_obj:
            while True:
                chunk = await upload.read(1024 * 1024)
                if not chunk:
                    break
                total_bytes += len(chunk)
                if total_bytes > max_bytes:
                    raise HTTPException(
                        status_code=413,
                        detail=f"Uploaded file exceeds maximum permitted size of {max_mb}MB",
                    )
                file_obj.write(chunk)
    except Exception:
        try:
            os.remove(path)
        except OSError:
            pass
        raise
    finally:
        try:
            await upload.close()
        except Exception:
            pass
    return path
