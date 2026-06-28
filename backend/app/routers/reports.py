import os
from fastapi import APIRouter, Depends, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.report import Report
from app.models.comparison import ComparisonHistory
from app.schemas.report import ReportResponse, ReportDetailsResponse, ReportAnalysisResponse
from app.schemas.comparison import ReportCompareRequest, ReportCompareAPIResponse
from app.services.report_service import report_service
from app.services.comparison_service import comparison_service
from app.services.pdf_service import pdf_service
from app.utils.response_utils import CustomHTTPException, success_response

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.post("/analyze", response_model=ReportAnalysisResponse, status_code=status.HTTP_201_CREATED)
def analyze_report(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Uploads a health report (PDF, PNG, JPG, JPEG), runs OCR, extracts clinical values,
    executes ML risk predictions, saves to MySQL, and generates an AI health summary.
    """
    report = report_service.analyze_report(db, current_user, file)
    return {
        "success": True,
        "message": "Report analysis pipeline completed successfully.",
        "report": report
    }

@router.get("", response_model=List[ReportResponse])
def get_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lists all reports uploaded by the logged-in user.
    """
    return db.query(Report).filter(Report.user_id == current_user.id).order_by(Report.created_at.desc()).all()

@router.get("/{id}", response_model=ReportDetailsResponse)
def get_report_details(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetches comprehensive data for a specific report, including values and predictions.
    """
    report = db.query(Report).filter(Report.id == id, Report.user_id == current_user.id).first()
    if not report:
        raise CustomHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found.",
            error_code="REPORT_NOT_FOUND"
        )
    return report

@router.post("/compare", response_model=ReportCompareAPIResponse)
def compare_reports(
    payload: ReportCompareRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Compares two user reports (baseline/older vs. newer). Computes differences,
    improvement statuses, overall percentage growth, and compiles an AI summary.
    """
    comparison = comparison_service.compare_reports(
        db, current_user.id, payload.base_report_id, payload.compare_report_id
    )
    return {
        "success": True,
        "message": "Reports comparison generated successfully.",
        "comparison": comparison
    }

@router.get("/{id}/download")
def download_pdf_report(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generates and downloads a beautifully styled clinical PDF report.
    Includes patient parameters, predictions, abnormal status alerts, and progress shifts.
    """
    report = db.query(Report).filter(Report.id == id, Report.user_id == current_user.id).first()
    if not report:
        raise CustomHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found.",
            error_code="REPORT_NOT_FOUND"
        )
        
    if report.status != "COMPLETED":
        raise CustomHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot generate PDF for report in status {report.status}.",
            error_code="INCOMPLETE_REPORT"
        )

    # Resolve if comparison data is available for this report
    # We look for any comparison where this report is the "compare_report_id"
    comparison_model = db.query(ComparisonHistory).filter(
        ComparisonHistory.user_id == current_user.id,
        ComparisonHistory.compare_report_id == id
    ).order_by(ComparisonHistory.created_at.desc()).first()

    comparison_dict = None
    if comparison_model:
        comparison_dict = {
            "comparison_data": comparison_model.comparison_data,
            "overall_improvement_percentage": comparison_model.overall_improvement_percentage,
            "ai_summary": comparison_model.ai_summary
        }

    # Generate PDF raw bytes & save to local path
    pdf_service.generate_report_pdf(current_user, report, comparison_dict)

    if not report.file_path or not os.path.exists(report.file_path):
        raise CustomHTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate or retrieve PDF report file.",
            error_code="PDF_GENERATION_FAILED"
        )

    return FileResponse(
        path=report.file_path,
        media_type="application/pdf",
        filename=f"healthinsight_report_{report.id}.pdf"
    )
