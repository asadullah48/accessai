import pytest
from accessai.core.compliance_guardrails import ComplianceGuardrails
from accessai.core.models import LiveStreamFrame, AudioDescriptionEvent, SpatialAudioPosition

def test_compliance_guardrail_pass():
    frame = LiveStreamFrame(inter_dialogue_gap_sec=4.0)
    event = AudioDescriptionEvent(
        event_id="E1",
        description_text="Presenter points at revenue slide",
        ssml_markup="<speak>Presenter points at revenue slide</speak>",
        estimated_speech_sec=2.2,
        spatial_position=SpatialAudioPosition.CENTER,
        fits_silence_gap=True
    )
    audit = ComplianceGuardrails.audit_stream_accessibility(frame, event, latency_ms=110.0)
    assert audit.is_compliant is True
    assert audit.dialogue_collision_passed is True
    assert audit.wcag_rule_1_4_3_contrast_ratio >= 7.0
    assert audit.compliance_score > 90.0

def test_compliance_guardrail_collision_detected():
    frame = LiveStreamFrame(inter_dialogue_gap_sec=1.0)
    event = AudioDescriptionEvent(
        event_id="E2",
        description_text="Long description that exceeds available silence gap and collides with voice",
        ssml_markup="<speak>Long description</speak>",
        estimated_speech_sec=3.5,
        spatial_position=SpatialAudioPosition.CENTER,
        fits_silence_gap=False
    )
    audit = ComplianceGuardrails.audit_stream_accessibility(frame, event, latency_ms=110.0)
    assert audit.is_compliant is False
    assert audit.dialogue_collision_passed is False
