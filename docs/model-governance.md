# Model Governance

AegisMind now treats model promotion as a gated lifecycle.

## Candidate lifecycle

1. Train a candidate model.
2. Evaluate held-out performance.
3. Measure calibration error.
4. Measure population drift.
5. Run the promotion gate.
6. Record the decision in an append-only JSONL audit log.
7. Promote only after the required governance review.

Default gates:

- performance metric >= 0.80
- ECE <= 0.10
- PSI < 0.25

These are engineering defaults, not universal safety thresholds. Production thresholds must be validated for the intended domain.

## Retraining

The retraining assessment uses PSI and labels the current distribution as stable, watch, or drifted. A PSI at or above 0.25 requests retraining assessment.

The system deliberately separates detecting drift from automatically deploying a model. Deployment should remain subject to evaluation and appropriate human governance.
