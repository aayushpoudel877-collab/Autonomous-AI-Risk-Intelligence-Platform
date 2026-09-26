from pydantic import BaseModel, Field

class RiskAnalysisRequest(BaseModel):
    signals: list[float] = Field(default_factory=list, min_length=1)
    source: str = "unknown"

class RiskAnalysisResponse(BaseModel):
    risk_score: float
    risk_level: str
    confidence: float
    source: str
    factors: list[str]
