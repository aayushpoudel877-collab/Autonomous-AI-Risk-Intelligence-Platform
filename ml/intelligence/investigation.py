from dataclasses import dataclass,field
from datetime import datetime,timezone
from ml.intelligence.retrieval import retrieve

@dataclass
class Investigation:
    investigation_id:str
    query:str
    status:str="open"
    findings:list[str]=field(default_factory=list)
    evidence:list[dict]=field(default_factory=list)
    created_at:str=field(default_factory=lambda:datetime.now(timezone.utc).isoformat())

class InvestigationEngine:
    def __init__(self,chunks=()):
        self.chunks=list(chunks)
    def investigate(self,investigation_id,query,top_k=5):
        evidence=retrieve(query,self.chunks,top_k)
        findings=["Retrieved evidence supports further review." if evidence else "No matching evidence was retrieved."]
        return Investigation(investigation_id,query,"open",findings,[e.__dict__ for e in evidence])
