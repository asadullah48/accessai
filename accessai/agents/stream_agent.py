"""StreamAgent: ingests and normalises live stream frames."""

from __future__ import annotations

from accessai.core.models import LiveStreamFrame


class StreamAgent:
    """
    StreamAgent: ingests live video/media stream frames, extracts on-screen OCR,
    identifies visual entities, and calculates inter-dialogue silence gaps.
    """

    def __init__(self) -> None:
        self.name = "StreamAgent"
        self.version = "1.1.0"

    def inspect_frame(self, frame: LiveStreamFrame) -> LiveStreamFrame:
        """
        Normalise a frame for downstream agents.

        Blank entity strings and surrounding whitespace are stripped here so the
        narrator never has to defend against them, and salience order is preserved
        because the narrator treats the first entity as the primary subject.
        """
        cleaned = [entity.strip() for entity in frame.visual_entities if entity.strip()]
        return frame.model_copy(
            update={
                "visual_entities": cleaned,
                "on_screen_ocr": frame.on_screen_ocr.strip(),
                "scene_category": frame.scene_category.strip(),
            }
        )
