from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PredictionBase(BaseModel):
    heart_disease_risk: str = Field(..., description="Risk level (LOW, BORDERLINE, HIGH)")
    diabetes_risk: str = Field(..., description="Risk level (LOW, BORDERLINE, HIGH)")
    kidney_disease_risk: str = Field(..., description="Risk level (LOW, BORDERLINE, HIGH)")
    stroke_risk: str = Field(..., description="Risk level (LOW, BORDERLINE, HIGH)")
    health_score: int = Field(..., ge=0, le=100, description="Overall health score (0-100)")

class PredictionCreate(PredictionBase):
    pass

class PredictionResponse(PredictionBase):
    id: int
    report_id: Optional[int] = None
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
