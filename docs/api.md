# API Contract

## GET /health
Returns service status.

## POST /api/v1/risk/analyze
Accepts a list of normalized signals and returns score, level, confidence, source, and factors.

## POST /api/v1/risk/explain
Returns the risk response together with ranked signal contributions and model caveats.
