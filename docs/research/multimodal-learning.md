# Multimodal Learning

## Current architecture

The platform now supports three representation paths:

- tabular signals through the classical and MLP models
- temporal sequences through the GRU encoder
- text and image embeddings through optional transformer/ResNet encoders

LearnedModalityAttention provides a deterministic attention-style fusion layer while the research roadmap can later replace its scoring rule with learned cross-modal attention.

## Research questions

1. Does learned attention improve calibration over fixed fusion weights?
2. How does missing-modality handling affect risk stability?
3. Which modality combinations provide the largest incremental information?
4. Can temporal context reduce false alarms without suppressing rare events?

All results should be evaluated on held-out data and reported with uncertainty.
