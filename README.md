# 👁️ AccessAI: Real-Time Audio Description & Accessibility Multi-Agent Framework

> **An assistive multi-agent framework generating live audio descriptions and real-time visual summaries for visually impaired users with WCAG 2.2 AAA and Section 508 compliance.**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://www.python.org/)
[![WCAG 2.2 AAA](https://img.shields.io/badge/Accessibility-WCAG%202.2%20AAA-brightgreen.svg)]()
[![FastAPI](https://img.shields.io/badge/API-FastAPI%20%3A8015-teal.svg)](http://127.0.0.1:8015/docs)
[![Author](https://img.shields.io/badge/Author-Asadullah%20Shafique-purple.svg)](https://asadullahshafique-devunity.vercel.app)

---

## 🚀 Key Value Propositions

1. **Specialized Assistive Multi-Agent Roles**:
   - **`StreamAgent`**: Monitors live video feeds, extracts visual salience, performs on-screen OCR, and detects inter-dialogue silence gaps.
   - **`NarratorAgent`**: Generates vivid, concise audio descriptions formatted as SSML speech markup fitted precisely into dialogue pauses.
   - **`ComplianceAgent`**: Validates descriptions against WCAG 2.2 AAA, Section 508, and ADA Title III standards, ensuring zero speech collisions and sub-200ms latency.
2. **Zero Dialogue Collision Guardrails**: Enforces mathematical constraints ensuring synthesized speech never overlaps human conversation or speaker dialogue.
3. **Spatial Audio Cues**: Embeds directional spatial sound markers (Center, Left Offscreen, Right Offscreen) for enhanced spatial orientation.
4. **Sub-200ms E2E Latency**: Optimized stream ingestion pipeline built for live broadcast and interactive video conferencing.
5. **Interactive Accessibility Studio**: Dark cyber-glassmorphic bilingual (English/Arabic RTL) dashboard with live video simulator, real-time waveform visualizer, and WCAG 2.2 AAA compliance scorecard.

---

## 🏛️ AccessAI Architecture

```
                    ┌─────────────────────────┐
                    │  Live Stream / Video    │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │       StreamAgent       │
                    │  • Visual Salience      │
                    │  • Silence Gap Analysis │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │      NarratorAgent      │
                    │  • Audio Description    │
                    │  • SSML Speech Engine   │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │     ComplianceAgent     │
                    │  • WCAG 2.2 AAA Audit   │
                    │  • Collision Prevention │
                    └─────────────────────────┘
```

---

## 🛠️ Quick Start

```powershell
# 1. Clone repository
git clone https://github.com/asadullah48/accessai.git
cd accessai

# 2. Install dependencies
pip install -e .

# 3. Run automated test suite
python -m pytest tests -v

# 4. Start local gateway & frontend studio
uvicorn accessai.server:app --host 127.0.0.1 --port 8015 --reload
```

- **Interactive Accessibility Studio**: [http://127.0.0.1:8015/](http://127.0.0.1:8015/)
- **Swagger OpenAPI Docs**: [http://127.0.0.1:8015/docs](http://127.0.0.1:8015/docs)

---

## 🌐 Connected Ecosystem & Portfolio

- **DevUnity Portfolio**: [https://asadullahshafique-devunity.vercel.app](https://asadullahshafique-devunity.vercel.app)
- **CollabX**: [https://github.com/asadullah48/collabx](https://github.com/asadullah48/collabx)
- **DocuCode**: [https://github.com/asadullah48/docucode](https://github.com/asadullah48/docucode)
- **PrivateBrain**: [https://github.com/asadullah48/privatebrain](https://github.com/asadullah48/privatebrain)
- **ResearchX**: [https://github.com/asadullah48/researchx](https://github.com/asadullah48/researchx)
- **GraphAI**: [https://github.com/asadullah48/graphai](https://github.com/asadullah48/graphai)
- **LoopAI**: [https://github.com/asadullah48/loopai](https://github.com/asadullah48/loopai)
- **HarnessAI**: [https://github.com/asadullah48/harnessai](https://github.com/asadullah48/harnessai)
- **SecureBridge**: [https://github.com/asadullah48/securebridge](https://github.com/asadullah48/securebridge)
- **WorkforceAI Academy**: [https://github.com/asadullah48/workforceai-academy](https://github.com/asadullah48/workforceai-academy)
- **ConciergeAgent**: [https://github.com/asadullah48/conciergeagent](https://github.com/asadullah48/conciergeagent)
- **ContextX**: [https://github.com/asadullah48/contextx](https://github.com/asadullah48/contextx)
- **GuardrailAI**: [https://github.com/asadullah48/guardrailai](https://github.com/asadullah48/guardrailai)
- **MarketAgentHub**: [https://github.com/asadullah48/marketagenthub](https://github.com/asadullah48/marketagenthub)
- **WorkforceAI**: [https://github.com/asadullah48/workforceai](https://github.com/asadullah48/workforceai)
- **DomainX**: [https://github.com/asadullah48/domainx](https://github.com/asadullah48/domainx)
