"""End-to-end pipeline behaviour."""

import pytest

from accessai.core.models import LiveStreamFrame
from accessai.orchestration.accessai_engine import AccessAIEngine


@pytest.fixture
def engine() -> AccessAIEngine:
    return AccessAIEngine()


def test_pipeline_produces_a_compliant_window(engine):
    frame = LiveStreamFrame(
        scene_category="Financial Briefing",
        visual_entities=["CEO presenting quarterly profit margin"],
        on_screen_ocr="Net Income Up 32%",
        inter_dialogue_gap_sec=3.8,
    )
    window = engine.process_live_frame(frame)
    assert window.audit.is_compliant is True
    assert "Net Income Up 32%" in window.description.description_text


def test_window_stitches_frame_description_and_audit(engine, nominal_frame):
    window = engine.process_live_frame(nominal_frame)
    assert window.frame.frame_id == nominal_frame.frame_id
    assert window.description.event_id
    assert window.audit.audit_id
    assert window.processed_at > 0


def test_pipeline_is_deterministic_for_identical_frames(engine, nominal_frame):
    first = engine.process_live_frame(nominal_frame)
    second = engine.process_live_frame(nominal_frame)
    assert first.window_id == second.window_id
    assert first.description.description_text == second.description.description_text


def test_distinct_frames_yield_distinct_windows(engine):
    a = engine.process_live_frame(LiveStreamFrame(frame_id="FRM-A"))
    b = engine.process_live_frame(LiveStreamFrame(frame_id="FRM-B"))
    assert a.window_id != b.window_id


def test_audit_measures_the_description_the_pipeline_produced(engine):
    """The audited duration must be the pruned one, not the pre-prune estimate."""
    window = engine.process_live_frame(
        LiveStreamFrame(
            visual_entities=["Alpha subject", "Beta detail", "Gamma detail"],
            on_screen_ocr="Caption",
            inter_dialogue_gap_sec=1.6,
        )
    )
    collision = next(c for c in window.audit.checks if c.rule_id == "dialogue-collision")
    assert f"{window.description.estimated_speech_sec:.2f}s" in collision.observed


def test_pipeline_survives_a_frame_with_no_entities(engine):
    window = engine.process_live_frame(
        LiveStreamFrame(
            visual_entities=[], scene_category="Rocket Launch", inter_dialogue_gap_sec=3.0
        )
    )
    assert "Rocket Launch" in window.description.description_text
    assert window.audit.wcag_rule_1_2_5_passed is True


def test_non_compliant_frame_is_logged(engine, caplog):
    import logging

    caplog.set_level(logging.WARNING, logger="accessai.orchestration.accessai_engine")
    engine.process_live_frame(LiveStreamFrame(inter_dialogue_gap_sec=0.2))
    assert any("failed accessibility audit" in record.message for record in caplog.records)
