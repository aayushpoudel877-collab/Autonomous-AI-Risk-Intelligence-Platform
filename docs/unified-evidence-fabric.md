# Unified Evidence Fabric

Phase 16 makes evidence a durable cross-domain contract for AegisMind.

## Unified model

The SQLite-backed EvidenceFabric stores multimodal evidence records, graph nodes and edges, evidence-to-node provenance relationships, and temporal events. Stable evidence identifiers are shared across retrieval, graph reasoning, provenance, and adaptive investigations.

## API behavior

Document and multimodal evidence ingestion registers records in the fabric. Knowledge graph writes use the same fabric, and adaptive investigations load graph, temporal, and provenance context from it.

The existing adaptive request fields events and provenance_links remain accepted for compatibility. Supplied events are persisted, and supplied provenance links are incorporated into the shared graph when possible.

## Persistence

Set AEGISMIND_EVIDENCE_DB to choose the SQLite path. The default is data/evidence_fabric.db.

This is a durable local implementation. A later production phase can replace the storage adapter with PostgreSQL without changing the evidence contract.

## Guarantees

- Stable evidence IDs are preserved across services.
- Graph and provenance state survives API restarts.
- Temporal events are persisted once and reused by investigations.
- Existing knowledge and intelligence routes remain available.
- Adaptive planning can consume context created by another API route.

## Limitations

SQLite is still a local persistence layer rather than a distributed graph or ANN database. Citation synthesis remains deterministic and retrieval-grounded rather than an LLM claim generator.
