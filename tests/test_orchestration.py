from ml.intelligence.documents import ingest_text
from ml.intelligence.investigation import InvestigationEngine
from ml.intelligence.orchestration import (
    AdaptiveInvestigationPlanner,
    AutonomousInvestigator,
    InvestigationObjective,
    InvestigationPlanner,
)


def test_planner_creates_bounded_steps():
    trace = InvestigationPlanner().plan("i-1", "database latency", 3)
    assert len(trace.steps) == 3
    assert trace.steps[1].query == "database latency cause"


def test_autonomous_investigation_accumulates_evidence():
    chunks = ingest_text(
        "Database latency increased after deployment. Service impact was observed.",
        "ops",
    )
    trace = AutonomousInvestigator(InvestigationEngine(chunks)).run("i-2", "database latency", 3, 2)
    assert trace.status == "completed"
    assert trace.completed_steps >= 1
    assert trace.evidence
    assert trace.evidence[0]["step_id"]


def test_adaptive_planner_selects_missing_objective():
    planner = AdaptiveInvestigationPlanner()
    objective = InvestigationObjective("test", ("cause", "impact"), 2)
    step, aspect = planner.next_step(
        "i-3",
        "database latency",
        [{"chunk_id": "c1", "text": "Database latency increased after deployment.", "source": "ops"}],
        set(),
        objective,
    )
    assert step is not None
    assert aspect == "impact"
    assert "impact" in step.query


def test_adaptive_investigation_replans_from_evidence():
    chunks = ingest_text(
        "Database latency increased after deployment because a query plan changed. "
        "The service impacted users and caused request failures. "
        "The incident occurred after the deployment.",
        "ops",
    )
    objective = InvestigationObjective("incident", ("cause", "impact", "timeline"), 3)
    trace = AutonomousInvestigator(InvestigationEngine(chunks)).run_adaptive(
        "i-4", "database latency", max_steps=5, top_k=2, objective=objective
    )
    assert trace.status == "completed"
    assert trace.completed_steps >= 1
    assert trace.decisions
    assert trace.stop_reason in {"objectives_satisfied", "max_steps_reached"}
    assert any(d.objective in {"cause", "impact", "timeline", "entity", "evidence"} for d in trace.decisions)


def test_adaptive_api():
    from fastapi.testclient import TestClient
    from backend.app.main import app

    client = TestClient(app)
    client.post("/api/v1/intelligence/documents", json={
        "text": "Database latency increased because deployment changed a query plan. "
                "Users were affected during the incident.",
        "source": "ops-adaptive",
    })
    response = client.post("/api/v1/intelligence/investigations/adaptive", json={
        "investigation_id": "api-adaptive-1",
        "query": "database latency",
        "max_steps": 4,
        "top_k": 2,
        "min_evidence": 2,
        "required_aspects": ["cause", "impact"],
    })
    assert response.status_code == 200
    body = response.json()
    assert body["steps"]
    assert body["decisions"]
