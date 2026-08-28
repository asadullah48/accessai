"""HTTP gateway contract."""

import xml.etree.ElementTree as ET

import pytest
from fastapi.testclient import TestClient

from accessai import __version__
from accessai.server import app

client = TestClient(app)

DESCRIBE_URL = "/api/v1/accessibility/describe-stream"


def payload(**overrides):
    base = {
        "frame_id": "FRM-TEST-01",
        "timestamp_ms": 25000,
        "scene_category": "Keynote Lecture",
        "visual_entities": ["Professor writing formula on whiteboard"],
        "on_screen_ocr": "E = mc^2 Proof",
        "inter_dialogue_gap_sec": 3.2,
    }
    base.update(overrides)
    return base


def test_dashboard_is_served():
    res = client.get("/")
    assert res.status_code == 200
    assert "AccessAI" in res.text


def test_healthz_reports_the_package_version():
    res = client.get("/healthz")
    assert res.status_code == 200
    assert res.json() == {"status": "healthy", "service": "AccessAI", "version": __version__}


def test_readyz():
    res = client.get("/readyz")
    assert res.status_code == 200
    assert res.json()["assistive_agents_active"] == 3


def test_describe_stream_returns_description_and_audit():
    res = client.post(DESCRIBE_URL, json=payload())
    assert res.status_code == 200
    data = res.json()
    assert "Professor writing formula" in data["description"]["description_text"]
    assert data["audit"]["is_compliant"] is True
    assert data["audit"]["compliance_score"] == 100.0


def test_response_exposes_the_individual_checks():
    data = client.post(DESCRIBE_URL, json=payload()).json()
    rule_ids = {check["rule_id"] for check in data["audit"]["checks"]}
    assert {"dialogue-collision", "wcag-1.2.5", "wcag-1.2.7", "wcag-1.4.6", "latency"} == rule_ids


def test_narrow_gap_returns_a_failing_audit_not_an_error():
    res = client.post(DESCRIBE_URL, json=payload(inter_dialogue_gap_sec=0.2))
    assert res.status_code == 200
    assert res.json()["audit"]["is_compliant"] is False


def test_empty_entities_does_not_500():
    res = client.post(DESCRIBE_URL, json=payload(visual_entities=[]))
    assert res.status_code == 200
    assert res.json()["description"]["description_text"].strip()


def test_ocr_with_xml_metacharacters_does_not_500():
    """The gap must be wide enough that the OCR survives pruning into the markup."""
    res = client.post(
        DESCRIBE_URL,
        json=payload(on_screen_ocr="Tom & Jerry <ep 3>", inter_dialogue_gap_sec=10.0),
    )
    assert res.status_code == 200
    markup = res.json()["description"]["ssml_markup"]
    assert "Tom &amp; Jerry &lt;ep 3&gt;" in markup
    ET.fromstring(markup)


@pytest.mark.parametrize(
    "bad",
    [
        {"inter_dialogue_gap_sec": -1.0},
        {"inter_dialogue_gap_sec": 999.0},
        {"timestamp_ms": -1},
        {"caption_foreground_hex": "chartreuse"},
        {"frame_id": ""},
    ],
)
def test_invalid_input_is_rejected_with_422(bad):
    assert client.post(DESCRIBE_URL, json=payload(**bad)).status_code == 422


def test_openapi_schema_documents_the_endpoint():
    schema = client.get("/openapi.json").json()
    assert DESCRIBE_URL in schema["paths"]
    assert schema["info"]["version"] == __version__


# --------------------------------------------------------------------- CORS ---


def test_unlisted_origin_gets_no_cors_grant():
    """Default settings serve a same-origin studio; strangers get no ACAO header."""
    res = client.get("/healthz", headers={"Origin": "https://evil.example"})
    assert res.status_code == 200
    assert "access-control-allow-origin" not in res.headers


def test_configured_origin_is_echoed():
    res = client.get("/healthz", headers={"Origin": "http://127.0.0.1:8015"})
    assert res.headers["access-control-allow-origin"] == "http://127.0.0.1:8015"


def test_credentials_are_never_granted_by_default():
    res = client.get("/healthz", headers={"Origin": "http://127.0.0.1:8015"})
    assert "access-control-allow-credentials" not in res.headers


def test_preflight_from_unlisted_origin_is_rejected():
    res = client.options(
        DESCRIBE_URL,
        headers={
            "Origin": "https://evil.example",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert res.status_code == 400
    assert "access-control-allow-origin" not in res.headers


def test_preflight_from_configured_origin_succeeds():
    res = client.options(
        DESCRIBE_URL,
        headers={
            "Origin": "http://localhost:8015",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert res.status_code == 200
    assert res.headers["access-control-allow-origin"] == "http://localhost:8015"


# ---------------------------------------------------------- request context ---


def test_every_response_carries_a_request_id():
    res = client.get("/healthz")
    assert res.headers["x-request-id"]


def test_request_ids_differ_between_requests():
    first = client.get("/healthz").headers["x-request-id"]
    second = client.get("/healthz").headers["x-request-id"]
    assert first != second


def test_inbound_request_id_is_preserved():
    """A trace started at a proxy must survive the hop."""
    res = client.get("/healthz", headers={"X-Request-ID": "trace-from-proxy-123"})
    assert res.headers["x-request-id"] == "trace-from-proxy-123"


def test_process_time_header_is_present_and_numeric():
    res = client.post(DESCRIBE_URL, json=payload())
    assert float(res.headers["x-process-time-ms"]) >= 0.0


def test_request_id_is_present_on_a_rejected_request():
    res = client.post(DESCRIBE_URL, json=payload(inter_dialogue_gap_sec=-1.0))
    assert res.status_code == 422
    assert res.headers["x-request-id"]


def _gateway_logs(caplog):
    """Only this module's records; caplog also captures httpx and uvicorn."""
    return [r for r in caplog.records if r.name == "accessai.server"]


def test_api_traffic_is_logged_at_info(caplog):
    import logging

    with caplog.at_level(logging.INFO, logger="accessai.server"):
        client.post(DESCRIBE_URL, json=payload())
    assert any(DESCRIBE_URL in r.getMessage() for r in _gateway_logs(caplog))


def test_health_probes_are_not_logged_at_info(caplog):
    """Probes fire every few seconds; at INFO they would bury real traffic."""
    import logging

    with caplog.at_level(logging.INFO, logger="accessai.server"):
        client.get("/healthz")
    assert not [r for r in _gateway_logs(caplog) if "/healthz" in r.getMessage()]


def test_health_probes_are_still_logged_at_debug(caplog):
    """Suppressed at INFO, but never silently dropped."""
    import logging

    with caplog.at_level(logging.DEBUG, logger="accessai.server"):
        client.get("/healthz")
    assert [r for r in _gateway_logs(caplog) if "/healthz" in r.getMessage()]


def test_startup_logs_the_effective_configuration(caplog):
    """A deployment must be able to prove which CORS policy was actually loaded."""
    import logging

    from accessai.server import app as fresh_app

    # Entering the TestClient context manager runs the lifespan handler.
    with caplog.at_level(logging.INFO, logger="accessai.server"), TestClient(fresh_app):
        pass

    startup = [r.getMessage() for r in _gateway_logs(caplog) if "starting in" in r.getMessage()]
    assert startup, "no startup configuration line was logged"
    assert "cors_origins=" in startup[0]
    assert "credentials=False" in startup[0]
