import numpy as np
from fastapi.testclient import TestClient
from backend.app.main import app
from ml.governance import PromotionGate
from ml.retraining import assess_retraining

def test_promotion_gate_rejects_bad_candidate():
    d=PromotionGate().evaluate("risk","1",.7,.2,.3)
    assert not d.approved and len(d.reasons)==3

def test_retraining_assessment_stable():
    x=np.linspace(0,1,100)
    result=assess_retraining(x,x)
    assert result.status=="stable" and not result.should_retrain

def test_governance_api():
    client=TestClient(app)
    response=client.post("/api/v1/governance/evaluate",json={"model_name":"risk","version":"2","metric":.9,"ece":.04,"psi":.08})
    assert response.status_code==200 and response.json()["approved"] is True
