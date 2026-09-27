from fastapi import APIRouter, HTTPException
from backend.app.services.jobs import get_job, submit_job
from workers.tasks import assess_retraining_task, celery_app

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("")
def create_job(payload: dict):
    job = submit_job(payload.get("kind", "risk-analysis"), payload)
    if job["kind"] == "retraining-assessment":
        if celery_app is not None:
            try:
                task = assess_retraining_task.delay(
                    payload.get("reference", []), payload.get("current", [])
                )
                job["celery_task_id"] = task.id
            except Exception:
                job["status"] = "queued-local"
        else:
            job["status"] = "queued-local"
    return job


@router.get("/{job_id}")
def read_job(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    return job
