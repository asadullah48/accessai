"""SSML synthesis and speech-duration estimation for audio descriptions."""

from __future__ import annotations

import hashlib
import re
from xml.sax.saxutils import escape

from accessai.core.models import AudioDescriptionEvent, SpatialAudioPosition

# Professional audio-description delivery rate. Description tracks are read
# faster than conversational speech because they must fit between lines of dialogue.
SPEECH_RATE_WORDS_PER_SEC = 3.8

# Natural pause a synthesizer inserts at each sentence boundary.
SENTENCE_PAUSE_SEC = 0.30

# Even a single word occupies a minimum slot once onset and decay are included.
MIN_UTTERANCE_SEC = 0.5

# Prosody applied to description tracks so they are distinguishable from dialogue.
_PROSODY_RATE = "110%"
_PROSODY_PITCH = "+2st"

_SENTENCE_BOUNDARY = re.compile(r"[.!?]+(?:\s|$)")

# Spatial position -> stereo pan, giving listeners directional orientation.
_PAN_BY_POSITION = {
    SpatialAudioPosition.CENTER: "0",
    SpatialAudioPosition.LEFT_OFFSCREEN: "-0.7",
    SpatialAudioPosition.RIGHT_OFFSCREEN: "0.7",
    SpatialAudioPosition.BACKGROUND_AMBIENT: "0",
}


def stable_event_id(prefix: str, payload: str) -> str:
    """
    Deterministic identifier derived from content.

    Uses blake2b rather than the builtin hash(), whose string ordering is salted
    per process by PYTHONHASHSEED and therefore differs across restarts and
    replicas.
    """
    digest = hashlib.blake2b(payload.encode("utf-8"), digest_size=4).hexdigest()
    return f"{prefix}-{digest.upper()}"


def estimate_speech_duration(text: str) -> float:
    """
    Estimated spoken duration in seconds, including sentence-boundary pauses.

    Returns MIN_UTTERANCE_SEC for empty or whitespace-only input.
    """
    words = text.split()
    if not words:
        return MIN_UTTERANCE_SEC
    spoken = len(words) / SPEECH_RATE_WORDS_PER_SEC
    pauses = len(_SENTENCE_BOUNDARY.findall(text)) * SENTENCE_PAUSE_SEC
    return max(MIN_UTTERANCE_SEC, round(spoken + pauses, 2))


class AudioSynthesizer:
    """Formats descriptions into SSML markup and measures their speech duration."""

    @staticmethod
    def generate_ssml(
        text: str,
        position: SpatialAudioPosition = SpatialAudioPosition.CENTER,
        available_gap_sec: float | None = None,
        prune_level: int = 0,
    ) -> AudioDescriptionEvent:
        """
        Build an SSML utterance for `text`.

        Description text originates from OCR and scene analysis, so it is escaped
        before interpolation; unescaped '&' or '<' would otherwise emit markup a
        speech engine cannot parse.

        Args:
            available_gap_sec: Silence budget to measure against. When None, the
                event is marked as not fitting, since nothing was measured.
        """
        duration = estimate_speech_duration(text)
        safe_text = escape(text)
        pan = _PAN_BY_POSITION[position]

        ssml = (
            f"<speak>\n"
            f'  <prosody rate="{_PROSODY_RATE}" pitch="{_PROSODY_PITCH}">\n'
            f'    <emphasis level="moderate">{safe_text}</emphasis>\n'
            f"  </prosody>\n"
            f"</speak>"
        )

        fits = available_gap_sec is not None and duration <= available_gap_sec

        return AudioDescriptionEvent(
            event_id=stable_event_id("EVT", f"{text}|{position.value}|{pan}"),
            description_text=text,
            ssml_markup=ssml,
            estimated_speech_sec=duration,
            spatial_position=position,
            fits_silence_gap=fits,
            prune_level=prune_level,
        )
