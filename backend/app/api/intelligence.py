from fastapi import APIRouter
from pydantic import BaseModel,Field
from ml.intelligence.documents import ingest_text
from ml.intelligence.investigation import InvestigationEngine

router=APIRouter(prefix="/intelligence",tags=["intelligence"])
_STORE=[]

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
    _STORE.extend(chunks)
    return {"document_id":chunks[0].document_id,"chunks_created":len(chunks)}

@router.post("/investigations")
def investigate(payload:InvestigationRequest):
    result=InvestigationEngine(_STORE).investigate(payload.investigation_id,payload.query,payload.top_k)
    return result

@router.get("/documents")
def document_stats():
    return {"documents":len({c.document_id for c in _STORE}),"chunks":len(_STORE)}
