from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True)
class EvidenceLink:
    evidence_id: str
    node_id: str
    relation: str
    confidence: float
    created_at: str

def link_evidence_to_node(evidence_id, node_id, relation="supports", confidence=1.0):
    return EvidenceLink(evidence_id, node_id, relation,
                        max(0.0, min(1.0, float(confidence))),
                        datetime.now(timezone.utc).isoformat())
