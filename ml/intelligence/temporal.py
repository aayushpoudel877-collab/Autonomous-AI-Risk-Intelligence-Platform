from datetime import datetime,timezone

def parse_timestamp(value):
    return datetime.fromisoformat(value.replace("Z","+00:00"))

def temporal_window(events,start,end):
    lo=parse_timestamp(start); hi=parse_timestamp(end)
    return [e for e in events if lo<=parse_timestamp(e["timestamp"])<=hi]

def build_timeline(events):
    return sorted(events,key=lambda e:parse_timestamp(e["timestamp"]))

def temporal_gaps(events):
    ordered=build_timeline(events); gaps=[]
    for a,b in zip(ordered,ordered[1:]):
        delta=(parse_timestamp(b["timestamp"])-parse_timestamp(a["timestamp"])).total_seconds()
        gaps.append({"from":a["id"],"to":b["id"],"seconds":delta})
    return gaps
