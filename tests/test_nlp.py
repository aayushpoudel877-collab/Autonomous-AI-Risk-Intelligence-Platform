from ml.nlp.preprocessing import keyword_risk_score, normalize_text, tokenize

def test_normalization_and_tokens():
    assert normalize_text("  FRAUD!!!  ") == "fraud!!!"
    assert "fraud" in tokenize("Fraud in the payment system")

def test_keyword_risk_score():
    assert keyword_risk_score("routine maintenance") == 0.0
    assert keyword_risk_score("fraud breach incident") > 0
