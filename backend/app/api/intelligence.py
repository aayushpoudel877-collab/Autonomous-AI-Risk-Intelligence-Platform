import os
from dataclasses import asdict
from fastapi import APIRouter
from pydantic import BaseModel, Field

from ml.intelligence.citations import synthesize_investigation, validate_citations
from ml.intelligence.documents import ingest_text
from ml.intelligence.embeddings import HashEmbeddingProvider
from ml.intelligence.entities import extract_entities, extract_relations
from ml.intelligence.evidence_fabric import EvidenceFabric, EvidenceRecord
from ml.intelligence.investigation import InvestigationEngine
from ml.intelligence.multimodal import MultimodalEvidenceStore
from ml.intelligence.orchestration import AutonomousInvestigator, InvestigationObjective
from ml.intelligence.vector_store import SQLiteVectorStore

router = APIRouter(prefix="/intelligence", tags=["intelligence"])
_VECTOR_DB = os.getenv("AEGISMIND_VECTOR_DB", "data/vector_store.db")
_PROVIDER = HashEmbeddingProvider()
_STORE = SQLiteVectorStore(_VECTOR_DB, _PROVIDER)
_MULTIMODAL = MultimodalEvidenceStore(_STORE)
_FABRIC = EvidenceFabric()

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
    required_aspects: list[str] = Field(
        default_factory=lambda: ["cause", "impact", "timeline"], min_length=1, max_length=6
    )
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

def _register_chunk(chunk):
    _FABRIC.add_evidence(EvidenceRecord(
        evidence_id=chunk.chunk_id,
        modality=str(chunk.metadata.get("modality", "text")),
        source=chunk.source,
        content=chunk.text,
        metadata=chunk.metadata,
        document_id=chunk.document_id,
    ))

@router.post("/documents")
def add_document(payload: DocumentRequest):
    chunks = ingest_text(payload.text, payload.source)
    _STORE.add(chunks)
    for chunk in chunks:
        _register_chunk(chunk)
    return {"document_id": chunks[0].document_id, "chunks_created": len(chunks)}

@router.post("/evidence/tabular")
def add_tabular(payload: TabularRequest):
    result = _MULTIMODAL.add_tabular(payload.record, payload.source)
    _FABRIC.add_evidence(EvidenceRecord(
        evidence_id=result.evidence_id, modality=result.modality, source=result.source,
        content=result.content, metadata=result.metadata, vector_ref=result.evidence_id,
    ))
    return asdict(result)

@router.post("/evidence/image-descriptor")
def add_image_descriptor(payload: ImageDescriptorRequest):
    result = _MULTIMODAL.add_image_descriptor(payload.descriptor, payload.source)
    _FABRIC.add_evidence(EvidenceRecord(
        evidence_id=result.evidence_id, modality=result.modality, source=result.source,
        content=result.content, metadata=result.metadata, vector_ref=result.evidence_id,
    ))
    return asdict(result)

@router.post("/investigations")
def investigate(payload: InvestigationRequest):
    result = InvestigationEngine(persistent_index=_STORE).investigate(
        payload.investigation_id, payload.query, payload.top_k
    )
    return asdict(result)

@router.post("/investigations/autonomous")
def autonomous_investigation(payload: AutonomousInvestigationRequest):
    engine = InvestigationEngine(persistent_index=_STORE)
    trace = AutonomousInvestigator(engine).run(
        payload.investigation_id, payload.query, payload.max_steps, payload.top_k
    )
    return trace.as_dict()

@router.post("/investigations/adaptive")
def adaptive_investigation(payload: AdaptiveInvestigationRequest):
    for event in payload.events:
        _FABRIC.add_event(event)
    for link in payload.provenance_links:
        evidence_id = str(link.get("evidence_id", ""))
        if not evidence_id or _FABRIC.get_evidence(evidence_id) is None:
            continue
        node_id = str(link.get("node_id") or f"investigation:{payload.investigation_id}")
        _FABRIC.add_provenance(
            evidence_id, node_id, str(link.get("relation", "supports")),
            float(link.get("confidence", 1.0)),
        )

    context = _FABRIC.context()
    objective = InvestigationObjective(
        name=f"adaptive:{payload.investigation_id}",
        required_aspects=tuple(payload.required_aspects),
        min_evidence=payload.min_evidence,
        min_provenance=payload.min_provenance,
        require_graph_context=payload.require_graph_context,
        require_temporal_context=payload.require_temporal_context,
    )
    trace = AutonomousInvestigator(InvestigationEngine(persistent_index=_STORE)).run_adaptive(
        payload.investigation_id,
        payload.query,
        payload.max_steps,
        payload.top_k,
        objective,
        context["graph"],
        context["events"],
        context["provenance_links"],
    )
    return trace.as_dict()

@router.post("/synthesis")
def synthesis(payload: InvestigationRequest):
    investigation = InvestigationEngine(persistent_index=_STORE).investigate(
        payload.investigation_id, payload.query, payload.top_k
    )
    result = synthesize_investigation(investigation)
    return {
        "query": result.query,
        "claims": [asdict(c) for c in result.claims],
        "generated_at": result.generated_at,
        "limitations": result.limitations,
        "citation_errors": validate_citations(result),
    }

@router.post("/reports")
def report(payload: InvestigationRequest):
    result = InvestigationEngine(persistent_index=_STORE).report(
        payload.investigation_id, payload.query, payload.top_k
    )
    return asdict(result)

@router.post("/entities")
def entities(payload: DocumentRequest):
    return {
        "entities": [asdict(e) for e in extract_entities(payload.text)],
        "relations": [asdict(r) for r in extract_relations(payload.text)],
    }

@router.get("/documents")
def document_stats():
    return {"documents": _STORE.document_count(), "chunks": _STORE.count()}

@router.get("/fabric")
def fabric_stats():
    return _FABRIC.stats()
