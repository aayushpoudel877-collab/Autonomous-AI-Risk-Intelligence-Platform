from ml.fusion.attention import LearnedModalityAttention

def test_attention_weights_sum_to_one():
    result=LearnedModalityAttention().score({"text":.8,"image":.4,"tabular":.7})
    assert abs(sum(result.attention.values())-1) < 1e-3
    assert 0 <= result.score <= 1
    assert 0 <= result.confidence <= .99
