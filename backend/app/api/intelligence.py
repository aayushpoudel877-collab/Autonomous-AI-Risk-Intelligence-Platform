from dataclasses import asdict

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ml.intelligence.documents import ingest_text
from ml.intelligence.embeddings import RetrievalIndex
from ml.intelligence.entities import extract_entities, extract_relations
from ml.intelligence.investigation import InvestigationEngine

router = APIRouter(prefix="/intelligence", tags=["intelligence"])
_STORE = []
_INDEX = RetrievalIndex()


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
    _STORE.extend(chunks)
    _INDEX.add(chunks)
    return {"document_id": chunks[0].document_id, "chunks_created": len(chunks)}


@router.post("/investigations")
def investigate(payload: InvestigationRequest):
    result = InvestigationEngine(_STORE, _INDEX).investigate(
        payload.investigation_id, payload.query, payload.top_k
    )
    return asdict(result)


@router.post("/reports")
def report(payload: InvestigationRequest):
    result = InvestigationEngine(_STORE, _INDEX).report(
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
    return {"documents": len({chunk.document_id for chunk in _STORE}), "chunks": len(_STORE)}
