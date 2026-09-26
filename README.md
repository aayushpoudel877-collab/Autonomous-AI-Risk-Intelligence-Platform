# AegisMind — Autonomous AI Risk Intelligence Platform

A research-oriented, end-to-end platform for multimodal risk intelligence, combining classical ML, deep learning, anomaly detection, forecasting, NLP, computer vision, attention-based fusion, explainability, persistence and operational monitoring.

## Current architecture

Data -> validation -> classical ML / MLP / GRU -> optional NLP + vision encoders -> modality attention -> risk engine -> explainability -> PostgreSQL/SQLite persistence -> telemetry -> API/dashboard.

## Capabilities

- Synthetic risk-data generation and validation
- Random Forest classification and Isolation Forest anomaly detection
- Moving-average forecasting baseline
- PyTorch MLP and GRU temporal encoder
- Optional DistilBERT text embeddings
- Optional ResNet18 visual embeddings
- Attention-style multimodal fusion
- Calibration metrics: Brier score, ECE and reliability curves
- Population Stability Index drift detection
- Model registry and inference telemetry
- SQLAlchemy persistence with SQLite by default and PostgreSQL through DATABASE_URL
- Celery/Redis worker foundation
- FastAPI APIs and React/TypeScript dashboard
- Explainability, model-card and responsible-use documentation
- Automated tests and GitHub Actions CI

## Quickstart

    pip install -e ".[dev]"
    uvicorn backend.app.main:app --reload

Open /docs for interactive API documentation.

For deep learning:

    pip install -e ".[deep-learning]"

For NLP or vision:

    pip install -e ".[nlp]"
    pip install -e ".[vision]"

For worker infrastructure:

    pip install -e ".[workers]"

## Research direction

The next stages are planned around learned cross-modal attention, stronger sequence models, model comparison, experiment tracking, drift-aware retraining, Prometheus/OpenTelemetry integration, Kubernetes deployment, security hardening and reproducible benchmark suites.

This repository is a research/engineering system. Risk scores are model outputs, not facts or causal conclusions, and high-impact decisions require appropriate human review and domain-specific validation.
