from fastapi.testclient import TestClient
from backend.app.main import app

client=TestClient(app)

def test_monitoring_metrics():
    client.post("/api/v1/risk/analyze",json={"signals":[.6,.7],"source":"monitoring"})
    result=client.get("/api/v1/monitoring/metrics")
    assert result.status_code == 200
    assert result.json()["requests"] >= 1
