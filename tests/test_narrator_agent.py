"""NarratorAgent description generation and gap-fitting."""

import pytest

from accessai.agents.narrator_agent import NarratorAgent, build_description_ladder, truncate_to_gap
from accessai.core.audio_synthesizer import estimate_speech_duration
from accessai.core.models import LiveStreamFrame


@pytest.fixture
def agent() -> NarratorAgent:
    return NarratorAgent()


def test_generous_gap_keeps_full_detail(agent):
    frame = LiveStreamFrame(
        visual_entities=["Spacecraft docking with orbital station", "Thrusters firing"],
        on_screen_ocr="Docking Port Velocity 0.2 m/s",
        inter_dialogue_gap_sec=8.0,
    )
    event = agent.describe_scene(frame)
    assert "Spacecraft docking" in event.description_text
    assert "0.2 m/s" in event.description_text
    assert event.prune_level == 0
    assert event.fits_silence_gap is True


def test_narrow_gap_drops_supporting_detail_first(agent):
    frame = LiveStreamFrame(
        visual_entities=["Surgeon holding scalpel", "Heart rate monitor", "Nurse passing swab"],
        on_screen_ocr="Vitals Stable",
        inter_dialogue_gap_sec=1.6,
    )
    event = agent.describe_scene(frame)
    assert "Surgeon holding scalpel" in event.description_text
    assert "Nurse passing swab" not in event.description_text
    assert event.prune_level > 0


def test_primary_subject_survives_aggressive_pruning(agent):
    frame = LiveStreamFrame(
        visual_entities=["Forward sprinting past defender", "Crowd rising"],
        on_screen_ocr="GOAL! 2-1",
        inter_dialogue_gap_sec=0.9,
    )
    event = agent.describe_scene(frame)
    assert "Forward" in event.description_text


@pytest.mark.parametrize("gap", [0.8, 1.0, 1.5, 2.5, 3.5, 6.0])
def test_description_fits_whenever_physically_possible(agent, gap):
    frame = LiveStreamFrame(
        visual_entities=["Presenter gesturing at a very detailed quarterly revenue slide"],
        on_screen_ocr="Q4 Enterprise AI Growth: +142% YoY",
        inter_dialogue_gap_sec=gap,
    )
    event = agent.describe_scene(frame)
    assert event.fits_silence_gap is True
    assert event.estimated_speech_sec <= gap


def test_impossibly_short_gap_reports_failure_rather_than_lying(agent):
    """Below the minimum utterance length nothing can fit; say so."""
    frame = LiveStreamFrame(
        visual_entities=["Presenter"], on_screen_ocr="", inter_dialogue_gap_sec=0.1
    )
    event = agent.describe_scene(frame)
    assert event.fits_silence_gap is False


def test_missing_ocr_produces_no_empty_quotes(agent):
    frame = LiveStreamFrame(
        visual_entities=["Presenter waves"], on_screen_ocr="", inter_dialogue_gap_sec=5.0
    )
    assert "''" not in agent.describe_scene(frame).description_text


def test_ladder_is_ordered_shortest_last():
    frame = LiveStreamFrame(
        visual_entities=["Alpha entity", "Beta entity", "Gamma entity"],
        on_screen_ocr="Some caption",
    )
    ladder = build_description_ladder(frame)
    durations = [estimate_speech_duration(rung) for rung in ladder]
    assert durations == sorted(durations, reverse=True)


def test_ladder_deduplicates_collapsed_rungs():
    frame = LiveStreamFrame(visual_entities=["Only entity"], on_screen_ocr="")
    assert len(build_description_ladder(frame)) == len(set(build_description_ladder(frame)))


def test_ladder_falls_back_to_scene_when_no_entities():
    frame = LiveStreamFrame(
        visual_entities=[], scene_category="Rocket Launch", on_screen_ocr="T-10"
    )
    assert all("Rocket Launch" in rung for rung in build_description_ladder(frame))


def test_truncate_respects_the_sentence_pause_it_adds():
    text = " ".join(["word"] * 100)
    trimmed = truncate_to_gap(text, 2.0)
    assert estimate_speech_duration(trimmed) <= 2.0


def test_truncate_leaves_short_text_untouched():
    assert truncate_to_gap("Short line.", 30.0) == "Short line."
