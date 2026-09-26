from dataclasses import dataclass
import numpy as np
import pandas as pd

@dataclass(frozen=True)
class DatasetConfig:
    rows: int = 5000
    seed: int = 42

def generate_risk_dataset(config: DatasetConfig = DatasetConfig()) -> pd.DataFrame:
    rng=np.random.default_rng(config.seed)
    baseline=rng.normal(.45,.16,config.rows).clip(0,1)
    volatility=rng.normal(.35,.18,config.rows).clip(0,1)
    event_rate=rng.poisson(3,config.rows).astype(float)
    text_signal=rng.beta(2,4,config.rows)
    image_signal=rng.beta(2.2,3.8,config.rows)
    trend=np.linspace(0,.25,config.rows)
    anomaly=((volatility>.72)|(event_rate>7)).astype(int)
    risk=(.30*baseline+.22*volatility+.18*(event_rate/10)+.15*text_signal+.10*image_signal+.05*trend).clip(0,1)
    risk=np.clip(risk+anomaly*.12,0,1)
    return pd.DataFrame({"baseline_signal":baseline,"volatility":volatility,"event_rate":event_rate,"text_signal":text_signal,"image_signal":image_signal,"trend":trend,"anomaly":anomaly,"risk_target":(risk>=.62).astype(int),"risk_score":risk})

def save_dataset(path: str, config: DatasetConfig=DatasetConfig()):
    generate_risk_dataset(config).to_csv(path,index=False)
