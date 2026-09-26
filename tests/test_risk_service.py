from backend.app.schemas.risk import RiskAnalysisRequest
from backend.app.services.risk_service import analyze_risk

def test_high_risk_classification():
    result = analyze_risk(RiskAnalysisRequest(signals=[0.9, 0.8], source="test"))
    assert result.risk_level == "high"
    assert result.risk_score == 85.0

def test_low_risk_classification():
    result = analyze_risk(RiskAnalysisRequest(signals=[0.1, 0.2], source="test"))
    assert result.risk_level == "low"
