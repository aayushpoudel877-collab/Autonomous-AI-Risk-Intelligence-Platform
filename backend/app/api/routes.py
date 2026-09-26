from fastapi import APIRouter
from backend.app.schemas.risk import RiskAnalysisRequest,RiskAnalysisResponse
from backend.app.services.risk_service import analyze_risk
from ml.explainability.explanations import explain_risk

router=APIRouter(tags=["risk"])
@router.post("/risk/analyze",response_model=RiskAnalysisResponse)
def risk_analysis(payload:RiskAnalysisRequest): return analyze_risk(payload)
@router.post("/risk/explain")
def risk_explanation(payload:RiskAnalysisRequest):
    result=analyze_risk(payload); explanation=explain_risk(dict(zip([f"signal_{i}" for i in range(len(payload.signals))],payload.signals)),result.risk_score/100)
    return {"risk":result,"explanation":explanation}
@router.get("/system/info")
def system_info(): return {"module":"risk-intelligence","status":"operational"}
