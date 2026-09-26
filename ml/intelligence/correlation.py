from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class CorrelatedEvent:
    event_id:str
    source:str
    risk_score:float
    timestamp:str
    matched_evidence:list[str]

def correlate_events(events,window_seconds=3600):
    ordered=sorted(events,key=lambda e:e["timestamp"])
    groups=[]
    for event in ordered:
        ts=datetime.fromisoformat(event["timestamp"].replace("Z","+00:00"))
        matched=[]
        for prior in groups[-20:]:
            pts=datetime.fromisoformat(prior.timestamp.replace("Z","+00:00"))
            if abs((ts-pts).total_seconds())<=window_seconds and prior.source!=event.get("source","unknown"):
                matched.append(prior.event_id)
        groups.append(CorrelatedEvent(str(event["id"]),event.get("source","unknown"),float(event.get("risk_score",0)),event["timestamp"],matched))
    return groups
