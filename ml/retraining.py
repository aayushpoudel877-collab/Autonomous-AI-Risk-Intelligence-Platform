from dataclasses import dataclass
from ml.drift import drift_status,population_stability_index
from ml.governance import PromotionGate,PromotionDecision

@dataclass(frozen=True)
class RetrainingAssessment:
    psi:float
    status:str
    should_retrain:bool
    reason:str

def assess_retraining(reference,current,threshold=.25)->RetrainingAssessment:
    psi=population_stability_index(reference,current)
    status=drift_status(psi)
    return RetrainingAssessment(psi,status,psi>=threshold,f"PSI={psi:.4f}; status={status}")

class RetrainingController:
    def __init__(self,gate=None): self.gate=gate or PromotionGate()
    def evaluate_candidate(self,name,version,metric,ece,psi)->PromotionDecision:
        return self.gate.evaluate(name,version,metric,ece,psi)
