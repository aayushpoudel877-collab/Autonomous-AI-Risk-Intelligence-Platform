from fastapi import FastAPI
from backend.app.api.routes import router
from backend.app.core.config import settings
app=FastAPI(title=settings.app_name,version=settings.version)
app.include_router(router,prefix=settings.api_prefix)
@app.get("/health",tags=["system"])
def health(): return {"status":"ok","service":settings.app_name,"version":settings.version}
