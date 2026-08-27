import pytest
from accessai.agents.stream_agent import StreamAgent
from accessai.core.models import LiveStreamFrame

def test_stream_agent_inspect():
    agent = StreamAgent()
    frame = LiveStreamFrame(
        frame_id="FRM-99",
        scene_category="Surgical Operation",
        visual_entities=["Surgeon holding scalpel", "Heart rate monitor 72 BPM"],
        on_screen_ocr="Patient Vitals Stable",
        inter_dialogue_gap_sec=3.0
    )
    out = agent.inspect_frame(frame)
    assert out.frame_id == "FRM-99"
    assert len(out.visual_entities) == 2
