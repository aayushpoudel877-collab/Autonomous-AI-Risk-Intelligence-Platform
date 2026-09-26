from fastapi import FastAPI
from backend.app.api.routes import router
from backend.app.db import init_db

app=FastAPI(title="AegisMind Risk Intelligence API",version="0.2.0")
init_db()
app.include_router(router,prefix="/api/v1")

@app.get("/health")
def health(): return {"status":"ok"}
