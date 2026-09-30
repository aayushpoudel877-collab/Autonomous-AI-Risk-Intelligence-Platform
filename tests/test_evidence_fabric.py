from ml.intelligence.evidence_fabric import EvidenceFabric, EvidenceRecord
from ml.intelligence.knowledge_graph import Edge, Node


def test_evidence_fabric_persists_cross_domain_context(tmp_path):
    db = tmp_path / "fabric.db"
    fabric = EvidenceFabric(str(db))
    fabric.add_evidence(EvidenceRecord(
        "ev-1", "text", "ops", "Database failure affected users.", {"tag": "incident"}
    ))
    fabric.add_node(Node("service", "service", "Service"))
    fabric.add_edge(Edge("ev-1", "supports", "service", 0.9))
    fabric.add_event({"id": "evt-1", "timestamp": "2026-09-30T08:00:00+00:00", "type": "incident"})

    restarted = EvidenceFabric(str(db))
    context = restarted.context()

    assert restarted.get_evidence("ev-1").source == "ops"
    assert context["graph"].neighbors("ev-1")[0].target == "service"
    assert context["provenance_links"][0]["evidence_id"] == "ev-1"
    assert context["events"][0]["id"] == "evt-1"


def test_evidence_fabric_replaces_duplicate_records(tmp_path):
    fabric = EvidenceFabric(str(tmp_path / "fabric.db"))
    fabric.add_evidence(EvidenceRecord("ev-1", "text", "old", "old", {}))
    fabric.add_evidence(EvidenceRecord("ev-1", "text", "new", "new", {}))
    assert fabric.get_evidence("ev-1").source == "new"
    assert fabric.stats()["evidence"] == 1


def test_provenance_can_create_context_node(tmp_path):
    fabric = EvidenceFabric(str(tmp_path / "fabric.db"))
    fabric.add_evidence(EvidenceRecord("ev-1", "text", "ops", "incident", {}))
    link = fabric.add_provenance("ev-1", "investigation:i-1")
    assert link.source == "ev-1"
    assert fabric.graph().neighbors("ev-1")[0].target == "investigation:i-1"
