# Phase 15 — Graph, Temporal, and Provenance-Aware Investigation

Phase 15 connects adaptive planning to three existing AegisMind intelligence primitives.

## Graph awareness
The planner can inspect knowledge-graph neighbors of entities mentioned by retrieved evidence and generate a bounded follow-up query for a related node.

## Temporal awareness
The planner can consume timestamped events, detect gaps between adjacent events, and request timeline-focused evidence when a temporal gap exists.

## Provenance awareness
The planner tracks which retrieved evidence IDs have provenance links and can request additional source evidence when the configured provenance target is not met.

## Objective gating
An adaptive investigation can require:
- a minimum number of evidence items;
- specific evidence aspects;
- a minimum number of provenance-linked evidence items;
- graph context;
- temporal context.

All gates are explicit configuration. The system does not infer that retrieval relevance proves causality or factual truth.

## Compatibility

The original autonomous endpoint remains unchanged. The adaptive endpoint gains optional context fields, so existing requests remain valid.

## Limitations

Graph node matching currently uses normalized entity labels, temporal reasoning is based on timestamp gaps, and provenance links are supplied as investigation context rather than persisted as a unified provenance store. These are deliberate integration points for a later production-grade evidence fabric.
