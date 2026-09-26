from fastapi import APIRouter
from backend.app.services.telemetry import snapshot

router=APIRouter(prefix="/monitoring",tags=["monitoring"])

@router.get("/metrics")
def metrics():
    return snapshot()
