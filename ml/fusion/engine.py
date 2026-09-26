from dataclasses import dataclass
import numpy as np
@dataclass(frozen=True)
class FusionResult:
    score:float
    confidence:float
    modality_weights:dict[str,float]
class MultimodalFusion:
    def __init__(self,weights=None):
        self.weights=weights or {"text":.2,"image":.15,"tabular":.4,"temporal":.25}; total=sum(self.weights.values()); self.weights={k:v/total for k,v in self.weights.items()}
    def combine(self,signals):
        clipped={k:float(np.clip(v,0,1)) for k,v in signals.items() if k in self.weights}
        if not clipped: raise ValueError("at least one supported modality is required")
        weights={k:self.weights[k] for k in clipped}; norm=sum(weights.values()); score=sum(clipped[k]*weights[k] for k in clipped)/norm
        agreement=1-float(np.std(list(clipped.values()))) if len(clipped)>1 else .65
        return FusionResult(round(score,4),round(float(np.clip(.55+.4*agreement,0,.99)),4),weights)
