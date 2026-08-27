from accessai.core.models import LiveStreamFrame, AudioDescriptionEvent, AccessibilityAuditResult
from accessai.core.compliance_guardrails import ComplianceGuardrails

class ComplianceAgent:
    """
    ComplianceAgent: Audits audio descriptions against WCAG 2.2 AAA, Section 508,
    and ADA Title III standards.
    """
    def __init__(self):
        self.name = "ComplianceAgent"
        self.version = "1.0.0"

    def audit_accessibility(
        self, frame: LiveStreamFrame, event: AudioDescriptionEvent, latency_ms: float = 95.0
    ) -> AccessibilityAuditResult:
        return ComplianceGuardrails.audit_stream_accessibility(frame, event, latency_ms)
