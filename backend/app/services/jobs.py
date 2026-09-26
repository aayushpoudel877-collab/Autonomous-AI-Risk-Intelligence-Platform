from datetime import datetime, timezone
from uuid import uuid4

_jobs={}

def submit_job(kind:str,payload:dict)->dict:
    job_id=str(uuid4())
    _jobs[job_id]={"id":job_id,"kind":kind,"status":"queued","created_at":datetime.now(timezone.utc).isoformat(),"payload":payload}
    return _jobs[job_id]

def get_job(job_id:str):
    return _jobs.get(job_id)
