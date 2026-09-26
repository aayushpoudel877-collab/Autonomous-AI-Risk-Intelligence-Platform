from fastapi import APIRouter, HTTPException
from backend.app.services.jobs import get_job,submit_job

router=APIRouter(prefix="/jobs",tags=["jobs"])

@router.post("")
def create_job(payload:dict):
    return submit_job(payload.get("kind","risk-analysis"),payload)

@router.get("/{job_id}")
def read_job(job_id:str):
    job=get_job(job_id)
    if not job: raise HTTPException(status_code=404,detail="job not found")
    return job
