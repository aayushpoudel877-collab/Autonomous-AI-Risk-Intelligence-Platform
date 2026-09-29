from dataclasses import dataclass, field
import re

from ml.intelligence.entities import extract_entities
from ml.intelligence.knowledge_graph import KnowledgeGraph
from ml.intelligence.temporal import temporal_gaps


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
    min_provenance: int = 0
    require_graph_context: bool = False
    require_temporal_context: bool = False


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
    coverage: dict = field(default_factory=dict)

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
            "coverage": self.coverage,
        }


class InvestigationPlanner:
    def plan(self, investigation_id: str, goal: str, max_steps: int = 3):
        perspectives = [
            (goal, "initial evidence retrieval"),
            (f"{goal} cause", "look for causal context"),
            (f"{goal} impact", "look for impact and downstream effects"),
        ][:max_steps]
        steps = [
            InvestigationStep(f"{investigation_id}-step-{i}", "retrieve", query, reason)
            for i, (query, reason) in enumerate(perspectives, 1)
        ]
        return InvestigationTrace(investigation_id, goal, steps=steps)


class AdaptiveInvestigationPlanner:
    """Bounded planner that adapts using evidence, graph neighbors, and temporal gaps."""

    _ASPECT_TERMS = {
        "cause": ("cause", "because", "due", "trigger", "root", "failure", "introduced"),
        "impact": ("impact", "affected", "effect", "outage", "loss", "degraded", "downstream", "users"),
        "timeline": ("before", "after", "during", "since", "when", "yesterday", "today", "timestamp", "deployment"),
    }

    def _covered_aspects(self, evidence):
        text = " ".join(str(item.get("text", "")).lower() for item in evidence)
        covered = set()
        for aspect, terms in self._ASPECT_TERMS.items():
            if any(re.search(rf"\b{re.escape(term)}\b", text) for term in terms):
                covered.add(aspect)
        return covered

    def _graph_context(self, evidence, graph: KnowledgeGraph | None):
        if graph is None:
            return []
        labels = {str(node.label).casefold(): node.node_id for node in graph.nodes.values()}
        related = []
        for entity in extract_entities(" ".join(str(x.get("text", "")) for x in evidence[-5:])):
            node_id = labels.get(entity.text.casefold())
            if node_id:
                related.extend(
                    graph.nodes[edge.target].label if edge.target in graph.nodes else graph.nodes[edge.source].label
                    for edge in graph.neighbors(node_id)
                )
        return list(dict.fromkeys(related))

    def _temporal_context(self, events):
        if not events or len(events) < 2:
            return []
        try:
            return temporal_gaps(events)
        except (KeyError, TypeError, ValueError):
            return []

    def coverage(self, evidence, objective, graph=None, events=None, provenance_links=None):
        covered = self._covered_aspects(evidence)
        graph_context = self._graph_context(evidence, graph)
        gaps = self._temporal_context(events)
        provenance = {str(x.get("evidence_id")) for x in (provenance_links or []) if x.get("evidence_id")}
        evidence_ids = {str(x.get("chunk_id")) for x in evidence}
        return {
            "aspects": sorted(covered),
            "missing_aspects": sorted(set(objective.required_aspects) - covered),
            "evidence_count": len(evidence),
            "provenance_count": len(evidence_ids & provenance),
            "graph_context": graph_context,
            "temporal_gaps": gaps,
            "graph_context_found": bool(graph_context),
            "temporal_context_found": bool(gaps),
        }

    def _candidate_queries(self, goal, coverage):
        candidates = [
            (f"{goal} {aspect}", aspect, f"missing objective aspect: {aspect}")
            for aspect in coverage["missing_aspects"]
        ]
        for label in coverage["graph_context"][:2]:
            candidates.append(
                (f"{goal} {label}", "graph", f"follow knowledge-graph neighbor: {label}")
            )
        if coverage["temporal_gaps"]:
            candidates.append(
                (f"{goal} timeline between related events", "temporal", "investigate a detected temporal gap")
            )
        if coverage["provenance_count"] < coverage.get("evidence_count", 0):
            candidates.append(
                (f"{goal} source evidence", "provenance", "increase provenance coverage for retrieved evidence")
            )
        if not candidates:
            candidates.append(
                (f"{goal} additional evidence", "evidence", "increase independent evidence coverage")
            )
        return candidates

    @staticmethod
    def _normalize(query):
        return re.sub(r"\s+", " ", query.strip().lower())

    def next_step(
        self,
        investigation_id,
        goal,
        evidence,
        completed_queries,
        objective=None,
        step_number=1,
        graph=None,
        events=None,
        provenance_links=None,
    ):
        objective = objective or InvestigationObjective("risk-investigation")
        coverage = self.coverage(evidence, objective, graph, events, provenance_links)
        for query, aspect, reason in self._candidate_queries(goal, coverage):
            if self._normalize(query) not in {self._normalize(q) for q in completed_queries}:
                return (
                    InvestigationStep(
                        f"{investigation_id}-adaptive-{step_number}",
                        "retrieve",
                        query,
                        reason,
                    ),
                    aspect,
                )
        return None, "satisfied"

    def objectives_satisfied(self, evidence, objective, graph=None, events=None, provenance_links=None):
        coverage = self.coverage(evidence, objective, graph, events, provenance_links)
        aspects_ok = not set(coverage["missing_aspects"])
        evidence_ok = coverage["evidence_count"] >= objective.min_evidence
        provenance_ok = coverage["provenance_count"] >= objective.min_provenance
        graph_ok = not objective.require_graph_context or coverage["graph_context_found"]
        temporal_ok = not objective.require_temporal_context or coverage["temporal_context_found"]
        return evidence_ok and aspects_ok and provenance_ok and graph_ok and temporal_ok, coverage


class AutonomousInvestigator:
    def __init__(self, engine):
        self.engine = engine

    def run(self, investigation_id, goal, max_steps=3, top_k=5):
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
        investigation_id,
        goal,
        max_steps=6,
        top_k=5,
        objective=None,
        graph=None,
        events=None,
        provenance_links=None,
    ):
        objective = objective or InvestigationObjective("risk-investigation")
        trace = InvestigationTrace(investigation_id, goal, status="running")
        planner = AdaptiveInvestigationPlanner()
        seen = set()
        completed_queries = set()

        for step_number in range(1, max_steps + 1):
            step, aspect = planner.next_step(
                investigation_id, goal, trace.evidence, completed_queries, objective,
                step_number, graph, events, provenance_links
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
            satisfied, coverage = planner.objectives_satisfied(
                trace.evidence, objective, graph, events, provenance_links
            )
            trace.coverage = coverage
            if satisfied:
                trace.stop_reason = "objectives_satisfied"
                break

        if not trace.stop_reason:
            trace.stop_reason = "max_steps_reached"
        trace.status = "completed"
        return trace
