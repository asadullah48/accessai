import pytest
from accessai.core.audio_synthesizer import AudioSynthesizer
from accessai.core.models import SpatialAudioPosition

def test_audio_synthesizer_ssml():
    text = "The engineer initiates the neural compile sequence."
    event = AudioSynthesizer.generate_ssml(text, SpatialAudioPosition.CENTER)
    assert "<speak>" in event.ssml_markup
    assert "<prosody" in event.ssml_markup
    assert event.estimated_speech_sec >= 1.0
