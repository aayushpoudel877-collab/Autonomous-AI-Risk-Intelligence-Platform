from fastapi import APIRouter
from pydantic import BaseModel,Field
from ml.governance import GovernanceAuditLog,PromotionGate
from ml.retraining import assess_retraining

router=APIRouter(prefix="/governance",tags=["governance"])

class Candidate(BaseModel):
    model_name:str
    version:str
    metric:float=Field(ge=0,le=1)
    ece:float=Field(ge=0,le=1)
    psi:float=Field(ge=0)

class DriftRequest(BaseModel):
    reference:list[float]
    current:list[float]

@router.post("/evaluate")
def evaluate_candidate(candidate:Candidate):
    decision=PromotionGate().evaluate(candidate.model_name,candidate.version,candidate.metric,candidate.ece,candidate.psi)
    GovernanceAuditLog().append(decision)
    return {"approved":decision.approved,"model_name":decision.model_name,"version":decision.version,"reasons":decision.reasons,"decided_at":decision.decided_at}

@router.post("/retraining-assessment")
def retraining_assessment(payload:DriftRequest):
    return assess_retraining(payload.reference,payload.current)

@router.get("/audit")
def audit_log():
    return GovernanceAuditLog().read()[-100:]
