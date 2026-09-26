from ml.data.generator import DatasetConfig,generate_risk_dataset
from ml.models.classical import RiskClassifier

def train_baseline(rows=5000):
    model=RiskClassifier(); metrics=model.fit(generate_risk_dataset(DatasetConfig(rows=rows))); return model,metrics
if __name__=="__main__": print(train_baseline()[1])
