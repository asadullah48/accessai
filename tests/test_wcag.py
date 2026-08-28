"""WCAG 2.2 contrast mathematics."""

import pytest

from accessai.core.wcag import (
    ConformanceLevel,
    TextSize,
    contrast_ratio,
    meets_contrast,
    parse_hex_color,
    relative_luminance,
    required_contrast,
)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


def test_luminance_endpoints():
    assert relative_luminance(BLACK) == pytest.approx(0.0)
    assert relative_luminance(WHITE) == pytest.approx(1.0)


def test_maximum_contrast_is_21_to_1():
    assert contrast_ratio(BLACK, WHITE) == pytest.approx(21.0)


def test_identical_colours_have_no_contrast():
    assert contrast_ratio(WHITE, WHITE) == pytest.approx(1.0)


def test_contrast_is_symmetric():
    assert contrast_ratio(BLACK, WHITE) == pytest.approx(contrast_ratio(WHITE, BLACK))


@pytest.mark.parametrize(
    "hex_colour, expected",
    [("#767676", 4.54), ("#595959", 7.0)],
)
def test_canonical_boundary_greys_on_white(hex_colour, expected):
    """#767676 is the published AA boundary on white; #595959 the AAA boundary."""
    assert contrast_ratio(parse_hex_color(hex_colour), WHITE) == pytest.approx(expected, abs=0.01)


@pytest.mark.parametrize("shorthand, full", [("#0f8", "#00ff88"), ("#ABC", "#aabbcc")])
def test_shorthand_hex_expands(shorthand, full):
    assert parse_hex_color(shorthand) == parse_hex_color(full)


@pytest.mark.parametrize("bad", ["#12345", "nope", "", "#GGGGGG"])
def test_invalid_hex_rejected(bad):
    with pytest.raises(ValueError):
        parse_hex_color(bad)


def test_out_of_range_channel_rejected():
    with pytest.raises(ValueError):
        relative_luminance((256, 0, 0))


def test_aaa_demands_more_than_aa():
    aa = required_contrast(ConformanceLevel.AA, TextSize.NORMAL)
    aaa = required_contrast(ConformanceLevel.AAA, TextSize.NORMAL)
    assert aaa > aa


def test_large_text_threshold_is_relaxed():
    normal = required_contrast(ConformanceLevel.AAA, TextSize.NORMAL)
    large = required_contrast(ConformanceLevel.AAA, TextSize.LARGE)
    assert large < normal


def test_ratio_between_thresholds_passes_aa_but_fails_aaa():
    ratio = contrast_ratio(parse_hex_color("#767676"), WHITE)
    assert meets_contrast(ratio, ConformanceLevel.AA, TextSize.NORMAL)
    assert not meets_contrast(ratio, ConformanceLevel.AAA, TextSize.NORMAL)
