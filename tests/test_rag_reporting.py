from ml.intelligence.documents import ingest_text
from ml.intelligence.embeddings import RetrievalIndex
from ml.intelligence.investigation import InvestigationEngine
from ml.intelligence.entities import extract_entities,extract_relations

def test_embedding_index_search():
    chunks=ingest_text("Database latency increased after deployment.","ops")
    idx=RetrievalIndex(); idx.add(chunks)
    assert idx.search("database latency")

def test_investigation_report():
    chunks=ingest_text("Router packet loss increased during the incident.","ops")
    report=InvestigationEngine(chunks).report("i-2","router packet loss")
    assert report.evidence and report.limitations

def test_entity_relation_extraction():
    assert extract_entities("AegisMind service uses Database")
    assert extract_relations("AegisMind service uses Database")
