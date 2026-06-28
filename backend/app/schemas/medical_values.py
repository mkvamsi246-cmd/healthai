from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class MedicalValuesBase(BaseModel):
    age: Optional[int] = Field(None, ge=0, le=120)
    gender: Optional[str] = Field(None, pattern="^(Male|Female|Other)$")
    blood_sugar: Optional[float] = Field(None, description="Fasting blood sugar (mg/dL)")
    hba1c: Optional[float] = Field(None, description="HbA1c (%)")
    systolic_bp: Optional[int] = Field(None, description="Blood pressure systolic (mmHg)")
    diastolic_bp: Optional[int] = Field(None, description="Blood pressure diastolic (mmHg)")
    heart_rate: Optional[int] = Field(None, description="Heart rate (bpm)")
    spo2: Optional[float] = Field(None, description="Oxygen Saturation (%)")
    hdl: Optional[float] = Field(None, description="High-density lipoprotein (mg/dL)")
    ldl: Optional[float] = Field(None, description="Low-density lipoprotein (mg/dL)")
    triglycerides: Optional[float] = Field(None, description="Triglycerides (mg/dL)")
    total_cholesterol: Optional[float] = Field(None, description="Total cholesterol (mg/dL)")
    creatinine: Optional[float] = Field(None, description="Creatinine (mg/dL)")
    hemoglobin: Optional[float] = Field(None, description="Hemoglobin (g/dL)")
    weight: Optional[float] = Field(None, description="Weight (kg)")
    bmi: Optional[float] = Field(None, description="Body Mass Index")

class MedicalValuesCreate(MedicalValuesBase):
    pass

class MedicalValuesResponse(MedicalValuesBase):
    id: int
    report_id: Optional[int] = None
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
