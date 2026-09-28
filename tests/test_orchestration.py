from ml.intelligence.documents import ingest_text
from ml.intelligence.investigation import InvestigationEngine
from ml.intelligence.orchestration import AutonomousInvestigator, InvestigationPlanner

def test_planner_creates_bounded_steps():
    trace = InvestigationPlanner().plan("i-1", "database latency", 3)
    assert len(trace.steps) == 3
    assert trace.steps[1].query == "database latency cause"

def test_autonomous_investigation_accumulates_evidence():
    chunks = ingest_text("Database latency increased after deployment. Service impact was observed.", "ops")
    trace = AutonomousInvestigator(InvestigationEngine(chunks)).run("i-2", "database latency", 3, 2)
    assert trace.status == "completed"
    assert trace.completed_steps >= 1
    assert trace.evidence
    assert trace.evidence[0]["step_id"]

def test_autonomous_api():
    from fastapi.testclient import TestClient
    from backend.app.main import app
    client = TestClient(app)
    client.post("/api/v1/intelligence/documents", json={
        "text": "Database latency increased after deployment.", "source": "ops-autonomous"})
    response = client.post("/api/v1/intelligence/investigations/autonomous", json={
        "investigation_id": "api-auto-1", "query": "database latency", "max_steps": 2, "top_k": 2})
    assert response.status_code == 200
    assert response.json()["steps"]
    assert response.json()["evidence"]
