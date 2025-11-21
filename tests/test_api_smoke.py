from fastapi.testclient import TestClient
from app.main import app
def test_healthz_ok():
    c = TestClient(app)
    r = c.get("/healthz")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"
def test_metrics_text():
    c = TestClient(app)
    r = c.get("/metrics")
    assert r.status_code == 200
    assert r.headers.get("content-type","").startswith("text/plain")
    assert "app_requests_total" in r.text