from dataclasses import dataclass
import math
import re
from collections import Counter

@dataclass(frozen=True)
class Evidence:
    chunk_id:str
    source:str
    text:str
    score:float

def _terms(text):
    return re.findall(r"[a-z0-9]+",text.lower())

def retrieve(query,chunks,top_k=5):
    if not query.strip(): return []
    q=Counter(_terms(query)); scored=[]
    for c in chunks:
        d=Counter(_terms(c.text))
        overlap=sum(min(q[t],d[t]) for t in q)
        norm=math.sqrt(sum(v*v for v in q.values())*sum(v*v for v in d.values())) or 1
        score=overlap/norm
        if score>0: scored.append(Evidence(c.chunk_id,c.source,c.text,round(score,6)))
    return sorted(scored,key=lambda x:x.score,reverse=True)[:top_k]
