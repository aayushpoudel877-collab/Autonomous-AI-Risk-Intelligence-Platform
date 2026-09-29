from ml.intelligence.documents import ingest_text
from ml.intelligence.investigation import InvestigationEngine
from ml.intelligence.knowledge_graph import KnowledgeGraph, Node, Edge
from ml.intelligence.orchestration import (
    AdaptiveInvestigationPlanner, AutonomousInvestigator, InvestigationObjective, InvestigationPlanner
)


def test_planner_creates_bounded_steps():
    trace = InvestigationPlanner().plan("i-1", "database latency", 3)
    assert len(trace.steps) == 3
    assert trace.steps[1].query == "database latency cause"


def test_autonomous_investigation_accumulates_evidence():
    chunks = ingest_text("Database latency increased after deployment. Service impact was observed.", "ops")
    trace = AutonomousInvestigator(InvestigationEngine(chunks)).run("i-2", "database latency", 3, 2)
    assert trace.status == "completed"
    assert trace.completed_steps >= 1
    assert trace.evidence[0]["step_id"]


def test_adaptive_planner_selects_missing_objective():
    planner = AdaptiveInvestigationPlanner()
    objective = InvestigationObjective("test", ("cause", "impact"), 2)
    step, aspect = planner.next_step(
        "i-3", "database latency",
        [{"chunk_id": "c1", "text": "Database latency increased after deployment.", "source": "ops"}],
        set(), objective
    )
    assert step is not None
    assert aspect == "cause"
    assert "cause" in step.query


def test_graph_temporal_and_provenance_coverage():
    graph = KnowledgeGraph()
    graph.add_node(Node("db", "system_component", "Database"))
    graph.add_node(Node("query", "event", "QueryPlan"))
    graph.add_edge(Edge("db", "causes", "query", 0.9))
    planner = AdaptiveInvestigationPlanner()
    evidence = [{"chunk_id": "c1", "text": "Database failure affected users after deployment.", "source": "ops"}]
    events = [
        {"id": "e1", "timestamp": "2026-09-29T08:00:00+00:00"},
        {"id": "e2", "timestamp": "2026-09-29T08:20:00+00:00"},
    ]
    objective = InvestigationObjective("x", ("cause",), 1, min_provenance=1, require_graph_context=True, require_temporal_context=True)
    coverage = planner.coverage(evidence, objective, graph, events, [{"evidence_id": "c1"}])
    assert coverage["graph_context_found"]
    assert coverage["temporal_context_found"]
    assert coverage["provenance_count"] == 1


def test_adaptive_investigation_replans_from_context():
    chunks = ingest_text(
        "Database latency increased because deployment changed a query plan. "
        "Users were affected during the incident. The incident occurred after deployment.",
        "ops"
    )
    graph = KnowledgeGraph()
    graph.add_node(Node("db", "system_component", "Database"))
    graph.add_node(Node("svc", "service", "Service"))
    graph.add_edge(Edge("db", "impacts", "svc", 0.8))
    objective = InvestigationObjective("incident", ("cause", "impact"), 2, min_provenance=1, require_graph_context=True)
    trace = AutonomousInvestigator(InvestigationEngine(chunks)).run_adaptive(
        "i-4", "database latency", max_steps=5, top_k=2, objective=objective,
        graph=graph, provenance_links=[{"evidence_id": chunks[0].chunk_id}]
    )
    assert trace.status == "completed"
    assert trace.decisions
    assert trace.coverage["provenance_count"] == 1


def test_adaptive_api():
    from fastapi.testclient import TestClient
    from backend.app.main import app
    client = TestClient(app)
    client.post("/api/v1/intelligence/documents", json={
        "text": "Database latency increased because deployment changed a query plan. Users were affected during the incident.",
        "source": "ops-adaptive"
    })
    response = client.post("/api/v1/intelligence/investigations/adaptive", json={
        "investigation_id": "api-adaptive-2", "query": "database latency", "max_steps": 4, "top_k": 2,
        "min_evidence": 2, "required_aspects": ["cause", "impact"], "min_provenance": 0
    })
    assert response.status_code == 200
    assert response.json()["decisions"]
