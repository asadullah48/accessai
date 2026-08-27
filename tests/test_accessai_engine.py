import pytest
from accessai.orchestration.accessai_engine import AccessAIEngine
from accessai.core.models import LiveStreamFrame

def test_accessai_engine_pipeline():
    engine = AccessAIEngine()
    frame = LiveStreamFrame(
        scene_category="Financial Briefing",
        visual_entities=["CEO presenting quarterly profit margin"],
        on_screen_ocr="Net Income Up 32%",
        inter_dialogue_gap_sec=3.8
    )
    window = engine.process_live_frame(frame)
    assert window.audit.is_compliant is True
    assert "Net Income Up 32%" in window.description.description_text
