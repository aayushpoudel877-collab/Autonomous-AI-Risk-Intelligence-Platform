from dataclasses import dataclass,field
from datetime import datetime,timezone
from ml.intelligence.retrieval import retrieve
from ml.intelligence.embeddings import RetrievalIndex
from ml.intelligence.reporting import build_report

@dataclass
class Investigation:
    investigation_id:str
    query:str
    status:str="open"
    findings:list[str]=field(default_factory=list)
    evidence:list[dict]=field(default_factory=list)
    created_at:str=field(default_factory=lambda:datetime.now(timezone.utc).isoformat())

class InvestigationEngine:
    def __init__(self,chunks=(),index=None):
        self.chunks=list(chunks); self.index=index
        if self.index and self.chunks and not self.index.chunks:self.index.add(self.chunks)
    def investigate(self,investigation_id,query,top_k=5):
        if self.index:
            hits=self.index.search(query,top_k)
            evidence=[{"chunk_id":c.chunk_id,"source":c.source,"text":c.text,"score":round(s,6),"method":"embedding"} for c,s in hits]
        else:
            evidence=[e.__dict__ for e in retrieve(query,self.chunks,top_k)]
        return Investigation(investigation_id,query,"open",["Evidence retrieved for review." if evidence else "No matching evidence was retrieved."],evidence)
    def report(self,investigation_id,query,top_k=5):
        return build_report(self.investigate(investigation_id,query,top_k))
