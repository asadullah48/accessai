"""Compliance evaluation: every criterion must be able to fail."""

import pytest

from accessai.core.compliance_guardrails import (
    CHECK_WEIGHTS,
    LATENCY_BUDGET_MS,
    ComplianceGuardrails,
)
from accessai.core.models import AudioDescriptionEvent, LiveStreamFrame, SpatialAudioPosition
from accessai.core.wcag import ConformanceLevel, TextSize


def make_event(text="Presenter points at the revenue slide", seconds=2.2, fits=True):
    return AudioDescriptionEvent(
        event_id="E-TEST",
        description_text=text,
        ssml_markup=f"<speak>{text}</speak>",
        estimated_speech_sec=seconds,
        spatial_position=SpatialAudioPosition.CENTER,
        fits_silence_gap=fits,
    )


def audit(frame=None, event=None, latency_ms=110.0, level=ConformanceLevel.AAA):
    return ComplianceGuardrails.audit_stream_accessibility(
        frame or LiveStreamFrame(inter_dialogue_gap_sec=4.0),
        event or make_event(),
        latency_ms=latency_ms,
        conformance_level=level,
    )


def check(result, rule_id):
    return next(c for c in result.checks if c.rule_id == rule_id)


def test_nominal_frame_is_fully_compliant():
    result = audit()
    assert result.is_compliant is True
    assert result.compliance_score == 100.0
    assert all(c.passed for c in result.checks)


def test_collision_detected_when_speech_exceeds_gap():
    result = audit(LiveStreamFrame(inter_dialogue_gap_sec=1.0), make_event(seconds=3.5, fits=False))
    assert result.dialogue_collision_passed is False
    assert result.is_compliant is False


def test_extended_pause_rescues_rule_1_2_7_but_not_the_collision():
    frame = LiveStreamFrame(inter_dialogue_gap_sec=1.0, extended_pause_available=True)
    result = audit(frame, make_event(seconds=3.5, fits=False))
    assert result.wcag_rule_1_2_7_passed is True
    assert result.dialogue_collision_passed is False


def test_rule_1_2_7_not_engaged_when_description_fits():
    result = audit()
    assert result.wcag_rule_1_2_7_passed is True
    assert "no extension required" in check(result, "wcag-1.2.7").observed


def test_empty_description_fails_rule_1_2_5():
    result = audit(event=make_event(text="   ", seconds=0.5))
    assert result.wcag_rule_1_2_5_passed is False
    assert result.is_compliant is False


def test_low_contrast_captions_fail():
    frame = LiveStreamFrame(
        inter_dialogue_gap_sec=4.0,
        caption_foreground_hex="#777777",
        caption_background_hex="#6E6E6E",
    )
    result = audit(frame)
    assert result.contrast_passed is False
    assert result.wcag_rule_1_4_3_contrast_ratio < 2.0


def test_large_text_passes_at_a_ratio_normal_text_would_fail():
    colours = {"caption_foreground_hex": "#767676", "caption_background_hex": "#FFFFFF"}
    normal = audit(
        LiveStreamFrame(inter_dialogue_gap_sec=4.0, caption_text_size=TextSize.NORMAL, **colours)
    )
    large = audit(
        LiveStreamFrame(inter_dialogue_gap_sec=4.0, caption_text_size=TextSize.LARGE, **colours)
    )
    assert normal.contrast_passed is False
    assert large.contrast_passed is True


def test_aa_conformance_is_more_permissive_than_aaa():
    frame = LiveStreamFrame(
        inter_dialogue_gap_sec=4.0,
        caption_foreground_hex="#767676",
        caption_background_hex="#FFFFFF",
    )
    assert audit(frame, level=ConformanceLevel.AA).contrast_passed is True
    assert audit(frame, level=ConformanceLevel.AAA).contrast_passed is False


@pytest.mark.parametrize(
    "latency, expected", [(0.5, True), (199.9, True), (200.0, True), (200.1, False)]
)
def test_latency_budget_boundary(latency, expected):
    result = audit(latency_ms=latency)
    assert result.latency_passed is expected
    assert LATENCY_BUDGET_MS == 200.0


def test_score_reflects_the_weight_of_what_failed():
    passing = audit()
    over_budget = audit(latency_ms=500.0)
    expected_loss = CHECK_WEIGHTS["latency"]
    assert passing.compliance_score - over_budget.compliance_score == pytest.approx(
        expected_loss, abs=0.1
    )


def test_more_failures_score_lower():
    one = audit(latency_ms=500.0).compliance_score
    two = audit(
        LiveStreamFrame(
            inter_dialogue_gap_sec=4.0,
            caption_foreground_hex="#777777",
            caption_background_hex="#6E6E6E",
        ),
        latency_ms=500.0,
    ).compliance_score
    assert two < one


def test_weights_sum_to_one_hundred():
    assert sum(CHECK_WEIGHTS.values()) == pytest.approx(100.0)


def test_every_check_is_reported_with_observed_and_required():
    result = audit()
    assert {c.rule_id for c in result.checks} == set(CHECK_WEIGHTS)
    assert all(c.observed and c.required for c in result.checks)


def test_notes_mirror_the_checks():
    result = audit(latency_ms=500.0)
    assert len(result.audit_notes) == len(result.checks)
    assert any(note.startswith("FAIL") for note in result.audit_notes)


def test_audit_id_is_deterministic():
    assert audit().audit_id == audit().audit_id
