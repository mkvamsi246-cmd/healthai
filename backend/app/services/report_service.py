import logging
import os
from fastapi import UploadFile, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.user import User
from app.models.report import Report
from app.models.medical_values import MedicalValues
from app.models.prediction import Prediction
from app.services.ocr_service import ocr_service
from app.services.extraction_service import extraction_service
from app.services.ml_service import ml_service
from app.utils.file_utils import save_uploaded_file
from app.utils.response_utils import CustomHTTPException
from app.utils.medical_utils import medical_engine

logger = logging.getLogger(__name__)

class ReportService:
    def analyze_report(self, db: Session, user: User, file: UploadFile) -> Report:
        """
        Coordinates full report analysis:
        File Save -> OCR -> Extraction -> DB Write -> ML Call -> AI Summary -> DB Update.
        """
        # 1. Save upload file
        file_name, file_path = save_uploaded_file(file, user.id)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        ext = os.path.splitext(file_name)[1]
        
        # 2. Create pending database entry
        db_report = Report(
            user_id=user.id,
            file_name=file.filename or file_name,
            file_path=file_path,
            file_type=ext.replace(".", "").upper(),
            file_size=file_size,
            status="PENDING"
        )
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        
        try:
            # 3. Execute OCR text extraction
            logger.info(f"Extracting text via OCR for report ID {db_report.id}...")
            extracted_text = ocr_service.extract_text(file_path, ext)
            db_report.extracted_text = extracted_text
            db.commit()
            
            # 4. Extract medical biomarkers
            logger.info("Extracting medical values from text...")
            extracted_values = extraction_service.extract_values(extracted_text)
            
            # Use user profile defaults for age and gender if they were not found in text
            if extracted_values.get("age") is None and user.age:
                extracted_values["age"] = user.age
            if extracted_values.get("gender") is None and user.gender:
                extracted_values["gender"] = user.gender

            # Store medical values
            db_mv = MedicalValues(
                report_id=db_report.id,
                user_id=user.id,
                **extracted_values
            )
            db.add(db_mv)
            
            # 5. Call ML module to obtain predictions
            logger.info("Calculating risk predictions via ML...")
            prediction_results = ml_service.predict(extracted_values)
            
            # Store predictions (excluding non-column attributes like feature_importance)
            db_pred_data = {k: v for k, v in prediction_results.items() if k != "feature_importance"}
            db_pred = Prediction(
                report_id=db_report.id,
                user_id=user.id,
                **db_pred_data
            )
            db.add(db_pred)
            db.commit() # commit both mv and predictions
            
            # 6. Generate AI Summary for the report
            logger.info("Synthesizing AI Summary...")
            ai_summary = self._generate_report_ai_summary(
                extracted_values, prediction_results
            )
            
            # 7. Complete the report analysis
            db_report.ai_summary = ai_summary
            db_report.status = "COMPLETED"
            db.commit()
            db.refresh(db_report)
            
            logger.info(f"Successfully finalized analysis for report ID {db_report.id}.")
            return db_report
            
        except Exception as e:
            logger.error(f"Failed analyzing report ID {db_report.id}: {e}")
            db_report.status = "FAILED"
            db.commit()
            raise CustomHTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Report analysis pipeline crashed: {str(e)}",
                error_code="REPORT_ANALYSIS_FAILED"
            )

    def _generate_report_ai_summary(self, values: dict, predictions: dict) -> str:
        """
        Builds a customized, cohesive paragraph explanation of the report.
        """
        score = predictions.get("health_score", 100)
        summary_points = []
        
        # Introduction
        summary_points.append(
            f"Based on the clinical parameters extracted, the overall Health Score is calculated at {score}/100. "
        )

        # Risk breakdown
        risks = []
        if predictions.get("heart_disease_risk") == "HIGH": risks.append("heart disease")
        if predictions.get("diabetes_risk") == "HIGH": risks.append("diabetes")
        if predictions.get("kidney_disease_risk") == "HIGH": risks.append("chronic kidney disease")
        if predictions.get("stroke_risk") == "HIGH": risks.append("stroke")
        
        borderlines = []
        if predictions.get("heart_disease_risk") == "BORDERLINE": borderlines.append("heart disease")
        if predictions.get("diabetes_risk") == "BORDERLINE": borderlines.append("diabetes")
        if predictions.get("kidney_disease_risk") == "BORDERLINE": borderlines.append("kidney disease")
        if predictions.get("stroke_risk") == "BORDERLINE": borderlines.append("stroke")

        if risks:
            summary_points.append(f"A HIGH risk profile has been predicted for: {', '.join(risks)}. ")
        if borderlines:
            summary_points.append(f"BORDERLINE risk thresholds were noted for: {', '.join(borderlines)}. ")
        if not risks and not borderlines:
            summary_points.append("All primary disease risk vectors are within LOW parameters. ")

        # Out of bounds check
        abnormal = []
        for k, v in values.items():
            if k in ("age", "gender", "systolic_bp", "diastolic_bp"):
                continue
            if v is not None:
                status = medical_engine.get_parameter_status(k, v)
                if status in ("HIGH", "LOW"):
                    name = medical_engine.reference_data.get(k, {}).get("name", k.replace("_", " ").title())
                    abnormal.append(f"{name} ({v})")
                    
        # Check Blood Pressure
        sys, dia = values.get("systolic_bp"), values.get("diastolic_bp")
        if sys is not None and dia is not None:
            bp_eval = medical_engine.evaluate_blood_pressure(sys, dia)
            if "HIGH" in bp_eval["status"] or "BORDERLINE" in bp_eval["status"]:
                abnormal.append(f"Blood Pressure ({sys}/{dia} mmHg)")

        if abnormal:
            summary_points.append(
                f"Physiological values requiring immediate adjustment include: {', '.join(abnormal)}. "
            )
        else:
            summary_points.append("All individual biomarkers analyzed fall within healthy reference ranges. ")

        # Clinical wrap-up
        if score < 70:
            summary_points.append(
                "A medical review of these findings is highly advised to explore pharmacological or lifestyle therapies."
            )
        elif score < 85:
            summary_points.append(
                "Implementing regular physical training, dietary changes, and weight controls is recommended to optimize score benchmarks."
            )
        else:
            summary_points.append(
                "Excellent status. Continue active cardio routines, balanced meals, and regular health assessments."
            )

        return "".join(summary_points)

report_service = ReportService()
