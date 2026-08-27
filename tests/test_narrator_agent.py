import pytest
from accessai.agents.narrator_agent import NarratorAgent
from accessai.core.models import LiveStreamFrame

def test_narrator_agent_description():
    agent = NarratorAgent()
    frame = LiveStreamFrame(
        visual_entities=["Spacecraft docking with orbital station"],
        on_screen_ocr="Docking Port Velocity 0.2 m/s",
        inter_dialogue_gap_sec=4.0
    )
    event = agent.describe_scene(frame)
    assert "Spacecraft docking" in event.description_text
    assert "0.2 m/s" in event.description_text
    assert event.estimated_speech_sec <= frame.inter_dialogue_gap_sec
