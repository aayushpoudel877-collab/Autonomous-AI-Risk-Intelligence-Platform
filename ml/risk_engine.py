from dataclasses import dataclass
from ml.fusion.engine import MultimodalFusion
@dataclass(frozen=True)
class RiskDecision:
    score:float
    level:str
    confidence:float
    actions:list[str]
class RiskEngine:
    def __init__(self): self.fusion=MultimodalFusion()
    def assess(self,signals):
        result=self.fusion.combine(signals); level="low" if result.score<.35 else "medium" if result.score<.70 else "high"
        actions={"low":["continue routine monitoring"],"medium":["increase monitoring frequency","review contributing signals"],"high":["prioritize investigation","increase monitoring frequency","validate source data"]}[level]
        return RiskDecision(result.score,level,result.confidence,actions)
