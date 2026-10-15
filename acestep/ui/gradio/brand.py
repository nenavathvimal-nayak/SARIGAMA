"""DHAVLO MI branding utilities for Gradio interface.

Provides helpers to load and format the official 3D acoustic wave brand emblem
and favicon for browser presentation.
"""

from functools import lru_cache
import base64
import os
from typing import Optional


def _find_logo_path() -> Optional[str]:
    """Find the best available logo image path in the workspace."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    candidates = [
        os.path.join(base_dir, "docs", "public", "logo-256.png"),
        os.path.join(base_dir, "docs", "public", "logo.png"),
        os.path.join(base_dir, "assets", "dhavlo_mi_icon.png"),
        os.path.join(base_dir, "assets", "dhavlo_mi_logo.png"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


def _find_favicon_path() -> Optional[str]:
    """Find the best available favicon image path in the workspace."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    candidates = [
        os.path.join(base_dir, "docs", "public", "favicon.png"),
        os.path.join(base_dir, "docs", "public", "favicon-64.png"),
        os.path.join(base_dir, "docs", "public", "favicon-32.png"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return _find_logo_path()


@lru_cache(maxsize=1)
def get_brand_logo_base64() -> str:
    """Read and cache the official logo image as base64 string.

    Returns:
        Base64-encoded string of the PNG image, or empty string if not found.
    """
    logo_path = _find_logo_path()
    if not logo_path:
        return ""
    try:
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode("ascii")
    except OSError:
        return ""


@lru_cache(maxsize=1)
def get_brand_favicon_base64() -> str:
    """Read and cache the brand favicon as base64 string.

    Returns:
        Base64-encoded string of the favicon PNG, or empty string if not found.
    """
    favicon_path = _find_favicon_path()
    if not favicon_path:
        return ""
    try:
        with open(favicon_path, "rb") as f:
            return base64.b64encode(f.read()).decode("ascii")
    except OSError:
        return ""


def get_brand_logo_html() -> str:
    """Generate HTML snippet to display the official brand logo.

    Returns:
        HTML snippet with circular badge or empty string if asset unavailable.
    """
    b64 = get_brand_logo_base64()
    if not b64:
        return ""
    return (
        '<div class="brand-logo-container" style="text-align: center; margin-bottom: 0.75rem;">'
        f'<img src="data:image/png;base64,{b64}" alt="DHAVLO MI Logo" '
        'style="width: 88px; height: 88px; border-radius: 50%; '
        'box-shadow: 0 4px 20px rgba(0,0,0,0.25); display: inline-block; object-fit: contain;" />'
        "</div>"
    )


def get_brand_favicon_head() -> str:
    """Generate HTML head snippet setting the page favicon.

    Returns:
        HTML snippet with favicon link tag or empty string if asset unavailable.
    """
    b64 = get_brand_favicon_base64()
    if not b64:
        return ""
    return f'<link rel="icon" type="image/png" href="data:image/png;base64,{b64}">\n'
