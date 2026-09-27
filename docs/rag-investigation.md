# RAG and Investigation Upgrade

AegisMind now exposes a pluggable retrieval abstraction.

## Retrieval

EmbeddingProvider defines the contract for future sentence-transformer or other embedding models. The default hash embedding is deterministic and dependency-light; it is an engineering fallback, not a semantic language model.

RetrievalIndex keeps chunk vectors in memory and performs normalized dot-product similarity.

## Investigation reports

Investigations can produce structured reports containing the investigation identifier, query, retrieved evidence, evidence scores, limitations and generation timestamp.

The report layer intentionally does not invent unsupported conclusions.

## Entity extraction

A lightweight entity and relation extractor provides a stable contract for future NLP models. It can later be replaced by NER and relation-extraction models without changing the API shape.

## Next upgrade

Persistent vector storage, real embedding models, multimodal retrieval, citation-aware synthesis and graph-backed evidence provenance.
