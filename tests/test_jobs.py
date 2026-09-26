from fastapi.testclient import TestClient
from backend.app.main import app

client=TestClient(app)

def test_job_lifecycle():
    created=client.post("/api/v1/jobs",json={"kind":"risk-analysis","source":"test"})
    assert created.status_code == 200
    job_id=created.json()["id"]
    fetched=client.get(f"/api/v1/jobs/{job_id}")
    assert fetched.status_code == 200 and fetched.json()["status"] == "queued"
