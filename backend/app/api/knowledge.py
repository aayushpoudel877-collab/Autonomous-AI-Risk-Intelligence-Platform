from fastapi import APIRouter
from pydantic import BaseModel, Field
from ml.intelligence.evidence_fabric import EvidenceFabric
from ml.intelligence.knowledge_graph import Node, Edge
from ml.intelligence.temporal import temporal_window, build_timeline

router = APIRouter(prefix="/knowledge", tags=["knowledge"])
FABRIC = EvidenceFabric()

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

class EventRequest(BaseModel):
    id: str
    timestamp: str
    payload: dict = Field(default_factory=dict)

@router.post("/nodes")
def add_node(payload: NodeRequest):
    FABRIC.add_node(Node(**payload.model_dump()))
    return payload

@router.post("/edges")
def add_edge(payload: EdgeRequest):
    FABRIC.add_edge(Edge(**payload.model_dump()))
    return payload

@router.post("/evidence-links")
def add_evidence_link(payload: EvidenceLinkRequest):
    link = FABRIC.add_provenance(payload.evidence_id, payload.node_id, payload.relation, payload.confidence)
    return {"link": link.__dict__, "subgraph": FABRIC.graph().subgraph(payload.node_id, depth=1)}

@router.post("/events")
def add_event(payload: EventRequest):
    event = {"id": payload.id, "timestamp": payload.timestamp, **payload.payload}
    FABRIC.add_event(event)
    return event

@router.get("/subgraph/{node_id}")
def subgraph(node_id: str, depth: int = 1):
    return FABRIC.graph().subgraph(node_id, depth)

@router.post("/timeline")
def timeline(payload: TimelineRequest):
    for event in payload.events:
        FABRIC.add_event(event)
    return temporal_window(payload.events, payload.start, payload.end)

@router.post("/timeline/sort")
def sort_timeline(events: list[dict]):
    for event in events:
        FABRIC.add_event(event)
    return build_timeline(events)

@router.get("/fabric/stats")
def fabric_stats():
    return FABRIC.stats()
