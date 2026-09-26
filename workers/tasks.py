import os
try:
    from celery import Celery
except ImportError:
    Celery=None

def create_celery():
    if Celery is None: raise ImportError("Celery is required. Install aegismind[workers].")
    broker=os.getenv("CELERY_BROKER_URL","redis://redis:6379/0")
    return Celery("aegismind",broker=broker,backend=broker)

celery_app=create_celery() if Celery is not None else None

if celery_app is not None:
    @celery_app.task
    def health_check_task():
        return {"status":"ok","worker":"aegismind"}
