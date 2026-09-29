import os
from dataclasses import asdict
from fastapi import APIRouter
from pydantic import BaseModel, Field
from ml.intelligence.documents import ingest_text
from ml.intelligence.embeddings import HashEmbeddingProvider
from ml.intelligence.entities import extract_entities, extract_relations
from ml.intelligence.investigation import InvestigationEngine
from ml.intelligence.multimodal import MultimodalEvidenceStore
from ml.intelligence.vector_store import SQLiteVectorStore
from ml.intelligence.citations import synthesize_investigation, validate_citations
from ml.intelligence.knowledge_graph import KnowledgeGraph
from ml.intelligence.orchestration import AutonomousInvestigator, InvestigationObjective
from ml.intelligence.temporal import build_timeline

router = APIRouter(prefix="/intelligence", tags=["intelligence"])
_VECTOR_DB = os.getenv("AEGISMIND_VECTOR_DB", "data/vector_store.db")
_PROVIDER = HashEmbeddingProvider()
_STORE = SQLiteVectorStore(_VECTOR_DB, _PROVIDER)
_MULTIMODAL = MultimodalEvidenceStore(_STORE)
_GRAPH = KnowledgeGraph()

class DocumentRequest(BaseModel):
    text: str = Field(min_length=1)
    source: str = "user-provided"

class InvestigationRequest(BaseModel):
    investigation_id: str
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)

class AutonomousInvestigationRequest(InvestigationRequest):
    max_steps: int = Field(default=3, ge=1, le=6)

class AdaptiveInvestigationRequest(InvestigationRequest):
    max_steps: int = Field(default=6, ge=1, le=10)
    min_evidence: int = Field(default=3, ge=1, le=50)
    required_aspects: list[str] = Field(default_factory=lambda: ["cause", "impact", "timeline"], min_length=1, max_length=6)
    min_provenance: int = Field(default=0, ge=0, le=50)
    require_graph_context: bool = False
    require_temporal_context: bool = False
    events: list[dict] = Field(default_factory=list)
    provenance_links: list[dict] = Field(default_factory=list)

class TabularRequest(BaseModel):
    record: dict
    source: str = "tabular"

class ImageDescriptorRequest(BaseModel):
    descriptor: dict[str, float]
    source: str = "image"

@router.post("/documents")
def add_document(payload: DocumentRequest):
    chunks = ingest_text(payload.text, payload.source)
    _STORE.add(chunks)
    return {"document_id": chunks[0].document_id, "chunks_created": len(chunks)}

@router.post("/evidence/tabular")
def add_tabular(payload: TabularRequest):
    return asdict(_MULTIMODAL.add_tabular(payload.record, payload.source))

@router.post("/evidence/image-descriptor")
def add_image_descriptor(payload: ImageDescriptorRequest):
    return asdict(_MULTIMODAL.add_image_descriptor(payload.descriptor, payload.source))

@router.post("/investigations")
def investigate(payload: InvestigationRequest):
    result = InvestigationEngine(persistent_index=_STORE).investigate(payload.investigation_id, payload.query, payload.top_k)
    return asdict(result)

@router.post("/investigations/autonomous")
def autonomous_investigation(payload: AutonomousInvestigationRequest):
    engine = InvestigationEngine(persistent_index=_STORE)
    trace = AutonomousInvestigator(engine).run(payload.investigation_id, payload.query, payload.max_steps, payload.top_k)
    return trace.as_dict()

@router.post("/investigations/adaptive")
def adaptive_investigation(payload: AdaptiveInvestigationRequest):
    objective = InvestigationObjective(
        name=f"adaptive:{payload.investigation_id}",
        required_aspects=tuple(payload.required_aspects),
        min_evidence=payload.min_evidence,
        min_provenance=payload.min_provenance,
        require_graph_context=payload.require_graph_context,
        require_temporal_context=payload.require_temporal_context,
    )
    timeline = build_timeline(payload.events) if payload.events else []
    trace = AutonomousInvestigator(InvestigationEngine(persistent_index=_STORE)).run_adaptive(
        payload.investigation_id, payload.query, payload.max_steps, payload.top_k,
        objective, _GRAPH, timeline, payload.provenance_links
    )
    return trace.as_dict()

@router.post("/synthesis")
def synthesis(payload: InvestigationRequest):
    investigation = InvestigationEngine(persistent_index=_STORE).investigate(payload.investigation_id, payload.query, payload.top_k)
    result = synthesize_investigation(investigation)
    return {"query": result.query, "claims": [asdict(c) for c in result.claims], "generated_at": result.generated_at,
            "limitations": result.limitations, "citation_errors": validate_citations(result)}

@router.post("/reports")
def report(payload: InvestigationRequest):
    result = InvestigationEngine(persistent_index=_STORE).report(payload.investigation_id, payload.query, payload.top_k)
    return asdict(result)

@router.post("/entities")
def entities(payload: DocumentRequest):
    return {"entities": [asdict(e) for e in extract_entities(payload.text)], "relations": [asdict(r) for r in extract_relations(payload.text)]}

@router.get("/documents")
def document_stats():
    return {"documents": _STORE.document_count(), "chunks": _STORE.count()}
