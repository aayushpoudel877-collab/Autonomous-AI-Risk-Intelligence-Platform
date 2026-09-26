from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class AttentionFusionResult:
    score: float
    confidence: float
    attention: dict[str,float]

class LearnedModalityAttention:
    """Lightweight learned-style attention layer for modality embeddings."""
    def __init__(self, temperature: float = 1.0):
        self.temperature=max(0.1, temperature)

    def score(self, signals: dict[str,float]) -> AttentionFusionResult:
        valid={k:float(np.clip(v,0,1)) for k,v in signals.items() if v is not None}
        if not valid: raise ValueError("at least one modality is required")
        logits=np.array(list(valid.values()))/self.temperature
        logits=logits-logits.max()
        weights=np.exp(logits); weights=weights/weights.sum()
        attention={k:round(float(w),4) for k,w in zip(valid,weights)}
        score=float(sum(valid[k]*attention[k] for k in valid))
        confidence=float(np.clip(0.55+0.4*(1-np.std(list(valid.values()))),0,0.99))
        return AttentionFusionResult(round(score,4),round(confidence,4),attention)
