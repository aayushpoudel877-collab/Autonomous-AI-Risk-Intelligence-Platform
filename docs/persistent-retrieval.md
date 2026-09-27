# Persistent Retrieval and Learned Embeddings

AegisMind retrieval now supports durable SQLite-backed vector storage and an optional learned embedding provider.

## Durable vector storage

SQLiteVectorStore stores document chunks, provenance metadata, normalized vectors and embedding dimensions in SQLite. The default API location is data/vector_store.db; set AEGISMIND_VECTOR_DB to use another path.

The store can be reopened by another process without rebuilding the index from source documents.

## Embedding providers

- HashEmbeddingProvider is the deterministic, dependency-light baseline.
- SentenceTransformerProvider is an optional learned provider using sentence-transformers.

Install the learned provider with: pip install -e ".[embeddings]"

The API deliberately defaults to the hash provider so the base CI and local development path remain lightweight and offline-friendly.

## Retrieval contract

Investigation results now identify persistent-embedding retrieval when evidence comes from the durable vector store. Retrieval similarity is evidence-ranking metadata, not proof of causality.

## Configuration

AEGISMIND_VECTOR_DB=data/vector_store.db

The vector-store abstraction is intentionally provider-agnostic so a later deployment can replace SQLite with a managed vector database without changing investigation semantics.