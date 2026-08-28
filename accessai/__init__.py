"""AccessAI: Real-Time Audio Description & Accessibility Multi-Agent Framework."""

from accessai.agents.compliance_agent import ComplianceAgent
from accessai.agents.narrator_agent import NarratorAgent
from accessai.agents.stream_agent import StreamAgent
from accessai.orchestration.accessai_engine import AccessAIEngine

__version__ = "1.1.0"

__all__ = [
    "AccessAIEngine",
    "ComplianceAgent",
    "NarratorAgent",
    "StreamAgent",
    "__version__",
]
