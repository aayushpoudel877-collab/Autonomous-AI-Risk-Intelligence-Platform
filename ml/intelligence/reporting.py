from dataclasses import dataclass
from datetime import datetime,timezone

@dataclass(frozen=True)
class InvestigationReport:
    investigation_id:str
    title:str
    summary:str
    evidence:list[dict]
    limitations:list[str]
    generated_at:str

def build_report(investigation):
    evidence=investigation.evidence
    return InvestigationReport(
        investigation.investigation_id,
        "Evidence Review",
        f"Investigation {investigation.investigation_id} retrieved {len(evidence)} evidence item(s) for query: {investigation.query}.",
        evidence,
        ["Retrieval relevance is not proof of causation.","Findings should be validated against primary sources and domain context."],
        datetime.now(timezone.utc).isoformat())
