import pandas as pd
from sklearn.ensemble import IsolationForest
FEATURES=["baseline_signal","volatility","event_rate","text_signal","image_signal","trend"]
class RiskAnomalyDetector:
    def __init__(self,contamination=.05,random_state=42): self.model=IsolationForest(contamination=contamination,random_state=random_state,n_estimators=200)
    def fit(self,df): self.model.fit(df[FEATURES]); return self
    def score_samples(self,df):
        raw=-self.model.decision_function(df[FEATURES]); return (raw-raw.min())/(raw.max()-raw.min()+1e-9)
    def predict(self,df): return self.model.predict(df[FEATURES])==-1
