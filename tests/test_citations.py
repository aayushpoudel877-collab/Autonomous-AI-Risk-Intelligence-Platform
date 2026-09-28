from ml.intelligence.documents import ingest_text
from ml.intelligence.investigation import InvestigationEngine
from ml.intelligence.citations import synthesize_investigation, validate_citations


def test_every_grounded_claim_has_citation():
    chunks = ingest_text("Database latency increased after deployment.", "ops")
    investigation = InvestigationEngine(chunks).investigate("i-3", "database latency")
    synthesis = synthesize_investigation(investigation)
    assert synthesis.claims
    assert not validate_citations(synthesis)
    assert all(claim.citations for claim in synthesis.claims)


def test_empty_investigation_is_valid():
    investigation = InvestigationEngine([]).investigate("i-4", "unknown")
    synthesis = synthesize_investigation(investigation)
    assert synthesis.claims == []
    assert not validate_citations(synthesis)
