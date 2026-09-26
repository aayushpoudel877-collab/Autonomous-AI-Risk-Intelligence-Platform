from fastapi.testclient import TestClient
from backend.app.main import app

def test_retraining_job_is_accepted():
    client=TestClient(app)
    response=client.post("/api/v1/jobs",json={"kind":"retraining-assessment","reference":[0,1,0,1],"current":[0,1,1,1]})
    assert response.status_code==200
    assert response.json()["kind"]=="retraining-assessment"
