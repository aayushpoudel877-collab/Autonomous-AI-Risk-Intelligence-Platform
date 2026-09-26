from ml.risk_engine import RiskEngine
def test_fusion_produces_high_risk():
    r=RiskEngine().assess({"text":.9,"image":.8,"tabular":.95,"temporal":.85})
    assert r.level=="high" and 0<r.confidence<=.99
