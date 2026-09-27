# Multimodal Evidence Layer

AegisMind now accepts text, tabular records, and image feature descriptors through one persistent evidence store.

All modalities use the common DocumentChunk persistence contract while retaining modality-specific metadata.

Text uses document chunks. Tabular data preserves the original record and numeric-field metadata. Images currently accept feature descriptors rather than raw image files; a future vision encoder can replace the descriptor vector without changing the evidence contract.

The default vector provider remains deterministic hashing. Learned multimodal encoders can be introduced behind the same provider boundary.

Evidence links identify the evidence item, graph node, relationship and confidence. Evidence is contextual support, not automatic proof of causality.

API:
- POST /api/v1/intelligence/evidence/tabular
- POST /api/v1/intelligence/evidence/image-descriptor
- POST /api/v1/intelligence/investigations
- POST /api/v1/intelligence/reports
