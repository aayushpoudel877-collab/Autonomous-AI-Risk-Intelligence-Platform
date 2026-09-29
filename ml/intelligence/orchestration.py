from dataclasses import dataclass, field
import re

from ml.intelligence.entities import extract_entities


@dataclass(frozen=True)
class InvestigationStep:
    step_id: str
    action: str
    query: str
    reason: str


@dataclass(frozen=True)
class AdaptiveDecision:
    step_id: str
    query: str
    objective: str
    reason: str
    evidence_ids: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class InvestigationObjective:
    name: str
    required_aspects: tuple[str, ...] = ("cause", "impact", "timeline")
    min_evidence: int = 3


@dataclass
class InvestigationTrace:
    investigation_id: str
    goal: str
    status: str = "planned"
    steps: list[InvestigationStep] = field(default_factory=list)
    evidence: list[dict] = field(default_factory=list)
    completed_steps: int = 0
    stop_reason: str = ""
    decisions: list[AdaptiveDecision] = field(default_factory=list)

    def as_dict(self):
        return {
            "investigation_id": self.investigation_id,
            "goal": self.goal,
            "status": self.status,
            "steps": [s.__dict__ for s in self.steps],
            "evidence": self.evidence,
            "completed_steps": self.completed_steps,
            "stop_reason": self.stop_reason,
            "decisions": [d.__dict__ for d in self.decisions],
        }


class InvestigationPlanner:
    def plan(self, investigation_id: str, goal: str, max_steps: int = 3):
        perspectives = [
            (goal, "initial evidence retrieval"),
            (f"{goal} cause", "look for causal context"),
            (f"{goal} impact", "look for impact and downstream effects"),
        ][:max_steps]
        steps = [
            InvestigationStep(
                f"{investigation_id}-step-{i}", "retrieve", query, reason
            )
            for i, (query, reason) in enumerate(perspectives, 1)
        ]
        return InvestigationTrace(investigation_id, goal, steps=steps)


class AdaptiveInvestigationPlanner:
    """Deterministic evidence-aware planner with bounded query generation."""

    _ASPECT_TERMS = {
        "cause": ("cause", "because", "due", "trigger", "root", "after", "failure", "introduced"),
        "impact": ("impact", "affected", "effect", "outage", "loss", "degraded", "downstream", "users"),
        "timeline": ("before", "after", "during", "since", "when", "yesterday", "today", "timestamp", "deployment"),
    }

    def _covered_aspects(self, evidence):
        text = " ".join(str(item.get("text", "")).lower() for item in evidence)
        return {
            aspect for aspect, terms in self._ASPECT_TERMS.items()
            if any(term in text for term in terms)
        }

    def _candidate_queries(self, goal, missing, evidence):
        snippets = " ".join(str(item.get("text", "")) for item in evidence[-3:])
        entities = extract_entities(snippets)
        candidates = []
        for aspect in missing:
            candidates.append((f"{goal} {aspect}", aspect, f"missing objective aspect: {aspect}"))
        if entities:
            entity = entities[0].text
            candidates.append(
                (f"{entity} related to {goal}", "entity", f"expand investigation through entity {entity}")
            )
        return candidates

    def next_step(
        self,
        investigation_id: str,
        goal: str,
        evidence: list[dict],
        completed_queries: set[str],
        objective: InvestigationObjective | None = None,
        step_number: int = 1,
    ):
        objective = objective or InvestigationObjective("risk-investigation")
        covered = self._covered_aspects(evidence)
        missing = [aspect for aspect in objective.required_aspects if aspect not in covered]
        candidates = self._candidate_queries(goal, missing, evidence)

        if not candidates:
            candidates = [
                (f"{goal} additional evidence", "evidence", "increase independent evidence coverage")
            ]

        for query, aspect, reason in candidates:
            normalized = re.sub(r"\s+", " ", query.strip().lower())
            if normalized not in {re.sub(r"\s+", " ", q.strip().lower()) for q in completed_queries}:
                step_id = f"{investigation_id}-adaptive-{step_number}"
                return InvestigationStep(step_id, "retrieve", query, reason), aspect

        return None, "satisfied"

    def objectives_satisfied(self, evidence: list[dict], objective: InvestigationObjective):
        covered = self._covered_aspects(evidence)
        return len(evidence) >= objective.min_evidence and all(
            aspect in covered for aspect in objective.required_aspects
        )


class AutonomousInvestigator:
    def __init__(self, engine):
        self.engine = engine

    def run(self, investigation_id: str, goal: str, max_steps: int = 3, top_k: int = 5):
        trace = InvestigationPlanner().plan(investigation_id, goal, max_steps)
        trace.status = "running"
        seen = set()
        for step in trace.steps:
            result = self.engine.investigate(
                f"{investigation_id}-{trace.completed_steps + 1}", step.query, top_k
            )
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

    def run_adaptive(
        self,
        investigation_id: str,
        goal: str,
        max_steps: int = 6,
        top_k: int = 5,
        objective: InvestigationObjective | None = None,
    ):
        objective = objective or InvestigationObjective("risk-investigation")
        trace = InvestigationTrace(investigation_id, goal, status="running")
        planner = AdaptiveInvestigationPlanner()
        seen: set[str] = set()
        completed_queries: set[str] = set()

        for step_number in range(1, max_steps + 1):
            step, aspect = planner.next_step(
                investigation_id, goal, trace.evidence, completed_queries, objective, step_number
            )
            if step is None:
                trace.stop_reason = "objectives_satisfied"
                break

            trace.steps.append(step)
            completed_queries.add(step.query)
            result = self.engine.investigate(
                f"{investigation_id}-{trace.completed_steps + 1}", step.query, top_k
            )
            new_ids = []
            for item in result.evidence:
                key = item["chunk_id"]
                if key not in seen:
                    seen.add(key)
                    new_ids.append(key)
                    trace.evidence.append({**item, "step_id": step.step_id, "query": step.query})

            trace.decisions.append(
                AdaptiveDecision(step.step_id, step.query, aspect, step.reason, new_ids)
            )
            trace.completed_steps += 1

            if planner.objectives_satisfied(trace.evidence, objective):
                trace.stop_reason = "objectives_satisfied"
                break

        if not trace.stop_reason:
            trace.stop_reason = "max_steps_reached"
        trace.status = "completed"
        return trace
