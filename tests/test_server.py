from fastapi.testclient import TestClient
from accessai.server import app

client = TestClient(app)

def test_server_dashboard_root():
    res = client.get("/")
    assert res.status_code == 200
    assert "AccessAI" in res.text

def test_server_healthz():
    res = client.get("/healthz")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_server_readyz():
    res = client.get("/readyz")
    assert res.status_code == 200
    assert res.json()["assistive_agents_active"] == 3

def test_server_describe_stream_api():
    payload = {
        "frame_id": "FRM-TEST-01",
        "timestamp_ms": 25000,
        "scene_category": "Keynote Lecture",
        "visual_entities": ["Professor writing formula on whiteboard"],
        "on_screen_ocr": "E = mc^2 Proof",
        "inter_dialogue_gap_sec": 3.2
    }
    res = client.post("/api/v1/accessibility/describe-stream", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "Professor writing formula" in data["description"]["description_text"]
    assert data["audit"]["is_compliant"] is True
