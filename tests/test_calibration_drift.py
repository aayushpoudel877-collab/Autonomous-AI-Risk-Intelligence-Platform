import numpy as np
from ml.calibration.metrics import brier_score, expected_calibration_error
from ml.drift import population_stability_index, drift_status

def test_calibration_metrics():
    y=np.array([0,0,1,1]); p=np.array([.1,.2,.8,.9])
    assert 0 <= brier_score(y,p) <= 1
    assert 0 <= expected_calibration_error(y,p) <= 1

def test_drift():
    ref=np.linspace(0,1,100); current=np.linspace(0,1,100)
    psi=population_stability_index(ref,current)
    assert psi < .1 and drift_status(psi) == "stable"
