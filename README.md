# 👁️ AccessAI: Real-Time Audio Description & Accessibility Multi-Agent Framework

> **An assistive multi-agent framework that generates live audio descriptions fitted into dialogue gaps, and audits them against WCAG 2.2 AAA, Section 508 and ADA Title III.**

[![CI](https://github.com/asadullah48/accessai/actions/workflows/ci.yml/badge.svg)](https://github.com/asadullah48/accessai/actions/workflows/ci.yml)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://www.python.org/)
[![WCAG 2.2 AAA](https://img.shields.io/badge/Accessibility-WCAG%202.2%20AAA-brightgreen.svg)]()
[![FastAPI](https://img.shields.io/badge/API-FastAPI%20%3A8015-teal.svg)](http://127.0.0.1:8015/docs)
[![Author](https://img.shields.io/badge/Author-Asadullah%20Shafique-purple.svg)](https://asadullahshafique-devunity.vercel.app)

---

## 🚀 What this does

Live streams are largely inaccessible to blind and low-vision viewers: audio description
normally requires manual post-production, so live broadcast goes undescribed. Naive
automation makes it worse by talking over the dialogue.

AccessAI models the three jobs that solving this requires, and **measures** whether the
result would actually be usable:

1. **`StreamAgent`** normalises an analysed frame: salient visual entities, on-screen OCR
   text, and the length of the silence gap between lines of dialogue.
2. **`NarratorAgent`** writes the most detailed description that still fits that gap,
   walking a degradation ladder and shortening until it fits.
3. **`ComplianceAgent`** audits the result against five criteria and returns a weighted
   compliance score with a per-criterion breakdown.

### The audit is evaluated, not asserted

Every criterion is computed from the frame and the description, and every one can fail:

| Criterion | How it is measured | Weight |
| :--- | :--- | ---: |
| **Zero Dialogue Collision** | Estimated speech duration vs. the available silence gap | 30 |
| **WCAG 1.2.5** Audio Description | A non-empty description track was produced | 25 |
| **WCAG 1.4.6** Contrast (Enhanced) | Real relative-luminance maths on the caption colours | 20 |
| **WCAG 1.2.7** Extended Audio Description | Engaged only when the gap is too short; needs an extended pause | 15 |
| **Latency budget** | Measured with `perf_counter`, reported as measured | 10 |

`compliance_score` is the weight of the criteria that passed, so it moves with *how much*
failed rather than flipping between two constants.

The weights live in `accessai/core/compliance_guardrails.py::CHECK_WEIGHTS` and encode a
policy judgement: a dialogue collision is weighted heaviest because it does not merely
fail to help, it actively masks speech the listener could otherwise hear. Tune them to
your own risk posture.

---

## 🏛️ Architecture

```
                    +-------------------------+
                    |  Live Stream / Video    |
                    +------------+------------+
                                 |
                    +------------v------------+
                    |       StreamAgent       |
                    |  - Entity normalisation |
                    |  - Silence gap budget   |
                    +------------+------------+
                                 |
                    +------------v------------+
                    |      NarratorAgent      |
                    |  - Degradation ladder   |
                    |  - Escaped SSML output  |
                    +------------+------------+
                                 |
                    +------------v------------+
                    |     ComplianceAgent     |
                    |  - 5 measured criteria  |
                    |  - Weighted score       |
                    +-------------------------+
```

### Description degradation ladder

When the gap is too short, detail is dropped in order of importance. The primary subject
is never dropped, because a description that names nothing is worse than a terse one.

| Gap | Result |
| :--- | :--- |
| 6.0s | `On screen: Presenter gesturing at slide, Bar chart showing revenue growth, Audience clapping. "Q4 Enterprise AI Growth: +142% YoY".` |
| 3.0s | `Presenter gesturing at slide.` |
| 0.9s | `Presenter gesturing.` |
| 0.2s | Shortest form returned with `fits_silence_gap: false` — below the minimum utterance length nothing can fit, and the audit says so |

---

## 🛠️ Quick Start

```bash
git clone https://github.com/asadullah48/accessai.git
cd accessai

pip install -e ".[dev]"

pytest -v
ruff check accessai tests

uvicorn accessai.server:app --host 127.0.0.1 --port 8015 --reload
```

- **Accessibility Studio**: <http://127.0.0.1:8015/>
- **OpenAPI docs**: <http://127.0.0.1:8015/docs>

### Container

```bash
docker compose up --build
```

The image runs as an unprivileged user (uid 10001). The compose file and the Helm chart
add a read-only root filesystem, `no-new-privileges`, and drop all Linux capabilities.

### Published image

Multi-arch (`linux/amd64`, `linux/arm64`) images are published to GHCR on every `v*` tag,
with provenance and an SBOM:

```bash
docker run --rm -p 8015:8015 ghcr.io/asadullah48/accessai:1.1.0
```

The Helm chart installs that image directly:

```bash
helm upgrade --install accessai ./helm --set image.tag=1.1.0
```

Releasing a new version is `git tag vX.Y.Z && git push origin vX.Y.Z`. The workflow runs
the test suite against the tagged tree before it builds, then pulls the published image by
digest and smoke tests it.

---

## 🔌 API

`POST /api/v1/accessibility/describe-stream`

```jsonc
{
  "frame_id": "FRM-8820",
  "timestamp_ms": 14200,
  "scene_category": "Keynote Presentation",
  "visual_entities": ["Presenter gesturing at slide", "Bar chart showing growth"],
  "on_screen_ocr": "Q4 Enterprise AI Growth: +142% YoY",
  "inter_dialogue_gap_sec": 3.5,      // 0.0 - 60.0
  "extended_pause_available": false,  // may the player pause the video?
  "caption_foreground_hex": "#F2F5F7",
  "caption_background_hex": "#0B0F14",
  "caption_text_size": "NORMAL"       // NORMAL | LARGE
}
```

Returns the frame, the generated `AudioDescriptionEvent` (escaped SSML, estimated speech
duration, `fits_silence_gap`, `prune_level`) and the `AccessibilityAuditResult` with its
per-criterion `checks` array. Out-of-range input is rejected with `422`.

`GET /healthz` liveness · `GET /readyz` readiness.

Every response carries `X-Request-ID` (an inbound one is preserved, so a trace survives a
proxy hop) and `X-Process-Time-Ms`.

---

## ⚙️ Configuration

All settings are environment variables, read at startup and logged so a deployment can
prove which policy was loaded.

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `ACCESSAI_CORS_ORIGINS` | `http://127.0.0.1:8015,http://localhost:8015` | Comma-separated browser origins allowed to call the API. `*` permitted. |
| `ACCESSAI_CORS_ALLOW_CREDENTIALS` | `false` | Send `Access-Control-Allow-Credentials`. |
| `ACCESSAI_LOG_LEVEL` | `INFO` | Root log level. |
| `ACCESSAI_LOG_HEALTH_PROBES` | `false` | Log `/healthz` and `/readyz` at INFO instead of DEBUG. |
| `ACCESSAI_ENVIRONMENT` | `development` | Free-form deployment label (`ENVIRONMENT` also honoured). |

**Credentials are never paired with a wildcard origin.** The Fetch specification forbids
returning `Access-Control-Allow-Origin: *` together with
`Access-Control-Allow-Credentials: true` — a browser rejects the response, so every
credentialed cross-origin call silently fails. If both are requested the loader disables
credentials and logs why, rather than emitting a configuration that cannot work. To send
credentials, list explicit origins.

---

## 🎛️ Interactive Accessibility Studio

A bilingual (English / Arabic RTL) dashboard at `/`, built to the standard it audits:

- Every control has an associated `<label>`; results announce through `aria-live` regions
- Keyboard skip link, visible focus indicators on every interactive element
- Pass/fail stated in text, never by colour alone (WCAG 1.4.1)
- Honours `prefers-reduced-motion` and forced-colours themes
- Headline metrics are driven by the audit that just ran, so they cannot drift from the
  record shown beneath them
- Palette verified with this project's own contrast module: every token clears 7:1 on
  both surfaces

---

## ⚖️ Scope and honesty

This is a **working model of the pipeline**, not a deployed broadcast system. Being
precise about the boundary:

- **Real:** the WCAG contrast mathematics (`accessai/core/wcag.py`, validated against the
  published boundary colours `#767676` and `#595959`), the speech-duration estimate, the
  gap-fitting degradation ladder, SSML escaping, the weighted scoring, and the latency
  measurement.
- **Not included:** computer vision, OCR, and speech synthesis. `visual_entities` and
  `on_screen_ocr` are supplied as input rather than extracted from pixels, and the SSML is
  emitted for a downstream engine rather than rendered to audio.

Speech duration is a word-rate estimate (3.8 words/sec plus sentence pauses), not a
measurement of synthesized audio; a production deployment should feed the real duration
back from the TTS engine.

---

## 🧪 Development

```bash
pytest --cov=accessai --cov-report=term-missing   # 145 tests, 99% coverage
ruff check accessai tests
ruff format accessai tests
```

`tests/test_regressions.py` pins defects found in the 1.0.0 audit; each test there fails
against the pre-1.1.0 implementation.

### Continuous integration

Every push and pull request runs ruff, the suite against Python 3.10 through 3.13, and a
Docker build whose container is smoke tested over HTTP.

Workflow actions are pinned to commit SHAs rather than moving tags, with the release each
one corresponds to kept in a trailing comment:

```yaml
- uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
```

A major tag is mutable, and these workflows run with a token that can write packages, so
the pin fixes exactly which code runs. Dependabot proposes updates weekly as one grouped
pull request, which is what keeps a pinned action from quietly going stale.

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

---

## 📄 License

Apache License 2.0 — see [LICENSE](./LICENSE).
