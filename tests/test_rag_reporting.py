import numpy as np

from ml.intelligence.documents import ingest_text
from ml.intelligence.embeddings import HashEmbeddingProvider, RetrievalIndex
from ml.intelligence.entities import extract_entities, extract_relations
from ml.intelligence.investigation import InvestigationEngine


def test_embedding_index_search():
    chunks = ingest_text("Database latency increased after deployment.", "ops")
    index = RetrievalIndex()
    index.add(chunks)
    assert index.search("database latency")


def test_hash_embeddings_are_reproducible():
    provider = HashEmbeddingProvider(dimensions=32)
    first = provider.encode(["database latency"])
    second = provider.encode(["database latency"])
    assert np.array_equal(first, second)


def test_investigation_report():
    chunks = ingest_text("Router packet loss increased during the incident.", "ops")
    report = InvestigationEngine(chunks).report("i-2", "router packet loss")
    assert report.evidence and report.limitations


def test_entity_relation_extraction():
    assert extract_entities("AegisMind service uses Database")
    assert extract_relations("AegisMind service uses Database")
