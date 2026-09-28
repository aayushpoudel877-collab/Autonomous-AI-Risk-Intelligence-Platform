from dataclasses import dataclass
from datetime import datetime,timezone

from ml.intelligence.citations import synthesize_investigation


@dataclass(frozen=True)
class InvestigationReport:
    investigation_id:str
    title:str
    summary:str
    evidence:list[dict]
    claims:list[dict]
    limitations:list[str]
    generated_at:str


def build_report(investigation):
    synthesis = synthesize_investigation(investigation)
    evidence=investigation.evidence
    summary = (
        f"Investigation {investigation.investigation_id} retrieved "
        f"{len(evidence)} evidence item(s) for query: {investigation.query}."
    )
    return InvestigationReport(
        investigation.investigation_id,
        "Evidence-Grounded Review",
        summary,
        evidence,
        [{"claim_id": c.claim_id, "text": c.text,
          "confidence": c.confidence,
          "citations": [{"citation_id": x.citation_id,
                         "evidence_id": x.evidence_id,
                         "source": x.source,
                         "locator": x.locator} for x in c.citations]}
         for c in synthesis.claims],
        synthesis.limitations,
        datetime.now(timezone.utc).isoformat())
