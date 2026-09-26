# Model Card

## Scope
The baseline classifier and anomaly detector are engineering baselines for the AegisMind research platform.

## Intended use
Benchmarking multimodal risk-scoring pipelines and studying explainability, drift, and forecasting.

## Limitations
Synthetic data does not represent a real population. Scores are not causal conclusions and should not be used as the sole basis for consequential decisions.

## Evaluation
The training pipeline reports accuracy, F1, and ROC-AUC. Forecasting reports MAE and RMSE.
