# Observability

AegisMind now records lightweight inference telemetry in-process.

Metrics exposed at GET /api/v1/monitoring/metrics:

- request count
- error count and error rate
- mean inference latency
- mean risk score

This is intentionally framework-neutral. Production deployments can export these values to Prometheus/OpenTelemetry and visualize them in Grafana.

Telemetry should be treated as operational metadata, not a substitute for model evaluation.
