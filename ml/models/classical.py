from dataclasses import dataclass
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score,f1_score,roc_auc_score
from sklearn.model_selection import train_test_split
FEATURES=["baseline_signal","volatility","event_rate","text_signal","image_signal","trend"]
@dataclass
class Evaluation:
    accuracy:float
    f1:float
    roc_auc:float
class RiskClassifier:
    def __init__(self,random_state=42): self.model=RandomForestClassifier(n_estimators=200,max_depth=8,random_state=random_state,class_weight="balanced")
    def fit(self,df):
        Xtr,Xte,ytr,yte=train_test_split(df[FEATURES],df["risk_target"],test_size=.2,random_state=42,stratify=df["risk_target"])
        self.model.fit(Xtr,ytr); pred=self.model.predict(Xte); proba=self.model.predict_proba(Xte)[:,1]
        return Evaluation(accuracy_score(yte,pred),f1_score(yte,pred),roc_auc_score(yte,proba))
    def predict_proba(self,df): return self.model.predict_proba(df[FEATURES])[:,1]
