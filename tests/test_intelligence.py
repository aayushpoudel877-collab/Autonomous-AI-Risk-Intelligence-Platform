from fastapi.testclient import TestClient
from backend.app.main import app
from ml.intelligence.documents import ingest_text
from ml.intelligence.retrieval import retrieve

def test_document_chunking():
    chunks=ingest_text("Network outage detected. Router logs show packet loss.","ops")
    assert chunks and chunks[0].source=="ops"

def test_retrieval_returns_matching_evidence():
    chunks=ingest_text("Database latency increased after deployment.","ops")
    result=retrieve("database latency",chunks)
    assert result and result[0].score>0

def test_intelligence_api():
    c=TestClient(app)
    assert c.post("/api/v1/intelligence/documents",json={"text":"Service latency increased significantly.","source":"report"}).status_code==200
    response=c.post("/api/v1/intelligence/investigations",json={"investigation_id":"i-1","query":"service latency"})
    assert response.status_code==200 and response.json()["evidence"]
