from dataclasses import dataclass
import numpy as np

try:
    import torch
    from torch import nn
except ImportError:
    torch = None
    nn = None

@dataclass(frozen=True)
class SequenceOutput:
    score: float
    embedding: list[float]

if nn is not None:
    class TemporalRiskEncoder(nn.Module):
        def __init__(self, input_dim: int, hidden_dim: int = 32, layers: int = 1):
            super().__init__()
            self.gru = nn.GRU(input_dim, hidden_dim, num_layers=layers, batch_first=True)
            self.head = nn.Sequential(nn.Linear(hidden_dim, 16), nn.ReLU(), nn.Linear(16, 1), nn.Sigmoid())

        def forward(self, x):
            sequence, _ = self.gru(x)
            embedding = sequence[:, -1, :]
            return self.head(embedding).squeeze(-1), embedding
else:
    class TemporalRiskEncoder:
        def __init__(self, *args, **kwargs):
            raise ImportError("PyTorch is required. Install aegismind[deep-learning].")

def encode_sequence(model, sequence: np.ndarray) -> SequenceOutput:
    if torch is None:
        raise ImportError("PyTorch is required. Install aegismind[deep-learning].")
    model.eval()
    with torch.no_grad():
        x = torch.tensor(sequence, dtype=torch.float32).unsqueeze(0)
        score, embedding = model(x)
    return SequenceOutput(float(score.item()), embedding.squeeze(0).cpu().numpy().round(6).tolist())
