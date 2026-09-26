import numpy as np

def population_stability_index(reference, current, bins: int=10) -> float:
    ref=np.asarray(reference,dtype=float); cur=np.asarray(current,dtype=float)
    if ref.size == 0 or cur.size == 0: raise ValueError("samples must not be empty")
    edges=np.unique(np.quantile(ref,np.linspace(0,1,bins+1)))
    if len(edges)<3: return 0.0
    r,_=np.histogram(ref,bins=edges); c,_=np.histogram(cur,bins=edges)
    rp=np.clip(r/r.sum(),1e-6,None); cp=np.clip(c/c.sum(),1e-6,None)
    return float(np.sum((cp-rp)*np.log(cp/rp)))

def drift_status(psi: float) -> str:
    if psi < .1: return "stable"
    if psi < .25: return "watch"
    return "drifted"
