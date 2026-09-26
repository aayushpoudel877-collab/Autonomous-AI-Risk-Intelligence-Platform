from fastapi.testclient import TestClient
from backend.app.main import app

client=TestClient(app)

def test_event_history_endpoint():
    created=client.post("/api/v1/risk/analyze",json={"signals":[.2,.3],"source":"history-test"})
    assert created.status_code == 200
    response=client.get("/api/v1/risk/events?limit=5")
    assert response.status_code == 200
    assert any(event["source"]=="history-test" for event in response.json())
