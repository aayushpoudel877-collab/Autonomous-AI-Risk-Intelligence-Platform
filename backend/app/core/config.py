import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "AegisMind Risk Intelligence Platform")
    version: str = os.getenv("APP_VERSION", "0.1.0")
    api_prefix: str = os.getenv("API_V1_PREFIX", "/api/v1")
    environment: str = os.getenv("APP_ENV", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
