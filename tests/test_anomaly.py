from ml.data.generator import generate_risk_dataset
from ml.models.anomaly import RiskAnomalyDetector

def test_anomaly_detector_returns_boolean_flags():
    df=generate_risk_dataset(); flags=RiskAnomalyDetector().fit(df).predict(df.head(25)); assert len(flags)==25 and flags.dtype==bool
