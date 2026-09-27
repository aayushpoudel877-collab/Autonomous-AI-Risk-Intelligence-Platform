from dataclasses import dataclass, asdict
from hashlib import sha256
import json
import numpy as np
from ml.intelligence.documents import DocumentChunk
from ml.intelligence.vector_store import SQLiteVectorStore

@dataclass(frozen=True)
class MultimodalEvidence:
    evidence_id: str
    modality: str
    source: str
    content: str
    metadata: dict
    vector: list[float]
    def as_dict(self):
        return asdict(self)

def _stable_vector(values, dimensions):
    vector = np.zeros(dimensions, dtype=float)
    for value in values:
        digest = sha256(str(value).encode("utf-8")).digest()
        vector[int.from_bytes(digest[:8], "big") % dimensions] += 1.0
    norm = np.linalg.norm(vector)
    return (vector / norm if norm else vector).tolist()

class MultimodalEvidenceStore:
    def __init__(self, vector_store: SQLiteVectorStore):
        self.store = vector_store
        self.dimensions = vector_store.provider.dimensions

    def add_text(self, text, source="unknown", metadata=None):
        chunks = [DocumentChunk(
            document_id=sha256(text.encode("utf-8")).hexdigest()[:16],
            chunk_id=sha256((source + text).encode("utf-8")).hexdigest()[:24],
            text=text, source=source,
            metadata={**(metadata or {}), "modality": "text"},
        )]
        self.store.add(chunks)
        return [self._from_chunk(chunk) for chunk in chunks]

    def add_image_descriptor(self, descriptor, source="unknown", metadata=None):
        payload = json.dumps(descriptor, sort_keys=True)
        evidence = MultimodalEvidence(
            sha256((source + payload).encode("utf-8")).hexdigest()[:24],
            "image", source, "Image feature descriptor",
            {**(metadata or {}), "descriptor": descriptor},
            _stable_vector(descriptor.values(), self.dimensions),
        )
        self.store.add([DocumentChunk(
            document_id=evidence.evidence_id[:16], chunk_id=evidence.evidence_id,
            text=payload, source=source,
            metadata={"modality": "image", **evidence.metadata},
        )])
        return evidence

    def add_tabular(self, record, source="unknown", metadata=None):
        numeric = [float(v) for v in record.values() if isinstance(v, (int, float)) and not isinstance(v, bool)]
        labels = [f"{k}={v}" for k, v in record.items()]
        content = json.dumps(record, sort_keys=True)
        evidence = MultimodalEvidence(
            sha256((source + content).encode("utf-8")).hexdigest()[:24],
            "tabular", source, content,
            {**(metadata or {}), "numeric_fields": len(numeric)},
            _stable_vector(numeric + labels, self.dimensions),
        )
        self.store.add([DocumentChunk(
            document_id=evidence.evidence_id[:16], chunk_id=evidence.evidence_id,
            text=content, source=source,
            metadata={"modality": "tabular", **evidence.metadata},
        )])
        return evidence

    def _from_chunk(self, chunk):
        return MultimodalEvidence(
            chunk.chunk_id, chunk.metadata.get("modality", "text"),
            chunk.source, chunk.text, chunk.metadata, [],
        )
