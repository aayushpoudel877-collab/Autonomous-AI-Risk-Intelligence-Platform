# Citation-Aware Evidence Synthesis

AegisMind now separates retrieval from synthesis. Retrieved evidence is transformed into explicit grounded claims, and every claim carries one or more citation records pointing back to the evidence item and source.

## Pipeline

retrieval -> evidence IDs -> grounded claims -> citations -> report/API

## Guarantees

- A generated claim cannot be considered grounded unless it has a citation.
- Citation records preserve the evidence ID and source.
- Validation reports missing or incomplete citations.
- Reports expose claim-level citations rather than only a flat evidence list.

## API

- POST /api/v1/intelligence/synthesis
- POST /api/v1/intelligence/reports

## Important limitation

The current synthesis is deterministic and intentionally conservative. It does not claim that retrieved evidence proves causality or truth, and retrieval similarity is not a calibrated probability. A future generator can implement richer language synthesis behind the same citation contract.
