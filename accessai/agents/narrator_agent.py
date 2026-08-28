"""NarratorAgent: turns an analysed frame into a gap-fitted audio description."""

from __future__ import annotations

from accessai.core.audio_synthesizer import (
    SENTENCE_PAUSE_SEC,
    SPEECH_RATE_WORDS_PER_SEC,
    AudioSynthesizer,
    estimate_speech_duration,
)
from accessai.core.models import AudioDescriptionEvent, LiveStreamFrame, SpatialAudioPosition


def _quote(text: str) -> str:
    """Render on-screen text as a spoken quotation, or nothing when absent."""
    stripped = text.strip()
    return f" '{stripped}'." if stripped else ""


def build_description_ladder(frame: LiveStreamFrame) -> list[str]:
    """
    Candidate descriptions ordered from most to least detailed.

    Each rung drops the least essential information first: supporting entities go
    before the on-screen text, and the on-screen text goes before the primary
    subject. The primary subject is never dropped, because a description that
    names nothing is worse than a terse one.
    """
    entities = [entity.strip() for entity in frame.visual_entities if entity.strip()]
    ocr = _quote(frame.on_screen_ocr)

    if not entities:
        # No visual entities detected: fall back to scene context so the listener
        # still receives orientation rather than silence.
        scene = frame.scene_category.strip() or "Scene change"
        return [f"{scene}.{ocr}", f"{scene}."]

    primary = entities[0]
    ladder = []
    if len(entities) > 1:
        ladder.append(f"On screen: {', '.join(entities)}.{ocr}")
    ladder.append(f"{primary}.{ocr}")
    ladder.append(f"{primary}.")
    # De-duplicate while preserving order (a single entity with no OCR collapses).
    return list(dict.fromkeys(ladder))


def truncate_to_gap(text: str, gap_sec: float) -> str:
    """
    Hard-trim a description to the word budget a silence gap can carry.

    The trimmed text ends in a full stop, which costs a sentence pause, so that
    pause is deducted from the budget before solving for the word count -
    otherwise the trim reintroduces the overrun it was meant to remove.
    """
    speakable_sec = gap_sec - SENTENCE_PAUSE_SEC
    budget = max(1, int(speakable_sec * SPEECH_RATE_WORDS_PER_SEC))
    words = text.split()
    if len(words) <= budget:
        return text
    return " ".join(words[:budget]).rstrip(",.") + "."


class NarratorAgent:
    """
    NarratorAgent: synthesizes concise audio descriptions fitted into the
    available silence gap without colliding with dialogue.
    """

    def __init__(self) -> None:
        self.name = "NarratorAgent"
        self.version = "1.1.0"

    def describe_scene(
        self,
        frame: LiveStreamFrame,
        position: SpatialAudioPosition = SpatialAudioPosition.CENTER,
    ) -> AudioDescriptionEvent:
        """
        Produce the most detailed description that still fits the dialogue gap.

        Walks the degradation ladder and returns the first rung that fits. If even
        the shortest rung overruns, the text is hard-trimmed to the word budget;
        the returned event reports honestly whether it ultimately fits.
        """
        gap = frame.inter_dialogue_gap_sec
        ladder = build_description_ladder(frame)

        for level, candidate in enumerate(ladder):
            if estimate_speech_duration(candidate) <= gap:
                return AudioSynthesizer.generate_ssml(
                    candidate, position, available_gap_sec=gap, prune_level=level
                )

        # Nothing on the ladder fits. Trim the shortest rung to the word budget.
        # A gap below the minimum utterance length cannot be satisfied at all, and
        # the event will correctly report fits_silence_gap=False.
        trimmed = truncate_to_gap(ladder[-1], gap)
        return AudioSynthesizer.generate_ssml(
            trimmed, position, available_gap_sec=gap, prune_level=len(ladder)
        )
