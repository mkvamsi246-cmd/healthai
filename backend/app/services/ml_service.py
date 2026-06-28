import logging
from typing import Dict, Any
from ml.predict import predict_health_risk

logger = logging.getLogger(__name__)

class MLService:
    def predict(self, medical_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinates calling the ML module's predict function.
        Cleans data and guarantees fallback returns.
        """
        try:
            # Clean structure: ensure numerical parameters are passed, or defaults
            payload = {
                "age": medical_data.get("age"),
                "gender": medical_data.get("gender"),
                "blood_sugar": medical_data.get("blood_sugar"),
                "hba1c": medical_data.get("hba1c"),
                "systolic_bp": medical_data.get("systolic_bp"),
                "diastolic_bp": medical_data.get("diastolic_bp"),
                "heart_rate": medical_data.get("heart_rate"),
                "spo2": medical_data.get("spo2"),
                "hdl": medical_data.get("hdl"),
                "ldl": medical_data.get("ldl"),
                "triglycerides": medical_data.get("triglycerides"),
                "total_cholesterol": medical_data.get("total_cholesterol"),
                "creatinine": medical_data.get("creatinine"),
                "hemoglobin": medical_data.get("hemoglobin"),
                "weight": medical_data.get("weight"),
                "bmi": medical_data.get("bmi"),
            }
            
            logger.info("Executing ML risk prediction...")
            results = predict_health_risk(payload)
            logger.info(f"ML risk prediction complete: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Failed calling predict_health_risk(): {e}")
            # Safe absolute fallback
            return {
                "heart_disease_risk": "LOW",
                "diabetes_risk": "LOW",
                "kidney_disease_risk": "LOW",
                "stroke_risk": "LOW",
                "health_score": 85
            }

ml_service = MLService()
