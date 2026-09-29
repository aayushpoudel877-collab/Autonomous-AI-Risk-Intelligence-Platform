# Adaptive Investigation Planning

Phase 14 upgrades the bounded orchestration layer into an evidence-aware adaptive loop.

## Flow

1. Start from an investigation goal.
2. Retrieve evidence for the current query.
3. Inspect retrieved evidence for objective coverage.
4. Identify missing aspects such as cause, impact, or timeline.
5. Generate the next query from the missing objective and, when available, an extracted entity.
6. Retrieve again and deduplicate evidence by chunk ID.
7. Record the decision, query, reason, and newly discovered evidence IDs.
8. Stop when objectives are satisfied or the configured step budget is exhausted.

## Safety and correctness boundaries

The planner is deterministic and bounded. It does not claim that retrieved text is verified truth, causation, or a calibrated probability. Objective matching is a retrieval heuristic based on evidence text and should be replaced or supplemented with domain-specific evaluators for production use.

The previous `/investigations/autonomous` endpoint remains unchanged for compatibility. The new `/investigations/adaptive` endpoint exposes the adaptive behavior explicitly.

## API

`POST /api/v1/intelligence/investigations/adaptive`

Request fields:
- `investigation_id`
- `query`
- `top_k`
- `max_steps`
- `min_evidence`
- `required_aspects`

The response includes the investigation trace plus `decisions`, where every adaptive decision records its selected objective, reason, query, and newly added evidence IDs.

## Known limitations

- Aspect coverage currently uses deterministic keyword heuristics.
- Entity expansion uses the existing lightweight entity extractor.
- Knowledge-graph traversal and temporal-gap analysis are integration points for a later phase.
- The vector store remains a SQLite full-scan prototype.
