from ml.explainability.explanations import explain_risk
def test_explanation_ranks_signals():
    e=explain_risk({"text":.2,"tabular":.9},.7)
    assert e.contributors[0]["signal"]=="tabular" and e.caveats
