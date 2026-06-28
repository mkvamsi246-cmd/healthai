from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime

class ReportCompareRequest(BaseModel):
    base_report_id: int = Field(..., description="The previous report ID to compare from")
    compare_report_id: int = Field(..., description="The newer report ID to compare to")

class CompareItem(BaseModel):
    parameter: str
    previous_value: Optional[float] = None
    current_value: Optional[float] = None
    difference: Optional[float] = None
    status: str = Field(..., description="Improved, Stable, or Worsened")
    unit: str

class ReportComparisonResponse(BaseModel):
    id: Optional[int] = None
    base_report_id: int
    compare_report_id: int
    comparison_data: Dict[str, CompareItem]
    overall_improvement_percentage: float
    ai_summary: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ReportCompareAPIResponse(BaseModel):
    success: bool
    message: str
    comparison: ReportComparisonResponse
