from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class Citation:
    citation_id: str
    evidence_id: str
    source: str
    locator: str = ""


@dataclass(frozen=True)
class GroundedClaim:
    claim_id: str
    text: str
    citations: list[Citation]
    confidence: float


@dataclass(frozen=True)
class GroundedSynthesis:
    query: str
    claims: list[GroundedClaim]
    generated_at: str
    limitations: list[str] = field(default_factory=list)


def synthesize_investigation(investigation) -> GroundedSynthesis:
    claims = []
    for i, item in enumerate(investigation.evidence, start=1):
        evidence_id = item.get("chunk_id", f"evidence-{i}")
        source = item.get("source", "unknown")
        score = float(item.get("score", 0.0))
        claim = f"Evidence from {source} is relevant to the investigation query: {investigation.query}."
        citation = Citation(
            citation_id=f"cite-{i}",
            evidence_id=evidence_id,
            source=source,
            locator=evidence_id,
        )
        claims.append(GroundedClaim(
            claim_id=f"claim-{i}",
            text=claim,
            citations=[citation],
            confidence=max(0.0, min(1.0, score)),
        ))
    return GroundedSynthesis(
        query=investigation.query,
        claims=claims,
        generated_at=datetime.now(timezone.utc).isoformat(),
        limitations=[
            "Claims are grounded to retrieved evidence, not independent verification.",
            "Retrieval relevance does not establish causation or factual truth.",
            "Confidence reflects retrieval similarity and is not a calibrated probability.",
        ],
    )


def validate_citations(synthesis: GroundedSynthesis) -> list[str]:
    errors = []
    for claim in synthesis.claims:
        if not claim.citations:
            errors.append(f"{claim.claim_id}: missing citation")
        for citation in claim.citations:
            if not citation.evidence_id or not citation.source:
                errors.append(f"{claim.claim_id}: incomplete citation")
    return errors
