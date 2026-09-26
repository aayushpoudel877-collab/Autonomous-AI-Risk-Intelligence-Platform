# Architecture

AegisMind separates ingestion, modeling, fusion, serving, and presentation concerns.

## Runtime flow

1. Data enters through validated source adapters.
2. Feature pipelines normalize heterogeneous signals.
3. Models generate modality-specific scores.
4. Fusion combines supported signals into a normalized risk score.
5. The risk engine produces decision-support state and confidence.
6. Explainability exposes contributing signals and caveats.
7. FastAPI serves analysis endpoints to the dashboard.
8. Monitoring tracks model behavior over time.

Risk outputs are analytical signals and should remain subject to human review.
