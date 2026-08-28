"""SSML synthesis and speech-duration estimation."""

import xml.etree.ElementTree as ET

import pytest

from accessai.core.audio_synthesizer import (
    MIN_UTTERANCE_SEC,
    SENTENCE_PAUSE_SEC,
    SPEECH_RATE_WORDS_PER_SEC,
    AudioSynthesizer,
    estimate_speech_duration,
    stable_event_id,
)
from accessai.core.models import SpatialAudioPosition


def test_ssml_carries_prosody_and_emphasis():
    event = AudioSynthesizer.generate_ssml(
        "The engineer starts the sequence.", available_gap_sec=5.0
    )
    root = ET.fromstring(event.ssml_markup)
    assert root.tag == "speak"
    assert root.find("prosody") is not None
    assert root.find("prosody/emphasis") is not None


def test_duration_scales_with_word_count():
    short = estimate_speech_duration("one two three four")
    long = estimate_speech_duration(" ".join(["word"] * 40))
    assert long > short


def test_duration_accounts_for_sentence_pauses():
    words = "alpha bravo charlie delta echo foxtrot"
    without = estimate_speech_duration(words)
    with_pauses = estimate_speech_duration("alpha bravo charlie. delta echo foxtrot.")
    assert with_pauses == pytest.approx(without + 2 * SENTENCE_PAUSE_SEC, abs=0.02)


@pytest.mark.parametrize("blank", ["", "   ", "\n\t"])
def test_blank_text_gets_minimum_utterance(blank):
    assert estimate_speech_duration(blank) == MIN_UTTERANCE_SEC


def test_duration_never_below_minimum():
    assert estimate_speech_duration("Hi") >= MIN_UTTERANCE_SEC


def test_speech_rate_constant_is_applied():
    text = " ".join(["word"] * 38)
    assert estimate_speech_duration(text) == pytest.approx(38 / SPEECH_RATE_WORDS_PER_SEC, abs=0.01)


@pytest.mark.parametrize("position", list(SpatialAudioPosition))
def test_every_spatial_position_synthesizes(position):
    event = AudioSynthesizer.generate_ssml(
        "Door opens to the side.", position, available_gap_sec=5.0
    )
    assert event.spatial_position is position
    assert ET.fromstring(event.ssml_markup) is not None


def test_spatial_position_changes_event_identity():
    left = AudioSynthesizer.generate_ssml("Same text", SpatialAudioPosition.LEFT_OFFSCREEN)
    right = AudioSynthesizer.generate_ssml("Same text", SpatialAudioPosition.RIGHT_OFFSCREEN)
    assert left.event_id != right.event_id


def test_identical_input_yields_identical_id():
    a = AudioSynthesizer.generate_ssml("Presenter waves")
    b = AudioSynthesizer.generate_ssml("Presenter waves")
    assert a.event_id == b.event_id


def test_different_text_yields_different_id():
    a = AudioSynthesizer.generate_ssml("Presenter waves")
    b = AudioSynthesizer.generate_ssml("Presenter bows")
    assert a.event_id != b.event_id


def test_stable_event_id_is_prefixed_and_deterministic():
    assert stable_event_id("EVT", "payload") == stable_event_id("EVT", "payload")
    assert stable_event_id("EVT", "payload").startswith("EVT-")


def test_fit_boundary_is_inclusive():
    """A description exactly filling the gap is not a collision."""
    text = " ".join(["word"] * 19)  # 19 / 3.8 == 5.0s exactly, no sentence pause
    duration = estimate_speech_duration(text)
    event = AudioSynthesizer.generate_ssml(text, available_gap_sec=duration)
    assert event.fits_silence_gap is True
