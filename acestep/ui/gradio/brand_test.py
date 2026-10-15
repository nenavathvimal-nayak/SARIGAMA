"""Unit tests for DHAVLO MI Gradio brand helpers."""

import base64
import unittest
from unittest.mock import patch

from acestep.ui.gradio.brand import (
    _find_favicon_path,
    _find_logo_path,
    get_brand_favicon_base64,
    get_brand_favicon_head,
    get_brand_logo_base64,
    get_brand_logo_html,
)


class TestBrandHelpers(unittest.TestCase):
    """Test brand logo and favicon resolution and HTML generation."""

    def test_find_logo_path_returns_existing_file(self):
        path = _find_logo_path()
        self.assertIsNotNone(path)
        self.assertTrue(path.endswith(".png"))

    def test_find_favicon_path_returns_existing_file(self):
        path = _find_favicon_path()
        self.assertIsNotNone(path)
        self.assertTrue(path.endswith(".png"))

    def test_get_brand_logo_base64_decodes_valid_png(self):
        get_brand_logo_base64.cache_clear()
        b64 = get_brand_logo_base64()
        self.assertTrue(len(b64) > 100)
        raw_bytes = base64.b64decode(b64)
        # PNG signature check: \x89PNG\r\n\x1a\n
        self.assertEqual(raw_bytes[:8], b"\x89PNG\r\n\x1a\n")

    def test_get_brand_favicon_base64_decodes_valid_png(self):
        get_brand_favicon_base64.cache_clear()
        b64 = get_brand_favicon_base64()
        self.assertTrue(len(b64) > 100)
        raw_bytes = base64.b64decode(b64)
        self.assertEqual(raw_bytes[:8], b"\x89PNG\r\n\x1a\n")

    def test_get_brand_logo_html_contains_img_tag(self):
        get_brand_logo_base64.cache_clear()
        html = get_brand_logo_html()
        self.assertIn("brand-logo-container", html)
        self.assertIn('<img src="data:image/png;base64,', html)
        self.assertIn('alt="DHAVLO MI Logo"', html)
        self.assertIn("border-radius: 50%", html)

    def test_get_brand_favicon_head_contains_link_tag(self):
        get_brand_favicon_base64.cache_clear()
        head = get_brand_favicon_head()
        self.assertIn('<link rel="icon" type="image/png"', head)
        self.assertIn('href="data:image/png;base64,', head)

    @patch("acestep.ui.gradio.brand._find_logo_path", return_value=None)
    def test_missing_logo_path_returns_empty_html(self, _mock_find):
        get_brand_logo_base64.cache_clear()
        self.assertEqual(get_brand_logo_base64(), "")
        self.assertEqual(get_brand_logo_html(), "")

    @patch("acestep.ui.gradio.brand._find_favicon_path", return_value=None)
    def test_missing_favicon_path_returns_empty_head(self, _mock_find):
        get_brand_favicon_base64.cache_clear()
        self.assertEqual(get_brand_favicon_base64(), "")
        self.assertEqual(get_brand_favicon_head(), "")


if __name__ == "__main__":
    unittest.main()
