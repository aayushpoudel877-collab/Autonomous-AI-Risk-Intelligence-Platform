# Automated Retraining Workflow

The platform separates drift detection, candidate evaluation, and deployment.

1. Monitoring observes production inputs.
2. PSI evaluates distribution change.
3. A retraining assessment creates a candidate-job request when drift crosses the configured threshold.
4. Celery can execute the assessment asynchronously through Redis.
5. The candidate is evaluated for performance, calibration, and drift.
6. The promotion gate records an approve/reject decision.
7. Deployment remains a separately governed operation.

This structure allows future replacement of the lightweight worker with a full training pipeline without coupling detection to deployment.
