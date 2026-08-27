import pytest
from accessai.agents.compliance_agent import ComplianceAgent
from accessai.core.models import LiveStreamFrame, AudioDescriptionEvent, SpatialAudioPosition

def test_compliance_agent_audit():
    agent = ComplianceAgent()
    frame = LiveStreamFrame(inter_dialogue_gap_sec=3.0)
    event = AudioDescriptionEvent(
        event_id="E-AUD",
        description_text="Actor walks onto stage.",
        ssml_markup="<speak>Actor walks onto stage.</speak>",
        estimated_speech_sec=1.5,
        spatial_position=SpatialAudioPosition.CENTER
    )
    audit = agent.audit_accessibility(frame, event, latency_ms=85.0)
    assert audit.is_compliant is True
    assert audit.latency_ms < 200.0
