"""Domain models for the AccessAI real-time accessibility pipeline."""

from __future__ import annotations

import time
from enum import Enum

from pydantic import BaseModel, Field

from accessai.core.wcag import ConformanceLevel, TextSize

# CSS hex colour, in either 3- or 6-digit form.
_HEX_COLOUR = r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$"


class AccessibilityStandard(str, Enum):
    WCAG_2_2_AAA = "WCAG_2_2_AAA"
    SECTION_508 = "SECTION_508"
    ADA_TITLE_III = "ADA_TITLE_III"
    EN_301_549 = "EN_301_549"


class SpatialAudioPosition(str, Enum):
    CENTER = "CENTER"
    LEFT_OFFSCREEN = "LEFT_OFFSCREEN"
    RIGHT_OFFSCREEN = "RIGHT_OFFSCREEN"
    BACKGROUND_AMBIENT = "BACKGROUND_AMBIENT"


class LiveStreamFrame(BaseModel):
    """A single analysed frame of a live stream, with its dialogue timing budget."""

    frame_id: str = Field(default="FRM-8820", min_length=1, max_length=128)
    timestamp_ms: int = Field(default=14200, ge=0)
    scene_category: str = Field(default="Keynote Presentation", max_length=256)
    visual_entities: list[str] = Field(
        default=[
            "Presenter gesturing at slide",
            "Bar chart showing revenue growth",
            "Audience clapping",
        ],
        max_length=32,
        description="Salient on-screen entities, ordered most to least important.",
    )
    on_screen_ocr: str = Field(default="Q4 Enterprise AI Growth: +142% YoY", max_length=2048)

    # Silence budget the description must fit inside to avoid colliding with dialogue.
    inter_dialogue_gap_sec: float = Field(default=3.5, ge=0.0, le=60.0)

    # Whether the player may pause video to create an extended description window
    # (WCAG 2.2 success criterion 1.2.7).
    extended_pause_available: bool = False

    # Caption/overlay colours, measured for contrast criteria 1.4.3 / 1.4.6.
    caption_foreground_hex: str = Field(default="#F2F5F7", pattern=_HEX_COLOUR)
    caption_background_hex: str = Field(default="#0B0F14", pattern=_HEX_COLOUR)
    caption_text_size: TextSize = TextSize.NORMAL


class AudioDescriptionEvent(BaseModel):
    """A synthesized audio-description utterance and its timing characteristics."""

    event_id: str
    description_text: str
    ssml_markup: str
    estimated_speech_sec: float = Field(ge=0.0)
    spatial_position: SpatialAudioPosition = SpatialAudioPosition.CENTER

    # True only when the utterance was measured against a real gap and fits it.
    fits_silence_gap: bool = False

    # How many times the description was shortened to fit the available gap.
    prune_level: int = Field(default=0, ge=0)


class AuditCheck(BaseModel):
    """One evaluated accessibility criterion within an audit."""

    rule_id: str
    title: str
    passed: bool
    observed: str
    required: str
    weight: float = Field(ge=0.0)


class AccessibilityAuditResult(BaseModel):
    """Outcome of auditing one description against the accessibility standards."""

    audit_id: str
    standard: AccessibilityStandard = AccessibilityStandard.WCAG_2_2_AAA
    conformance_level: ConformanceLevel = ConformanceLevel.AAA

    wcag_rule_1_2_5_passed: bool  # Audio Description (Prerecorded)
    wcag_rule_1_2_7_passed: bool  # Extended Audio Description
    wcag_rule_1_4_3_contrast_ratio: float  # Measured ratio; AAA (1.4.6) targets >= 7.0
    contrast_passed: bool
    dialogue_collision_passed: bool
    latency_ms: float = Field(ge=0.0)
    latency_passed: bool

    is_compliant: bool
    compliance_score: float = Field(ge=0.0, le=100.0)
    checks: list[AuditCheck]
    audit_notes: list[str]


class ProcessedStreamWindow(BaseModel):
    """A frame, its generated description, and the resulting compliance audit."""

    window_id: str
    frame: LiveStreamFrame
    description: AudioDescriptionEvent
    audit: AccessibilityAuditResult
    processed_at: float = Field(default_factory=time.time)
