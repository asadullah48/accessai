"""
WCAG 2.2 contrast mathematics.

Implements the normative relative-luminance and contrast-ratio algorithms from
WCAG 2.2 so that contrast findings are measured from real colour values rather
than asserted. Kept dependency-free and pure so it is trivially testable.

Reference: https://www.w3.org/TR/WCAG22/#dfn-relative-luminance
"""

from __future__ import annotations

from enum import Enum

RGB = tuple[int, int, int]

# WCAG 2.x normatively specifies 0.03928 as the linearisation breakpoint.
# The mathematically exact sRGB breakpoint is 0.04045, but conformance tools
# must reproduce the value the specification actually publishes.
_SRGB_LINEAR_BREAKPOINT = 0.03928

# Luminance coefficients for the sRGB primaries (ITU-R BT.709).
_LUMA_R, _LUMA_G, _LUMA_B = 0.2126, 0.7152, 0.0722

# Additive constant that models ambient flare in the contrast formula.
_FLARE = 0.05


class ConformanceLevel(str, Enum):
    """WCAG conformance level."""

    AA = "AA"
    AAA = "AAA"


class TextSize(str, Enum):
    """
    WCAG text-size class.

    LARGE is >= 18pt, or >= 14pt bold; it carries a relaxed contrast threshold
    because larger glyphs have thicker strokes and remain legible at lower ratios.
    """

    NORMAL = "NORMAL"
    LARGE = "LARGE"


# Success criteria 1.4.3 (AA) and 1.4.6 (AAA) minimum contrast ratios.
CONTRAST_THRESHOLDS = {
    (ConformanceLevel.AA, TextSize.NORMAL): 4.5,
    (ConformanceLevel.AA, TextSize.LARGE): 3.0,
    (ConformanceLevel.AAA, TextSize.NORMAL): 7.0,
    (ConformanceLevel.AAA, TextSize.LARGE): 4.5,
}


def parse_hex_color(value: str) -> RGB:
    """
    Parse a CSS hex colour ('#RGB' or '#RRGGBB') into an 8-bit RGB triple.

    Raises:
        ValueError: if the string is not a 3- or 6-digit hex colour.
    """
    text = value.strip().lstrip("#")
    if len(text) == 3:
        text = "".join(ch * 2 for ch in text)
    if len(text) != 6:
        raise ValueError(f"Invalid hex colour: {value!r} (expected #RGB or #RRGGBB)")
    try:
        return (int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16))
    except ValueError as exc:
        raise ValueError(f"Invalid hex colour: {value!r}") from exc


def _linearize(channel_8bit: int) -> float:
    """Convert one gamma-encoded 8-bit sRGB channel to linear light."""
    c = channel_8bit / 255.0
    if c <= _SRGB_LINEAR_BREAKPOINT:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb: RGB) -> float:
    """
    Relative luminance of an sRGB colour, normalised to 0.0 (black) - 1.0 (white).

    Raises:
        ValueError: if any channel falls outside 0-255.
    """
    if not all(0 <= channel <= 255 for channel in rgb):
        raise ValueError(f"RGB channels must be within 0-255, got {rgb!r}")
    r, g, b = (_linearize(channel) for channel in rgb)
    return _LUMA_R * r + _LUMA_G * g + _LUMA_B * b


def contrast_ratio(foreground: RGB, background: RGB) -> float:
    """
    Contrast ratio between two colours, from 1.0 (identical) to 21.0 (black/white).

    The ratio is symmetric: argument order does not affect the result.
    """
    l1 = relative_luminance(foreground)
    l2 = relative_luminance(background)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + _FLARE) / (darker + _FLARE)


def required_contrast(level: ConformanceLevel, size: TextSize) -> float:
    """Minimum contrast ratio demanded by the given level and text size."""
    return CONTRAST_THRESHOLDS[(level, size)]


def meets_contrast(
    ratio: float,
    level: ConformanceLevel = ConformanceLevel.AAA,
    size: TextSize = TextSize.NORMAL,
) -> bool:
    """Whether a measured ratio satisfies the threshold for the level and size."""
    return ratio >= required_contrast(level, size)
