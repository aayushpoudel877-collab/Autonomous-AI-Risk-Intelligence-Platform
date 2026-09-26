from statistics import mean
from backend.app.schemas.risk import RiskAnalysisRequest,RiskAnalysisResponse
from ml.risk_engine import RiskEngine

def analyze_risk(payload:RiskAnalysisRequest)->RiskAnalysisResponse:
    signals=[max(0,min(1,v)) for v in payload.signals]
    names={f"signal_{i}":v for i,v in enumerate(signals)}
    decision=RiskEngine().assess({"tabular":mean(signals),"temporal":max(signals),"text":min(signals),"image":mean(signals)})
    factors=[f"{k}: {v:.2f}" for k,v in names.items()]
    return RiskAnalysisResponse(risk_score=round(decision.score*100,2),risk_level=decision.level,confidence=decision.confidence,source=payload.source,factors=factors)
