from pydantic import BaseModel, Field

class RiskAnalysisRequest(BaseModel):
    signals:list[float]=Field(min_length=1,max_length=100)
    source:str="unknown"

class RiskAnalysisResponse(BaseModel):
    risk_score:float
    risk_level:str
    confidence:float
    source:str
    factors:list[str]

class RiskEventResponse(BaseModel):
    id:int
    source:str
    risk_score:float
    risk_level:str
    confidence:float
