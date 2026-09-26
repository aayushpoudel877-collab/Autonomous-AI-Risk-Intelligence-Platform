from pathlib import Path
import numpy as np
from ml.data.generator import DatasetConfig, generate_dataset
from ml.deep_learning.mlp import train_mlp

def train_baseline(output_dir: str = "data/synthetic", epochs: int = 20):
    frame = generate_dataset(DatasetConfig(rows=1000, seed=42))
    features = ["baseline_signal", "volatility", "event_rate", "text_signal", "image_signal", "trend"]
    X = frame[features].to_numpy(dtype=float)
    y = frame["risk_target"].to_numpy(dtype=float)
    model, result = train_mlp(X, y, epochs=epochs)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    np.save(Path(output_dir) / "mlp_training_loss.npy", np.array([result.final_loss]))
    return model, result
