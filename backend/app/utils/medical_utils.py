import json
import os
from typing import Dict, Any, Optional
from app.config import settings

class MedicalKnowledgeEngine:
    def __init__(self):
        self.reference_data: Dict[str, Any] = {}
        self.load_reference()

    def load_reference(self):
        json_path = settings.knowledge_path / "medical_reference.json"
        try:
            with open(json_path, "r") as f:
                self.reference_data = json.load(f)
        except Exception:
            # Fallback configuration to prevent crash if JSON is missing
            self.reference_data = {}

    def get_parameter_status(self, parameter: str, value: Optional[float]) -> str:
        """
        Determines if a value is LOW, NORMAL, BORDERLINE, or HIGH based on reference ranges.
        """
        if value is None or parameter not in self.reference_data:
            return "UNKNOWN"
            
        param_info = self.reference_data[parameter]
        ranges = param_info.get("ranges", {})
        
        # Check Low
        if "low" in ranges and "max" in ranges["low"]:
            if value < ranges["low"]["max"]:
                return "LOW"
                
        # Check High
        if "high" in ranges and "min" in ranges["high"]:
            if value >= ranges["high"]["min"]:
                return "HIGH"
                
        # Check Borderline
        if "borderline" in ranges:
            r_min = ranges["borderline"].get("min")
            r_max = ranges["borderline"].get("max")
            if r_min is not None and r_max is not None:
                if r_min <= value <= r_max:
                    return "BORDERLINE"
            elif r_min is not None and value >= r_min:
                return "BORDERLINE"
            elif r_max is not None and value <= r_max:
                return "BORDERLINE"
                
        # Check Normal
        if "normal" in ranges:
            r_min = ranges["normal"].get("min")
            r_max = ranges["normal"].get("max")
            if r_min is not None and r_max is not None:
                if r_min <= value <= r_max:
                    return "NORMAL"
                    
        return "NORMAL"

    def get_parameter_details(self, parameter: str, value: Optional[float]) -> Dict[str, Any]:
        """
        Returns full analysis details for a specific parameter value.
        """
        if parameter not in self.reference_data:
            return {
                "name": parameter.replace("_", " ").title(),
                "value": value,
                "status": "UNKNOWN",
                "unit": "",
                "meaning": "",
                "fact": "",
                "risk": "",
                "lifestyle_suggestion": "",
                "doctor_advice": ""
            }
            
        param_info = self.reference_data[parameter]
        status = self.get_parameter_status(parameter, value)
        
        # Resolve risks and recommendations based on value direction
        risks_dict = param_info.get("possible_risks", {})
        recs_dict = param_info.get("lifestyle_recommendations", {})
        
        risk_key = "high" if status in ("HIGH", "BORDERLINE") else "low"
        risk = risks_dict.get(risk_key, risks_dict.get("high", ""))
        suggestion = recs_dict.get(risk_key, recs_dict.get("high", ""))
        
        if status == "NORMAL":
            risk = "No elevated risk identified. Keep up the healthy habits."
            suggestion = "Continue maintaining your active lifestyle and balanced nutrition."

        return {
            "name": param_info.get("name", parameter.replace("_", " ").title()),
            "value": value,
            "status": status,
            "unit": param_info.get("unit", ""),
            "meaning": param_info.get("meaning", ""),
            "fact": param_info.get("health_facts", ""),
            "risk": risk,
            "lifestyle_suggestion": suggestion,
            "doctor_advice": param_info.get("doctor_consultation_advice", "")
        }

    def evaluate_blood_pressure(self, systolic: Optional[int], diastolic: Optional[int]) -> Dict[str, Any]:
        """
        Jointly evaluates systolic and diastolic BP.
        """
        if systolic is None or diastolic is None:
            return {
                "status": "UNKNOWN",
                "risk": "Incomplete blood pressure readings.",
                "suggestion": "Ensure both systolic and diastolic blood pressure are recorded."
            }

        # Categories: Normal, Elevated, Stage 1 Hypertension, Stage 2 Hypertension, Hypertensive Crisis
        if systolic >= 180 or diastolic >= 120:
            return {
                "status": "HIGH (Hypertensive Crisis)",
                "risk": "Extreme stroke and cardiac event hazard.",
                "suggestion": "Seek immediate medical attention. Rest and re-measure. Avoid physical exertion."
            }
        elif systolic >= 140 or diastolic >= 90:
            return {
                "status": "HIGH (Stage 2 Hypertension)",
                "risk": "High long-term cardiovascular and stroke risks.",
                "suggestion": "Adopt DASH diet, reduce sodium intake, limit caffeine/alcohol, engage in aerobic exercise daily."
            }
        elif (130 <= systolic <= 139) or (80 <= diastolic <= 89):
            return {
                "status": "BORDERLINE (Stage 1 Hypertension)",
                "risk": "Increased arterial strain, precursor to severe hypertension.",
                "suggestion": "Cut salt intake, lose excess weight, do regular moderate cardiovascular workouts."
            }
        elif (120 <= systolic <= 129) and diastolic < 80:
            return {
                "status": "BORDERLINE (Elevated)",
                "risk": "Slightly elevated blood pressure, can progress to high blood pressure over time.",
                "suggestion": "Monitor weekly, practice stress reduction, improve dietary fiber."
            }
        elif systolic < 90 or diastolic < 60:
            return {
                "status": "LOW (Hypotension)",
                "risk": "Possible inadequate oxygen transport causing dizziness or fatigue.",
                "suggestion": "Ensure proper hydration. Rest when dizzy. Eat adequate levels of salt."
            }
        else:
            return {
                "status": "NORMAL",
                "risk": "Healthy vascular system pressure.",
                "suggestion": "Maintain physical activity and a balanced diet low in saturated fats."
            }

medical_engine = MedicalKnowledgeEngine()
