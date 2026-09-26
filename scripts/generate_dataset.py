from pathlib import Path
from ml.data.generator import DatasetConfig,save_dataset

if __name__=="__main__":
    out=Path("data/synthetic/risk_events.csv")
    out.parent.mkdir(parents=True,exist_ok=True)
    save_dataset(str(out),DatasetConfig(rows=5000,seed=42))
    print(f"generated {out}")
