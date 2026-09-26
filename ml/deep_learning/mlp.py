from dataclasses import dataclass
import numpy as np

try:
    import torch
    from torch import nn
except ImportError:
    torch = None
    nn = None

@dataclass(frozen=True)
class TrainingResult:
    epochs: int
    final_loss: float

def _require_torch():
    if torch is None:
        raise ImportError("PyTorch is required for deep-learning training. Install aegismind[deep-learning].")

if nn is not None:
    class RiskMLP(nn.Module):
        def __init__(self, input_dim: int, hidden_dim: int = 32):
            super().__init__()
            self.network = nn.Sequential(
                nn.Linear(input_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.1),
                nn.Linear(hidden_dim, hidden_dim // 2),
                nn.ReLU(),
                nn.Linear(hidden_dim // 2, 1),
                nn.Sigmoid(),
            )

        def forward(self, x):
            return self.network(x).squeeze(-1)
else:
    class RiskMLP:
        def __init__(self, *args, **kwargs):
            _require_torch()

def train_mlp(X: np.ndarray, y: np.ndarray, epochs: int = 20, lr: float = 1e-3, seed: int = 42):
    _require_torch()
    torch.manual_seed(seed)
    X_t = torch.tensor(X, dtype=torch.float32)
    y_t = torch.tensor(y, dtype=torch.float32)
    model = RiskMLP(X.shape[1])
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    loss_fn = nn.BCELoss()
    last = 0.0
    model.train()
    for _ in range(epochs):
        optimizer.zero_grad()
        loss = loss_fn(model(X_t), y_t)
        loss.backward()
        optimizer.step()
        last = float(loss.detach().cpu())
    return model, TrainingResult(epochs=epochs, final_loss=round(last, 6))
