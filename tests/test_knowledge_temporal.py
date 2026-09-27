from ml.intelligence.knowledge_graph import KnowledgeGraph,Node,Edge
from ml.intelligence.temporal import temporal_window,build_timeline

def test_graph_relationships():
    g=KnowledgeGraph(); g.add_node(Node("a","event","A")); g.add_node(Node("b","entity","B")); g.add_edge(Edge("a","mentions","b",.9))
    assert g.neighbors("a")[0].target=="b"

def test_temporal_window():
    events=[{"id":"2","timestamp":"2026-01-02T00:00:00+00:00"},{"id":"1","timestamp":"2026-01-01T00:00:00+00:00"}]
    assert build_timeline(events)[0]["id"]=="1"
    assert len(temporal_window(events,"2026-01-01T00:00:00+00:00","2026-01-01T23:59:59+00:00"))==1


def test_evidence_provenance_link():
    g = KnowledgeGraph()
    g.add_node(Node("service-1", "entity", "Service"))
    evidence = "evidence-1"
    g.add_node(Node(evidence, "evidence", evidence))
    g.add_edge(Edge(evidence, "supports", "service-1", 0.8))
    result = g.subgraph("service-1", depth=1)
    assert any(edge["source"] == evidence for edge in result["edges"])
