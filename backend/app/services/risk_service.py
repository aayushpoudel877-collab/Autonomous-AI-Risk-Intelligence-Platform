from statistics import mean
from backend.app.schemas.risk import RiskAnalysisRequest, RiskAnalysisResponse

def analyze_risk(payload: RiskAnalysisRequest) -> RiskAnalysisResponse:
    values = [max(0.0, min(1.0, value)) for value in payload.signals]
    score = round(mean(values) * 100, 2)
    level = "low" if score < 35 else "medium" if score < 70 else "high"
    confidence = round(min(0.99, 0.55 + 0.08 * len(values)), 2)
    factors = [
        "aggregate signal intensity" if values else "no signal",
        "multi-signal consistency" if len(values) > 1 else "single-signal assessment",
    ]
    return RiskAnalysisResponse(risk_score=score, risk_level=level, confidence=confidence, source=payload.source, factors=factors)
