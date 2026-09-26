# Intelligence Layer

AegisMind now has an evidence-oriented intelligence foundation.

## Flow

Document -> chunking -> retrieval -> evidence -> investigation findings.

The current retriever is intentionally lightweight and deterministic: it uses normalized term overlap rather than requiring an external vector database or model download.

## Investigation contract

Investigations return evidence records containing a chunk identifier, source, text and relevance score. Findings are deliberately advisory. Retrieval is not proof of causation, and the system should not make consequential decisions or take high-impact actions without appropriate human review.

## Next research upgrades

- embedding-based semantic retrieval
- persistent vector index
- document parsers for PDF/HTML/office formats
- evidence confidence and provenance graphs
- multimodal retrieval
- LLM synthesis with citation enforcement
- event-to-document correlation
- knowledge graph and temporal reasoning
