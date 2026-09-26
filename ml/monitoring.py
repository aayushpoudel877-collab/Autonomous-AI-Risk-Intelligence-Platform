from dataclasses import dataclass, field
from time import perf_counter
from statistics import mean

@dataclass
class InferenceMonitor:
    latencies_ms: list[float] = field(default_factory=list)
    risk_scores: list[float] = field(default_factory=list)
    errors: int = 0

    def observe(self, score: float, started_at: float):
        self.risk_scores.append(float(score))
        self.latencies_ms.append((perf_counter()-started_at)*1000)

    def record_error(self):
        self.errors += 1

    def snapshot(self):
        return {
            "requests": len(self.risk_scores),
            "errors": self.errors,
            "error_rate": self.errors/max(1,len(self.risk_scores)+self.errors),
            "mean_latency_ms": mean(self.latencies_ms) if self.latencies_ms else 0.0,
            "mean_risk": mean(self.risk_scores) if self.risk_scores else 0.0,
        }
