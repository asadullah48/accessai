from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import time

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
    frame_id: str = "FRM-8820"
    timestamp_ms: int = 14200
    scene_category: str = "Keynote Presentation"
    visual_entities: List[str] = ["Presenter gesturing at slide", "Bar chart showing revenue growth", "Audience clapping"]
    on_screen_ocr: str = "Q4 Enterprise AI Growth: +142% YoY"
    inter_dialogue_gap_sec: float = 3.5

class AudioDescriptionEvent(BaseModel):
    event_id: str
    description_text: str
    ssml_markup: str
    estimated_speech_sec: float
    spatial_position: SpatialAudioPosition = SpatialAudioPosition.CENTER
    fits_silence_gap: bool = True

class AccessibilityAuditResult(BaseModel):
    audit_id: str
    standard: AccessibilityStandard = AccessibilityStandard.WCAG_2_2_AAA
    wcag_rule_1_2_5_passed: bool # Audio Description (Prerecorded)
    wcag_rule_1_2_7_passed: bool # Extended Audio Description
    wcag_rule_1_4_3_contrast_ratio: float # Target >= 7.0 for AAA
    dialogue_collision_passed: bool
    latency_ms: float
    is_compliant: bool
    compliance_score: float # 0.0 - 100.0
    audit_notes: List[str]

class ProcessedStreamWindow(BaseModel):
    window_id: str
    frame: LiveStreamFrame
    description: AudioDescriptionEvent
    audit: AccessibilityAuditResult
    processed_at: float = Field(default_factory=time.time)
