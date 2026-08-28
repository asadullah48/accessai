"""
Regression tests pinning defects found in the 1.0.0 audit.

Each test here fails against the pre-1.1.0 implementation. The names record what
was wrong so the history stays legible.
"""

import subprocess
import sys
import xml.etree.ElementTree as ET

import pytest

from accessai.agents.narrator_agent import NarratorAgent
from accessai.core.audio_synthesizer import AudioSynthesizer
from accessai.core.models import LiveStreamFrame
from accessai.orchestration.accessai_engine import AccessAIEngine


def test_empty_visual_entities_does_not_raise_index_error():
    """1.0.0 indexed visual_entities[0] unguarded, crashing on an empty list."""
    frame = LiveStreamFrame(
        visual_entities=[], scene_category="Keynote", inter_dialogue_gap_sec=3.0
    )
    event = NarratorAgent().describe_scene(frame)
    assert event.description_text.strip()


def test_blank_only_entities_fall_back_to_scene_context():
    frame = LiveStreamFrame(
        visual_entities=["  ", ""], scene_category="Surgery", inter_dialogue_gap_sec=3.0
    )
    event = NarratorAgent().describe_scene(frame)
    assert "Surgery" in event.description_text


@pytest.mark.parametrize("hostile", ["Tom & Jerry", "<slide 3>", "a & b < c > d", "5 < 6 && 7 > 2"])
def test_ssml_stays_well_formed_xml(hostile):
    """1.0.0 interpolated raw text, emitting unparseable markup on '&' or '<'."""
    event = AudioSynthesizer.generate_ssml(hostile, available_gap_sec=10.0)
    parsed = ET.fromstring(event.ssml_markup)
    assert parsed.tag == "speak"
    assert hostile in "".join(parsed.itertext())


def test_ssml_escapes_do_not_leak_into_description_text():
    """The spoken text must stay human-readable; only the markup is escaped."""
    event = AudioSynthesizer.generate_ssml("Tom & Jerry", available_gap_sec=10.0)
    assert event.description_text == "Tom & Jerry"
    assert "&amp;" in event.ssml_markup


def test_fits_silence_gap_reports_the_truth():
    """1.0.0 hardcoded fits_silence_gap=True regardless of the gap."""
    overrun = AudioSynthesizer.generate_ssml(" ".join(["word"] * 60), available_gap_sec=1.0)
    assert overrun.estimated_speech_sec > 1.0
    assert overrun.fits_silence_gap is False


def test_unmeasured_event_does_not_claim_to_fit():
    assert AudioSynthesizer.generate_ssml("Anything").fits_silence_gap is False


def test_event_id_is_stable_across_processes():
    """1.0.0 used builtin hash(), which PYTHONHASHSEED salts per process."""
    script = (
        "from accessai.core.audio_synthesizer import AudioSynthesizer;"
        "print(AudioSynthesizer.generate_ssml('Presenter points at slide').event_id)"
    )
    ids = {
        subprocess.run(
            [sys.executable, "-c", script], capture_output=True, text=True, check=True
        ).stdout.strip()
        for _ in range(3)
    }
    assert len(ids) == 1, f"event_id differed across processes: {ids}"


def test_latency_is_reported_as_measured_not_floored():
    """1.0.0 applied max(45.0, elapsed), inflating a sub-millisecond pipeline."""
    window = AccessAIEngine().process_live_frame(LiveStreamFrame())
    assert window.audit.latency_ms < 45.0, "latency still appears to be floored"
    assert window.audit.latency_ms > 0.0


def test_negative_dialogue_gap_is_rejected():
    """1.0.0 accepted a negative gap and still produced an audit record."""
    with pytest.raises(ValueError):
        LiveStreamFrame(inter_dialogue_gap_sec=-99.0)


def test_compliance_score_is_graded_not_binary():
    """1.0.0 emitted only 99.2 or 65.0; the score must track how much failed."""
    engine = AccessAIEngine()
    scores = {
        engine.process_live_frame(frame).audit.compliance_score
        for frame in (
            LiveStreamFrame(inter_dialogue_gap_sec=6.0),
            LiveStreamFrame(inter_dialogue_gap_sec=0.2),
            LiveStreamFrame(inter_dialogue_gap_sec=0.2, extended_pause_available=True),
            LiveStreamFrame(caption_foreground_hex="#777777", caption_background_hex="#6E6E6E"),
        )
    }
    assert len(scores) >= 3, f"score is not responsive to failure mix: {scores}"
    assert scores != {99.2, 65.0}


def test_contrast_is_measured_from_frame_colours():
    """1.0.0 hardcoded contrast_ratio = 8.4 for every frame."""
    engine = AccessAIEngine()
    high = engine.process_live_frame(
        LiveStreamFrame(caption_foreground_hex="#FFFFFF", caption_background_hex="#000000")
    ).audit
    low = engine.process_live_frame(
        LiveStreamFrame(caption_foreground_hex="#777777", caption_background_hex="#6E6E6E")
    ).audit
    assert high.wcag_rule_1_4_3_contrast_ratio == pytest.approx(21.0)
    assert low.wcag_rule_1_4_3_contrast_ratio < 2.0
    assert high.contrast_passed and not low.contrast_passed


def test_wcag_rules_can_actually_fail():
    """1.0.0 set rule_1_2_5 and rule_1_2_7 to True unconditionally."""
    audit = (
        AccessAIEngine()
        .process_live_frame(
            LiveStreamFrame(inter_dialogue_gap_sec=0.2, extended_pause_available=False)
        )
        .audit
    )
    assert audit.wcag_rule_1_2_7_passed is False
