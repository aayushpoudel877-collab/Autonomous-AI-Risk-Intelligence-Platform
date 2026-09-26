import numpy as np

def brier_score(y_true, probabilities) -> float:
    y=np.asarray(y_true,dtype=float); p=np.asarray(probabilities,dtype=float)
    if y.shape != p.shape: raise ValueError("y_true and probabilities must have the same shape")
    return float(np.mean((p-y)**2))

def expected_calibration_error(y_true, probabilities, bins: int=10) -> float:
    y=np.asarray(y_true,dtype=float); p=np.asarray(probabilities,dtype=float)
    edges=np.linspace(0,1,bins+1); total=0.0
    for lo,hi in zip(edges[:-1],edges[1:]):
        mask=(p>=lo)&(p < hi if hi < 1 else p <= hi)
        if not mask.any(): continue
        total += mask.mean()*abs(p[mask].mean()-y[mask].mean())
    return float(total)

def reliability_curve(y_true, probabilities, bins: int=10):
    y=np.asarray(y_true,dtype=float); p=np.asarray(probabilities,dtype=float)
    edges=np.linspace(0,1,bins+1); points=[]
    for lo,hi in zip(edges[:-1],edges[1:]):
        mask=(p>=lo)&(p < hi if hi < 1 else p <= hi)
        if mask.any(): points.append((float(p[mask].mean()),float(y[mask].mean()),int(mask.sum())))
    return points
