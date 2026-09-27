from ml.intelligence.embeddings import HashEmbeddingProvider
from ml.intelligence.multimodal import MultimodalEvidenceStore
from ml.intelligence.vector_store import SQLiteVectorStore
from ml.intelligence.provenance import link_evidence_to_node

def test_multimodal_text_and_tabular_evidence(tmp_path):
    store = SQLiteVectorStore(tmp_path / "multi.db", HashEmbeddingProvider(dimensions=32))
    evidence = MultimodalEvidenceStore(store)
    text = evidence.add_text("Router packet loss increased.", "incident")
    table = evidence.add_tabular({"packet_loss": 0.82, "latency": 120}, "telemetry")
    assert text[0].modality == "text"
    assert table.modality == "tabular"
    assert store.count() == 2

def test_image_descriptor_is_persisted(tmp_path):
    store = SQLiteVectorStore(tmp_path / "multi.db", HashEmbeddingProvider(dimensions=32))
    evidence = MultimodalEvidenceStore(store)
    image = evidence.add_image_descriptor({"edge_density": 0.8, "brightness": 0.2}, "camera")
    assert image.modality == "image"
    assert store.count() == 1

def test_provenance_link():
    link = link_evidence_to_node("ev-1", "node-1", confidence=0.7)
    assert link.evidence_id == "ev-1" and link.confidence == 0.7
