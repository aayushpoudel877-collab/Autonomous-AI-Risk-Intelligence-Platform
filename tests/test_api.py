from fastapi.testclient import TestClient
from backend.app.main import app
client=TestClient(app)
def test_health(): assert client.get("/health").status_code==200
def test_risk_api():
    r=client.post("/api/v1/risk/analyze",json={"signals":[.8,.9],"source":"test"})
    assert r.status_code==200 and r.json()["risk_level"]=="high"
