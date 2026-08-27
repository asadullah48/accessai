"""
AccessAI: Real-Time Audio Description & Accessibility Multi-Agent Framework
"""

__version__ = "1.0.0"

from accessai.agents.stream_agent import StreamAgent
from accessai.agents.narrator_agent import NarratorAgent
from accessai.agents.compliance_agent import ComplianceAgent
from accessai.orchestration.accessai_engine import AccessAIEngine

__all__ = [
    "StreamAgent",
    "NarratorAgent",
    "ComplianceAgent",
    "AccessAIEngine"
]
