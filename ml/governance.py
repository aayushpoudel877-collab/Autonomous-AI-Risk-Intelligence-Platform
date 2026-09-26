from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path

@dataclass(frozen=True)
class PromotionDecision:
    model_name:str
    version:str
    approved:bool
    reasons:tuple[str,...]
    decided_at:str

class PromotionGate:
    def __init__(self,min_metric:float=.80,max_ece:float=.10,max_psi:float=.25):
        self.min_metric=min_metric; self.max_ece=max_ece; self.max_psi=max_psi

    def evaluate(self,model_name:str,version:str,metric:float,ece:float,psi:float)->PromotionDecision:
        reasons=[]
        if metric < self.min_metric: reasons.append(f"metric {metric:.4f} below {self.min_metric:.4f}")
        if ece > self.max_ece: reasons.append(f"ECE {ece:.4f} above {self.max_ece:.4f}")
        if psi >= self.max_psi: reasons.append(f"PSI {psi:.4f} at/above {self.max_psi:.4f}")
        return PromotionDecision(model_name,version,not reasons,tuple(reasons) or ("all promotion gates passed",),datetime.now(timezone.utc).isoformat())

class GovernanceAuditLog:
    def __init__(self,path="data/governance_audit.jsonl"): self.path=Path(path)
    def append(self,decision:PromotionDecision):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.path.open("a",encoding="utf-8") as f:
            f.write(json.dumps({"model_name":decision.model_name,"version":decision.version,"approved":decision.approved,"reasons":decision.reasons,"decided_at":decision.decided_at})+"\n")
    def read(self):
        if not self.path.exists(): return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line]
