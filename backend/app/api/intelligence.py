from fastapi import APIRouter
from pydantic import BaseModel,Field
from ml.intelligence.documents import ingest_text
from ml.intelligence.investigation import InvestigationEngine
from ml.intelligence.embeddings import RetrievalIndex
from ml.intelligence.entities import extract_entities,extract_relations

router=APIRouter(prefix="/intelligence",tags=["intelligence"])
_STORE=[]; _INDEX=RetrievalIndex()

class DocumentRequest(BaseModel):
    text:str=Field(min_length=1)
    source:str="user-provided"

class InvestigationRequest(BaseModel):
    investigation_id:str
    query:str=Field(min_length=1)
    top_k:int=Field(default=5,ge=1,le=20)

@router.post("/documents")
def add_document(payload:DocumentRequest):
    chunks=ingest_text(payload.text,payload.source)
    _STORE.extend(chunks); _INDEX.add(chunks)
    return {"document_id":chunks[0].document_id,"chunks_created":len(chunks)}

@router.post("/investigations")
def investigate(payload:InvestigationRequest):
    return InvestigationEngine(_STORE,_INDEX).investigate(payload.investigation_id,payload.query,payload.top_k)

@router.post("/reports")
def report(payload:InvestigationRequest):
    return InvestigationEngine(_STORE,_INDEX).report(payload.investigation_id,payload.query,payload.top_k)

@router.post("/entities")
def entities(payload:DocumentRequest):
    return {"entities":[e.__dict__ for e in extract_entities(payload.text)],"relations":[r.__dict__ for r in extract_relations(payload.text)]}

@router.get("/documents")
def document_stats():
    return {"documents":len({c.document_id for c in _STORE}),"chunks":len(_STORE)}
