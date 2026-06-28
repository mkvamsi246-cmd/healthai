from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.medical_values import MedicalValuesResponse
from app.schemas.prediction import PredictionResponse

class ReportBase(BaseModel):
    file_name: str
    file_type: str
    file_size: int

class ReportResponse(ReportBase):
    id: int
    user_id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class ReportDetailsResponse(ReportResponse):
    extracted_text: Optional[str] = None
    ai_summary: Optional[str] = None
    medical_values: Optional[MedicalValuesResponse] = None
    prediction: Optional[PredictionResponse] = None

    class Config:
        from_attributes = True

class ReportAnalysisResponse(BaseModel):
    success: bool
    message: str
    report: ReportDetailsResponse
