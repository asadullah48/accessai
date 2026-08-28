"""ComplianceAgent delegation and configuration."""

from accessai.agents.compliance_agent import ComplianceAgent
from accessai.core.models import AudioDescriptionEvent, LiveStreamFrame, SpatialAudioPosition
from accessai.core.wcag import ConformanceLevel


def make_event(seconds=1.5):
    return AudioDescriptionEvent(
        event_id="E-AUD",
        description_text="Actor walks onto stage.",
        ssml_markup="<speak>Actor walks onto stage.</speak>",
        estimated_speech_sec=seconds,
        spatial_position=SpatialAudioPosition.CENTER,
    )


def test_agent_audits_a_compliant_frame():
    audit = ComplianceAgent().audit_accessibility(
        LiveStreamFrame(inter_dialogue_gap_sec=3.0), make_event(), latency_ms=85.0
    )
    assert audit.is_compliant is True
    assert audit.latency_ms < 200.0


def test_agent_reports_a_collision():
    audit = ComplianceAgent().audit_accessibility(
        LiveStreamFrame(inter_dialogue_gap_sec=1.0), make_event(seconds=4.0), latency_ms=85.0
    )
    assert audit.is_compliant is False
    assert audit.dialogue_collision_passed is False


def test_configured_conformance_level_is_applied():
    frame = LiveStreamFrame(
        inter_dialogue_gap_sec=3.0,
        caption_foreground_hex="#767676",
        caption_background_hex="#FFFFFF",
    )
    aa = ComplianceAgent(ConformanceLevel.AA).audit_accessibility(
        frame, make_event(), latency_ms=50.0
    )
    aaa = ComplianceAgent(ConformanceLevel.AAA).audit_accessibility(
        frame, make_event(), latency_ms=50.0
    )
    assert aa.contrast_passed is True
    assert aaa.contrast_passed is False
    assert aa.conformance_level is ConformanceLevel.AA
