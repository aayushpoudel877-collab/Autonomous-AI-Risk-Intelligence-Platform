from fastapi import FastAPI
from backend.app.api.routes import router
from backend.app.api.jobs import router as jobs_router
from backend.app.api.monitoring import router as monitoring_router
from backend.app.api.governance import router as governance_router
from backend.app.db import init_db

app=FastAPI(title="AegisMind Risk Intelligence API",version="0.5.0")
init_db()
app.include_router(router,prefix="/api/v1")
app.include_router(jobs_router,prefix="/api/v1")
app.include_router(monitoring_router,prefix="/api/v1")
app.include_router(governance_router,prefix="/api/v1")

@app.get("/health")
def health(): return {"status":"ok"}
