from ml.intelligence.documents import ingest_text
from ml.intelligence.embeddings import HashEmbeddingProvider
from ml.intelligence.vector_store import SQLiteVectorStore


def test_sqlite_vector_store_round_trip(tmp_path):
    path = tmp_path / "vectors.db"
    provider = HashEmbeddingProvider(dimensions=32)
    store = SQLiteVectorStore(path, provider)
    chunks = ingest_text("Database latency increased after deployment.", "ops")
    store.add(chunks)

    assert store.count() == 1
    assert store.document_count() == 1
    hits = store.search("database latency")
    assert hits and hits[0][0].text == chunks[0].text


def test_sqlite_vector_store_reopens(tmp_path):
    path = tmp_path / "vectors.db"
    provider = HashEmbeddingProvider(dimensions=32)
    chunks = ingest_text("Router packet loss increased.", "ops")
    SQLiteVectorStore(path, provider).add(chunks)

    reopened = SQLiteVectorStore(path, provider)
    assert reopened.search("router packet loss")
