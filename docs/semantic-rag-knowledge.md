# Semantic Retrieval, Knowledge Graph and Temporal Reasoning

This phase adds three research foundations:

- semantic-style retrieval behind a stable interface
- an in-memory knowledge graph for entities and relationships
- temporal filtering and event timelines

The retrieval implementation remains dependency-light. It can later be replaced by embedding models and a vector database without changing the investigation API contract.

Knowledge graph edges carry an explicit confidence value. Temporal reasoning is based on normalized timestamps and preserves event order.

## Evidence principle

A retrieved passage is evidence for investigation, not proof of causation. Claims should retain links to supporting evidence, and consequential actions should remain subject to appropriate human review.

## Upgrade path

1. Sentence-transformer embeddings
2. Persistent vector store
3. Entity/relation extraction
4. Graph database adapter
5. Temporal event graph
6. Multimodal evidence nodes
7. Citation-aware synthesis
