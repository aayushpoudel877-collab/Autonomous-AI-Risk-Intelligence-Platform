from dataclasses import dataclass, field

@dataclass(frozen=True)
class InvestigationStep:
    step_id: str
    action: str
    query: str
    reason: str

@dataclass
class InvestigationTrace:
    investigation_id: str
    goal: str
    status: str = "planned"
    steps: list[InvestigationStep] = field(default_factory=list)
    evidence: list[dict] = field(default_factory=list)
    completed_steps: int = 0
    stop_reason: str = ""

    def as_dict(self):
        return {"investigation_id": self.investigation_id, "goal": self.goal,
                "status": self.status, "steps": [s.__dict__ for s in self.steps],
                "evidence": self.evidence, "completed_steps": self.completed_steps,
                "stop_reason": self.stop_reason}

class InvestigationPlanner:
    def plan(self, investigation_id: str, goal: str, max_steps: int = 3):
        perspectives = [
            (goal, "initial evidence retrieval"),
            (f"{goal} cause", "look for causal context"),
            (f"{goal} impact", "look for impact and downstream effects"),
        ][:max_steps]
        steps = [InvestigationStep(f"{investigation_id}-step-{i}", "retrieve", q, reason)
                 for i, (q, reason) in enumerate(perspectives, 1)]
        return InvestigationTrace(investigation_id, goal, steps=steps)

class AutonomousInvestigator:
    def __init__(self, engine):
        self.engine = engine

    def run(self, investigation_id: str, goal: str, max_steps: int = 3, top_k: int = 5):
        trace = InvestigationPlanner().plan(investigation_id, goal, max_steps)
        trace.status = "running"
        seen = set()
        for step in trace.steps:
            result = self.engine.investigate(
                f"{investigation_id}-{trace.completed_steps + 1}", step.query, top_k)
            for item in result.evidence:
                key = item["chunk_id"]
                if key not in seen:
                    seen.add(key)
                    trace.evidence.append({**item, "step_id": step.step_id, "query": step.query})
            trace.completed_steps += 1
            if len(trace.evidence) >= top_k * 2:
                trace.stop_reason = "evidence_saturation"
                break
        trace.status = "completed"
        if not trace.stop_reason:
            trace.stop_reason = "planned_steps_exhausted"
        return trace
