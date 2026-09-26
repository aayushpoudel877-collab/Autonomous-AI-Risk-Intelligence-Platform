from dataclasses import dataclass
import math
import re
from collections import Counter

@dataclass(frozen=True)
class SemanticEvidence:
    chunk_id:str
    source:str
    text:str
    score:float
    method:str="tfidf-lite"

def _terms(text): return re.findall(r"[a-z0-9]+",text.lower())

def semantic_retrieve(query,chunks,top_k=5):
    q=Counter(_terms(query)); scored=[]
    if not q: return []
    for c in chunks:
        d=Counter(_terms(c.text))
        overlap=sum(min(q[t],d[t]) for t in q)
        denom=math.sqrt(sum(v*v for v in q.values())*sum(v*v for v in d.values())) or 1
        score=overlap/denom
        if score>0: scored.append(SemanticEvidence(c.chunk_id,c.source,c.text,round(score,6)))
    return sorted(scored,key=lambda x:x.score,reverse=True)[:top_k]
