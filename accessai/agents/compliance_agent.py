"""ComplianceAgent: audits descriptions against accessibility standards."""

from __future__ import annotations

from accessai.core.compliance_guardrails import ComplianceGuardrails
from accessai.core.models import AccessibilityAuditResult, AudioDescriptionEvent, LiveStreamFrame
from accessai.core.wcag import ConformanceLevel


class ComplianceAgent:
    """
    ComplianceAgent: audits audio descriptions against WCAG 2.2 AAA, Section 508,
    and ADA Title III standards.
    """

    def __init__(self, conformance_level: ConformanceLevel = ConformanceLevel.AAA) -> None:
        self.name = "ComplianceAgent"
        self.version = "1.1.0"
        self.conformance_level = conformance_level

    def audit_accessibility(
        self,
        frame: LiveStreamFrame,
        event: AudioDescriptionEvent,
        latency_ms: float = 95.0,
    ) -> AccessibilityAuditResult:
        """Evaluate one description and return its compliance record."""
        return ComplianceGuardrails.audit_stream_accessibility(
            frame, event, latency_ms=latency_ms, conformance_level=self.conformance_level
        )
