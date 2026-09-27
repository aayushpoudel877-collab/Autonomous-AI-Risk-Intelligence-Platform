from fastapi import APIRouter
from pydantic import BaseModel, Field
from ml.intelligence.knowledge_graph import KnowledgeGraph, Node, Edge
from ml.intelligence.provenance import link_evidence_to_node
from ml.intelligence.temporal import temporal_window, build_timeline

router = APIRouter(prefix="/knowledge", tags=["knowledge"])
GRAPH = KnowledgeGraph()
EVENTS = []

class NodeRequest(BaseModel):
    node_id: str
    node_type: str
    label: str

class EdgeRequest(BaseModel):
    source: str
    relation: str
    target: str
    confidence: float = Field(default=1.0, ge=0, le=1)

class EvidenceLinkRequest(BaseModel):
    evidence_id: str
    node_id: str
    relation: str = "supports"
    confidence: float = Field(default=1.0, ge=0, le=1)

class TimelineRequest(BaseModel):
    events: list[dict]
    start: str
    end: str

@router.post("/nodes")
def add_node(payload: NodeRequest):
    GRAPH.add_node(Node(**payload.model_dump()))
    return payload

@router.post("/edges")
def add_edge(payload: EdgeRequest):
    GRAPH.add_edge(Edge(**payload.model_dump()))
    return payload

@router.post("/evidence-links")
def add_evidence_link(payload: EvidenceLinkRequest):
    link = link_evidence_to_node(payload.evidence_id, payload.node_id, payload.relation, payload.confidence)
    GRAPH.add_node(Node(payload.evidence_id, "evidence", payload.evidence_id))
    GRAPH.add_edge(Edge(payload.evidence_id, payload.relation, payload.node_id, payload.confidence))
    return {"link": link.__dict__, "subgraph": GRAPH.subgraph(payload.node_id, depth=1)}

@router.get("/subgraph/{node_id}")
def subgraph(node_id: str, depth: int = 1):
    return GRAPH.subgraph(node_id, depth)

@router.post("/timeline")
def timeline(payload: TimelineRequest):
    return temporal_window(payload.events, payload.start, payload.end)

@router.post("/timeline/sort")
def sort_timeline(events: list[dict]):
    return build_timeline(events)
