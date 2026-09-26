import numpy as np
import pytest

torch = pytest.importorskip("torch")
from ml.deep_learning.mlp import RiskMLP, train_mlp

def test_mlp_forward_shape():
    model = RiskMLP(6)
    out = model(torch.zeros((4, 6)))
    assert tuple(out.shape) == (4,)
    assert torch.all((out >= 0) & (out <= 1))

def test_mlp_training_reduces_loss():
    X = np.array([[0,0],[0,1],[1,0],[1,1]], dtype=float)
    y = np.array([0,0,0,1], dtype=float)
    _, result = train_mlp(X, y, epochs=30)
    assert result.final_loss < 1.0
