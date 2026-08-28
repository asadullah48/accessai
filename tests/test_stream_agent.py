"""StreamAgent frame normalisation."""

from accessai.agents.stream_agent import StreamAgent
from accessai.core.models import LiveStreamFrame


def test_frame_fields_are_preserved():
    agent = StreamAgent()
    frame = LiveStreamFrame(
        frame_id="FRM-99",
        scene_category="Surgical Operation",
        visual_entities=["Surgeon holding scalpel", "Heart rate monitor 72 BPM"],
        on_screen_ocr="Patient Vitals Stable",
        inter_dialogue_gap_sec=3.0,
    )
    out = agent.inspect_frame(frame)
    assert out.frame_id == "FRM-99"
    assert len(out.visual_entities) == 2
    assert out.inter_dialogue_gap_sec == 3.0


def test_blank_entities_are_dropped():
    out = StreamAgent().inspect_frame(LiveStreamFrame(visual_entities=["Real entity", "  ", ""]))
    assert out.visual_entities == ["Real entity"]


def test_whitespace_is_trimmed():
    out = StreamAgent().inspect_frame(
        LiveStreamFrame(
            visual_entities=["  Padded entity  "],
            on_screen_ocr="  Caption text  ",
            scene_category="  Keynote  ",
        )
    )
    assert out.visual_entities == ["Padded entity"]
    assert out.on_screen_ocr == "Caption text"
    assert out.scene_category == "Keynote"


def test_salience_order_is_preserved():
    entities = ["Primary subject", "Secondary detail", "Tertiary detail"]
    assert (
        StreamAgent().inspect_frame(LiveStreamFrame(visual_entities=entities)).visual_entities
        == entities
    )


def test_inspection_does_not_mutate_the_input():
    frame = LiveStreamFrame(visual_entities=["  Padded  "])
    StreamAgent().inspect_frame(frame)
    assert frame.visual_entities == ["  Padded  "]
