from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Dict, Any

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.report import Report
from app.models.prediction import Prediction
from app.models.comparison import ComparisonHistory
from app.utils.response_utils import success_response

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("")
def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns aggregated dashboard metrics including latest health score,
    disease risk levels, recent reports, historical trends, and progress comparisons.
    """
    user_id = current_user.id
    
    # 1. Fetch latest report and its prediction
    latest_report = db.query(Report).filter(
        Report.user_id == user_id,
        Report.status == "COMPLETED"
    ).order_by(Report.created_at.desc()).first()

    health_score = 100
    risk_levels = {
        "heart_disease_risk": "LOW",
        "diabetes_risk": "LOW",
        "kidney_disease_risk": "LOW",
        "stroke_risk": "LOW"
    }
    
    if latest_report and latest_report.prediction:
        pred = latest_report.prediction
        health_score = pred.health_score
        risk_levels = {
            "heart_disease_risk": pred.heart_disease_risk,
            "diabetes_risk": pred.diabetes_risk,
            "kidney_disease_risk": pred.kidney_disease_risk,
            "stroke_risk": pred.stroke_risk
        }

    # 2. Fetch recent reports (last 5)
    recent_reports = db.query(Report).filter(
        Report.user_id == user_id
    ).order_by(Report.created_at.desc()).limit(5).all()

    recent_reports_data = []
    for r in recent_reports:
        recent_reports_data.append({
            "id": r.id,
            "file_name": r.file_name,
            "file_type": r.file_type,
            "status": r.status,
            "created_at": r.created_at,
            "health_score": r.prediction.health_score if r.prediction else None
        })

    # 3. Health trends over time (all completed reports)
    reports_history = db.query(Report).filter(
        Report.user_id == user_id,
        Report.status == "COMPLETED"
    ).order_by(Report.created_at.asc()).all()

    trends = []
    for r in reports_history:
        mv = r.medical_values
        pred = r.prediction
        if mv and pred:
            trends.append({
                "report_id": r.id,
                "date": r.created_at.strftime('%Y-%m-%d'),
                "health_score": pred.health_score,
                "blood_sugar": mv.blood_sugar,
                "hba1c": mv.hba1c,
                "weight": mv.weight,
                "bmi": mv.bmi,
                "systolic_bp": mv.systolic_bp,
                "diastolic_bp": mv.diastolic_bp,
                "heart_rate": mv.heart_rate,
                "spo2": mv.spo2,
                "creatinine": mv.creatinine
            })

    # 4. Comparison History (latest 3 progress trackings)
    comparisons = db.query(ComparisonHistory).filter(
        ComparisonHistory.user_id == user_id
    ).order_by(ComparisonHistory.created_at.desc()).limit(3).all()

    comparison_list = []
    for c in comparisons:
        comparison_list.append({
            "id": c.id,
            "base_report_id": c.base_report_id,
            "base_report_name": c.base_report.file_name if c.base_report else "Deleted Report",
            "compare_report_id": c.compare_report_id,
            "compare_report_name": c.compare_report.file_name if c.compare_report else "Deleted Report",
            "overall_improvement_percentage": c.overall_improvement_percentage,
            "ai_summary": c.ai_summary,
            "created_at": c.created_at
        })

    # Assemble response payload
    dashboard_payload = {
        "user_profile": {
            "full_name": current_user.full_name,
            "email": current_user.email,
            "age": current_user.age,
            "gender": current_user.gender
        },
        "current_health_score": health_score,
        "current_risks": risk_levels,
        "recent_reports": recent_reports_data,
        "health_trends": trends,
        "comparison_history": comparison_list
    }

    return success_response(
        data=dashboard_payload,
        message="Dashboard analytics summary compiled successfully."
    )
