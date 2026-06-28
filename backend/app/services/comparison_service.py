import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.report import Report
from app.models.comparison import ComparisonHistory
from app.schemas.comparison import CompareItem, ReportComparisonResponse
from app.utils.response_utils import CustomHTTPException

logger = logging.getLogger(__name__)

class ComparisonService:
    def compare_reports(self, db: Session, user_id: int, base_id: int, compare_id: int) -> ComparisonHistory:
        """
        Compares base_report_id (older) against compare_report_id (newer).
        Saves the comparison result and generates a summary.
        """
        # Fetch reports
        base_report = db.query(Report).filter(Report.id == base_id, Report.user_id == user_id).first()
        compare_report = db.query(Report).filter(Report.id == compare_id, Report.user_id == user_id).first()
        
        if not base_report or not compare_report:
            raise CustomHTTPException(
                status_code=404,
                detail="One or both reports do not exist or do not belong to the user.",
                error_code="REPORT_NOT_FOUND"
            )
            
        if not base_report.medical_values or not compare_report.medical_values:
            raise CustomHTTPException(
                status_code=400,
                detail="One or both reports do not contain extracted medical values for comparison.",
                error_code="INCOMPLETE_REPORT_VALUES"
            )
            
        if not base_report.prediction or not compare_report.prediction:
            raise CustomHTTPException(
                status_code=400,
                detail="One or both reports do not contain prediction values for comparison.",
                error_code="INCOMPLETE_REPORT_PREDICTIONS"
            )

        # Base and Compare values
        mv_base = base_report.medical_values
        mv_compare = compare_report.medical_values
        pred_base = base_report.prediction
        pred_compare = compare_report.prediction

        # List of parameters to compare and their direction (True means higher is better, False means lower is better)
        param_configs = {
            "blood_sugar": {"label": "Blood Sugar", "higher_better": False, "unit": "mg/dL"},
            "hba1c": {"label": "HbA1c", "higher_better": False, "unit": "%"},
            "heart_rate": {"label": "Heart Rate", "higher_better": None, "unit": "bpm"}, # HR is optimal in a normal range
            "hdl": {"label": "HDL Cholesterol", "higher_better": True, "unit": "mg/dL"},
            "ldl": {"label": "LDL Cholesterol", "higher_better": False, "unit": "mg/dL"},
            "creatinine": {"label": "Creatinine", "higher_better": False, "unit": "mg/dL"},
            "bmi": {"label": "BMI", "higher_better": False, "unit": "kg/m²"},
            "weight": {"label": "Weight", "higher_better": False, "unit": "kg"},
        }

        comparison_data = {}
        improved_count = 0
        worsened_count = 0
        compared_count = 0

        # Compare single numeric parameters
        for key, conf in param_configs.items():
            val_base = getattr(mv_base, key, None)
            val_compare = getattr(mv_compare, key, None)
            
            if val_base is not None and val_compare is not None:
                compared_count += 1
                diff = round(val_compare - val_base, 2)
                
                # Check status
                if diff == 0:
                    status = "Stable"
                elif conf["higher_better"] is True:
                    if diff > 0:
                        status = "Improved"
                        improved_count += 1
                    else:
                        status = "Worsened"
                        worsened_count += 1
                elif conf["higher_better"] is False:
                    if diff < 0:
                        status = "Improved"
                        improved_count += 1
                    else:
                        status = "Worsened"
                        worsened_count += 1
                else:
                    # Heart Rate or parameters where difference direction depends on range (optimal 60-100)
                    # Simple heuristic: is it closer to 70?
                    dist_base = abs(val_base - 75)
                    dist_compare = abs(val_compare - 75)
                    if dist_compare < dist_base:
                        status = "Improved"
                        improved_count += 1
                    elif dist_compare > dist_base:
                        status = "Worsened"
                        worsened_count += 1
                    else:
                        status = "Stable"

                comparison_data[key] = {
                    "parameter": conf["label"],
                    "previous_value": val_base,
                    "current_value": val_compare,
                    "difference": diff,
                    "status": status,
                    "unit": conf["unit"]
                }

        # Compare Blood Pressure separately (Systolic and Diastolic combined)
        sys_base, dia_base = mv_base.systolic_bp, mv_base.diastolic_bp
        sys_compare, dia_compare = mv_compare.systolic_bp, mv_compare.diastolic_bp
        
        if sys_base is not None and sys_compare is not None and dia_base is not None and dia_compare is not None:
            compared_count += 1
            # Normal blood pressure target is 120/80. Let's see if the distance decreased.
            dist_base = abs(sys_base - 120) + abs(dia_base - 80)
            dist_compare = abs(sys_compare - 120) + abs(dia_compare - 80)
            diff_sys = sys_compare - sys_base
            diff_dia = dia_compare - dia_base
            
            if dist_compare < dist_base:
                bp_status = "Improved"
                improved_count += 1
            elif dist_compare > dist_base:
                bp_status = "Worsened"
                worsened_count += 1
            else:
                bp_status = "Stable"
                
            comparison_data["blood_pressure"] = {
                "parameter": "Blood Pressure",
                "previous_value": float(f"{sys_base}.{dia_base}"), # Hacky value representation for standard float field
                "current_value": float(f"{sys_compare}.{dia_compare}"),
                "difference": round(dist_base - dist_compare, 2), # positive indicates improvement (reduction of distance to optimal)
                "status": bp_status,
                "unit": "mmHg"
            }
            # Custom fields to hold printable values for rendering later
            comparison_data["blood_pressure"]["previous_str"] = f"{sys_base}/{dia_base}"
            comparison_data["blood_pressure"]["current_str"] = f"{sys_compare}/{dia_compare}"

        # Health Score Comparison
        score_base = pred_base.health_score
        score_compare = pred_compare.health_score
        
        score_diff = score_compare - score_base
        if score_diff > 0:
            score_status = "Improved"
        elif score_diff < 0:
            score_status = "Worsened"
        else:
            score_status = "Stable"
            
        comparison_data["health_score"] = {
            "parameter": "Health Score",
            "previous_value": float(score_base),
            "current_value": float(score_compare),
            "difference": float(score_diff),
            "status": score_status,
            "unit": "points"
        }

        # Calculate Overall Improvement Percentage
        # Formula: (Current Health Score - Previous Health Score) / Previous Health Score * 100
        overall_improvement = 0.0
        if score_base > 0:
            overall_improvement = round(((score_compare - score_base) / score_base) * 100, 2)

        # Generate AI Summary for comparison
        ai_summary = self._generate_comparison_ai_summary(
            comparison_data, score_base, score_compare, overall_improvement, improved_count, worsened_count
        )

        # Check if comparison already exists for this pair
        existing = db.query(ComparisonHistory).filter(
            ComparisonHistory.user_id == user_id,
            ComparisonHistory.base_report_id == base_id,
            ComparisonHistory.compare_report_id == compare_id
        ).first()

        if existing:
            existing.comparison_data = comparison_data
            existing.overall_improvement_percentage = overall_improvement
            existing.ai_summary = ai_summary
            db_comparison = existing
        else:
            db_comparison = ComparisonHistory(
                user_id=user_id,
                base_report_id=base_id,
                compare_report_id=compare_id,
                comparison_data=comparison_data,
                overall_improvement_percentage=overall_improvement,
                ai_summary=ai_summary
            )
            db.add(db_comparison)
            
        try:
            db.commit()
            db.refresh(db_comparison)
            return db_comparison
        except Exception as e:
            db.rollback()
            raise CustomHTTPException(
                status_code=500,
                detail=f"Database comparison save failed: {str(e)}",
                error_code="DB_COMPARISON_SAVE_FAILED"
            )

    def _generate_comparison_ai_summary(
        self,
        comparison_data: dict,
        score_base: int,
        score_compare: int,
        improvement_pct: float,
        improved_count: int,
        worsened_count: int
    ) -> str:
        """
        Builds a dynamic AI clinical overview of the user's progress.
        """
        summary_parts = []
        
        # Introduction
        if score_compare > score_base:
            summary_parts.append(
                f"Your overall health score increased from {score_base} to {score_compare} "
                f"(a {improvement_pct:+}% improvement). This reflects positive systemic progress."
            )
        elif score_compare < score_base:
            summary_parts.append(
                f"Your overall health score decreased from {score_base} to {score_compare} "
                f"(a {improvement_pct}% change). Several parameters indicate signs of physiological stress."
            )
        else:
            summary_parts.append(
                f"Your overall health score remained stable at {score_compare}. "
                f"Key biomarkers show steady-state maintenance."
            )

        # Parameter details
        improved_items = []
        worsened_items = []
        for k, v in comparison_data.items():
            if k == "health_score":
                continue
                
            p_name = v["parameter"]
            p_status = v["status"]
            
            # Formatting strings for output
            if k == "blood_pressure":
                prev_val = v.get("previous_str", "")
                curr_val = v.get("current_str", "")
            else:
                prev_val = f"{v['previous_value']} {v['unit']}"
                curr_val = f"{v['current_value']} {v['unit']}"
                
            item_desc = f"{p_name} ({prev_val} → {curr_val})"
            
            if p_status == "Improved":
                improved_items.append(item_desc)
            elif p_status == "Worsened":
                worsened_items.append(item_desc)

        if improved_items:
            summary_parts.append(f"Areas of improvement include: {', '.join(improved_items)}.")
        if worsened_items:
            summary_parts.append(
                f"Biomarkers requiring attention or showing regression: {', '.join(worsened_items)}. "
                f"Consider adjusting your diet and lifestyle patterns in these specific sectors."
            )
            
        # Clinical wrap-up
        if worsened_count > 0:
            summary_parts.append(
                "Focus on regular aerobic exercise and low-glycemic foods to target elevated biomarkers. "
                "Consult your doctor to evaluate the regressed parameters."
            )
        else:
            summary_parts.append(
                "Excellent work on maintaining or improving your parameters. Continue with your current healthy habits."
            )
            
        return " ".join(summary_parts)

comparison_service = ComparisonService()
