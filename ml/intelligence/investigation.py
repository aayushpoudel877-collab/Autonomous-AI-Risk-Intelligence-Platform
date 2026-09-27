from dataclasses import dataclass, field
from datetime import datetime, timezone

from ml.intelligence.embeddings import RetrievalIndex
from ml.intelligence.reporting import build_report
from ml.intelligence.retrieval import retrieve


@dataclass
class Investigation:
    investigation_id: str
    query: str
    status: str = "open"
    findings: list[str] = field(default_factory=list)
    evidence: list[dict] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class InvestigationEngine:
    def __init__(self, chunks=(), index=None, persistent_index=None):
        self.chunks = list(chunks)
        self.index = index
        self.persistent_index = persistent_index
        if self.index and self.chunks and not self.index.chunks:
            self.index.add(self.chunks)

    def investigate(self, investigation_id, query, top_k=5):
        if self.persistent_index:
            hits = self.persistent_index.search(query, top_k)
            method = "persistent-embedding"
        elif self.index:
            hits = self.index.search(query, top_k)
            method = "embedding"
        else:
            hits = [(e, e.score) for e in retrieve(query, self.chunks, top_k)]
            method = "lexical"
        evidence = [
            {
                "chunk_id": chunk.chunk_id,
                "source": chunk.source,
                "text": chunk.text,
                "score": round(score, 6),
                "method": method,
            }
            for chunk, score in hits
        ]
        finding = "Evidence retrieved for review." if evidence else "No matching evidence was retrieved."
        return Investigation(investigation_id, query, "open", [finding], evidence)

    def report(self, investigation_id, query, top_k=5):
        return build_report(self.investigate(investigation_id, query, top_k))
