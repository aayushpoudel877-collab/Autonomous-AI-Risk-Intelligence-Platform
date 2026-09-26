from fastapi import APIRouter, Query
from backend.app.schemas.risk import RiskAnalysisRequest,RiskAnalysisResponse,RiskEventResponse
from backend.app.services.risk_service import analyze_risk
from backend.app.services.persistence import save_risk_event,recent_events
from ml.explainability.explanations import explain_risk

router=APIRouter(tags=["risk"])

@router.post("/risk/analyze",response_model=RiskAnalysisResponse)
def risk_analysis(payload:RiskAnalysisRequest):
    result=analyze_risk(payload); save_risk_event(result); return result

@router.post("/risk/explain")
def risk_explanation(payload:RiskAnalysisRequest):
    result=analyze_risk(payload)
    explanation=explain_risk(dict(zip([f"signal_{i}" for i in range(len(payload.signals))],payload.signals)),result.risk_score/100)
    return {"risk":result,"explanation":explanation}

@router.get("/risk/events",response_model=list[RiskEventResponse])
def risk_events(limit:int=Query(default=20,ge=1,le=100)):
    return recent_events(limit)

@router.get("/system/info")
def system_info(): return {"module":"risk-intelligence","status":"operational"}
