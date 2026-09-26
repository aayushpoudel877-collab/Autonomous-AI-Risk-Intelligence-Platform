from fastapi import APIRouter
from backend.app.schemas.risk import RiskAnalysisRequest, RiskAnalysisResponse
from backend.app.services.risk_service import analyze_risk

router = APIRouter(tags=["risk"])

@router.post("/risk/analyze", response_model=RiskAnalysisResponse)
def risk_analysis(payload: RiskAnalysisRequest) -> RiskAnalysisResponse:
    return analyze_risk(payload)

@router.get("/system/info")
def system_info() -> dict[str, str]:
    return {"module": "risk-intelligence", "status": "operational"}
