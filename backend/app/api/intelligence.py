import os
from dataclasses import asdict

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ml.intelligence.documents import ingest_text
from ml.intelligence.embeddings import HashEmbeddingProvider
from ml.intelligence.entities import extract_entities, extract_relations
from ml.intelligence.investigation import InvestigationEngine
from ml.intelligence.vector_store import SQLiteVectorStore

router = APIRouter(prefix="/intelligence", tags=["intelligence"])
_VECTOR_DB = os.getenv("AEGISMIND_VECTOR_DB", "data/vector_store.db")
_PROVIDER = HashEmbeddingProvider()
_STORE = SQLiteVectorStore(_VECTOR_DB, _PROVIDER)


class DocumentRequest(BaseModel):
    text: str = Field(min_length=1)
    source: str = "user-provided"


class InvestigationRequest(BaseModel):
    investigation_id: str
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


@router.post("/documents")
def add_document(payload: DocumentRequest):
    chunks = ingest_text(payload.text, payload.source)
    _STORE.add(chunks)
    return {"document_id": chunks[0].document_id, "chunks_created": len(chunks)}


@router.post("/investigations")
def investigate(payload: InvestigationRequest):
    result = InvestigationEngine(persistent_index=_STORE).investigate(
        payload.investigation_id, payload.query, payload.top_k
    )
    return asdict(result)


@router.post("/reports")
def report(payload: InvestigationRequest):
    result = InvestigationEngine(persistent_index=_STORE).report(
        payload.investigation_id, payload.query, payload.top_k
    )
    return asdict(result)


@router.post("/entities")
def entities(payload: DocumentRequest):
    return {
        "entities": [asdict(entity) for entity in extract_entities(payload.text)],
        "relations": [asdict(relation) for relation in extract_relations(payload.text)],
    }


@router.get("/documents")
def document_stats():
    return {"documents": _STORE.document_count(), "chunks": _STORE.count()}
