import time
from accessai.core.models import LiveStreamFrame, ProcessedStreamWindow
from accessai.agents.stream_agent import StreamAgent
from accessai.agents.narrator_agent import NarratorAgent
from accessai.agents.compliance_agent import ComplianceAgent

class AccessAIEngine:
    """
    AccessAIEngine: Coordinates the real-time stream accessibility loop.
    """
    def __init__(self):
        self.stream_agent = StreamAgent()
        self.narrator_agent = NarratorAgent()
        self.compliance_agent = ComplianceAgent()

    def process_live_frame(self, frame: LiveStreamFrame) -> ProcessedStreamWindow:
        t0 = time.time()
        
        # Step 1: Stream Analysis
        inspected = self.stream_agent.inspect_frame(frame)

        # Step 2: Narrator Description Synthesis
        desc = self.narrator_agent.describe_scene(inspected)

        # Step 3: Compliance Audit
        latency_ms = max(45.0, (time.time() - t0) * 1000.0)
        audit = self.compliance_agent.audit_accessibility(inspected, desc, latency_ms=latency_ms)

        return ProcessedStreamWindow(
            window_id=f"WIN-{abs(hash(frame.frame_id)) % 10000}",
            frame=inspected,
            description=desc,
            audit=audit
        )
