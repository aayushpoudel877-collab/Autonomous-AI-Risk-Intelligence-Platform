import numpy as np
import pytest

torch = pytest.importorskip("torch")
from ml.deep_learning.temporal import TemporalRiskEncoder, encode_sequence

def test_temporal_encoder_returns_embedding():
    model = TemporalRiskEncoder(4, hidden_dim=8)
    result = encode_sequence(model, np.zeros((5, 4)))
    assert 0 <= result.score <= 1
    assert len(result.embedding) == 8
