"""Coordination of the real-time stream accessibility loop."""

from __future__ import annotations

import logging
import time

from accessai.agents.compliance_agent import ComplianceAgent
from accessai.agents.narrator_agent import NarratorAgent
from accessai.agents.stream_agent import StreamAgent
from accessai.core.audio_synthesizer import stable_event_id
from accessai.core.models import LiveStreamFrame, ProcessedStreamWindow

logger = logging.getLogger(__name__)


class AccessAIEngine:
    """AccessAIEngine: coordinates the real-time stream accessibility loop."""

    def __init__(self) -> None:
        self.stream_agent = StreamAgent()
        self.narrator_agent = NarratorAgent()
        self.compliance_agent = ComplianceAgent()

    def process_live_frame(self, frame: LiveStreamFrame) -> ProcessedStreamWindow:
        """
        Run one frame through analysis, narration and audit.

        Latency is measured with perf_counter (monotonic, unaffected by clock
        adjustments) and reported exactly as measured - a compliance record that
        rounds its own timings toward the budget is not evidence of anything.
        """
        started = time.perf_counter()

        inspected = self.stream_agent.inspect_frame(frame)
        description = self.narrator_agent.describe_scene(inspected)

        latency_ms = (time.perf_counter() - started) * 1000.0
        audit = self.compliance_agent.audit_accessibility(
            inspected, description, latency_ms=latency_ms
        )

        if not audit.is_compliant:
            failed = [check.rule_id for check in audit.checks if not check.passed]
            logger.warning(
                "Frame %s failed accessibility audit (score %.1f): %s",
                inspected.frame_id,
                audit.compliance_score,
                ", ".join(failed),
            )

        return ProcessedStreamWindow(
            window_id=stable_event_id("WIN", f"{inspected.frame_id}|{description.event_id}"),
            frame=inspected,
            description=description,
            audit=audit,
        )
