import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ExtractionService:
    def extract_values(self, text: str) -> Dict[str, Any]:
        """
        Parses text for medical values using regex pattern mapping.
        Returns a dictionary containing all extracted parameters.
        """
        extracted = {
            "age": self._extract_age(text),
            "gender": self._extract_gender(text),
            "blood_sugar": self._extract_blood_sugar(text),
            "hba1c": self._extract_hba1c(text),
            "systolic_bp": None,
            "diastolic_bp": None,
            "heart_rate": self._extract_heart_rate(text),
            "spo2": self._extract_spo2(text),
            "hdl": self._extract_lipid(text, r"\bHDL\b"),
            "ldl": self._extract_lipid(text, r"\bLDL\b"),
            "triglycerides": self._extract_lipid(text, r"\bTriglycerides\b|\bTG\b"),
            "total_cholesterol": self._extract_lipid(text, r"Total\s+Cholesterol|\bCholesterol\b"),
            "creatinine": self._extract_creatinine(text),
            "hemoglobin": self._extract_hemoglobin(text),
            "weight": self._extract_weight(text),
            "bmi": self._extract_bmi(text)
        }

        # Handle joint Blood Pressure extraction
        systolic, diastolic = self._extract_blood_pressure(text)
        extracted["systolic_bp"] = systolic
        extracted["diastolic_bp"] = diastolic

        logger.info(f"Extracted parameters: {extracted}")
        return extracted

    def _extract_age(self, text: str) -> Optional[int]:
        # Matches: "Age: 45", "Age 45", "45 Years", "45 Yrs"
        patterns = [
            r"age\s*[:\-]?\s*(\d{1,3})",
            r"(\d{1,3})\s*(?:years|yrs)\s*(?:old)?",
            r"(?:patient\s+age)\s*[:\-]?\s*(\d{1,3})"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                val = int(match.group(1))
                if 0 <= val <= 120:
                    return val
        return None

    def _extract_gender(self, text: str) -> Optional[str]:
        # Matches: "Gender: Male", "Sex: Female", etc.
        patterns = [
            r"gender\s*[:\-]?\s*(male|female|other)",
            r"sex\s*[:\-]?\s*(male|female|other)",
            r"\b(male|female)\b"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                val = match.group(1).strip().capitalize()
                return val
        return None

    def _extract_blood_sugar(self, text: str) -> Optional[float]:
        # Matches fasting blood sugar, random glucose
        # e.g., "Fasting Blood Sugar: 95 mg/dL", "Glucose, Fasting: 105", "Blood Sugar 90"
        patterns = [
            r"(?:fasting\s+)?glucose\s*(?:\(fasting\))?\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(?:mg/dl)?",
            r"blood\s+sugar\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(?:mg/dl)?",
            r"fasting\s+blood\s+sugar\s*[:\-]?\s*(\d+(?:\.\d+)?)"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    val = float(match.group(1))
                    if 30 <= val <= 600:
                        return val
                except ValueError:
                    continue
        return None

    def _extract_hba1c(self, text: str) -> Optional[float]:
        # Matches: "HbA1c: 5.7%", "A1c: 6.0", "Glycated Hemoglobin: 5.8"
        patterns = [
            r"hba1c\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*%?",
            r"glycated\s+hemoglobin\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*%?",
            r"\ba1c\b\s*[:\-]?\s*(\d+(?:\.\d+)?)"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    val = float(match.group(1))
                    if 3.0 <= val <= 20.0:
                        return val
                except ValueError:
                    continue
        return None

    def _extract_blood_pressure(self, text: str) -> tuple[Optional[int], Optional[int]]:
        # Matches: "120/80", "120 / 80 mmHg", "BP: 130/85"
        patterns = [
            r"bp\s*[:\-]?\s*(\d{2,3})\s*/\s*(\d{2,3})",
            r"blood\s+pressure\s*[:\-]?\s*(\d{2,3})\s*/\s*(\d{2,3})",
            r"\b(\d{2,3})\s*/\s*(\d{2,3})\s*mm\s*hg",
            r"\b(\d{2,3})\s*/\s*(\d{2,3})\b"
        ]
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                try:
                    sys_val = int(match.group(1))
                    dia_val = int(match.group(2))
                    if 50 <= sys_val <= 250 and 30 <= dia_val <= 150:
                        return sys_val, dia_val
                except ValueError:
                    continue
        return None, None

    def _extract_heart_rate(self, text: str) -> Optional[int]:
        # Matches: "Heart Rate: 72 bpm", "Pulse: 80", "HR 75"
        patterns = [
            r"heart\s+rate\s*[:\-]?\s*(\d{2,3})\s*(?:bpm|beats)?",
            r"pulse\s*(?:rate)?\s*[:\-]?\s*(\d{2,3})\s*(?:bpm)?",
            r"\bhr\b\s*[:\-]?\s*(\d{2,3})\s*(?:bpm)?"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    val = int(match.group(1))
                    if 30 <= val <= 250:
                        return val
                except ValueError:
                    continue
        return None

    def _extract_spo2(self, text: str) -> Optional[float]:
        # Matches: "SpO2: 98%", "Oxygen Saturation: 99%"
        patterns = [
            r"spo2\s*[:\-]?\s*(\d{2,3})\s*%?",
            r"oxygen\s+saturation\s*[:\-]?\s*(\d{2,3})\s*%?",
            r"pulse\s+oximetry\s*[:\-]?\s*(\d{2,3})\s*%?"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    val = float(match.group(1))
                    if 50 <= val <= 100:
                        return val
                except ValueError:
                    continue
        return None

    def _extract_lipid(self, text: str, label_pattern: str) -> Optional[float]:
        # Matches lipids like HDL, LDL, Triglycerides, Total Cholesterol
        # Standard format: Name [spaces/colon] Value [spaces/unit]
        patterns = [
            rf"(?:{label_pattern})\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(?:mg/dl)?",
            rf"(\d+(?:\.\d+)?)\s*(?:mg/dl)?\s*(?:for|of)?\s*(?:{label_pattern})"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    val = float(match.group(1))
                    if 10 <= val <= 1000:
                        return val
                except ValueError:
                    continue
        return None

    def _extract_creatinine(self, text: str) -> Optional[float]:
        # Matches: "Creatinine: 0.9 mg/dL", "Serum Creatinine: 1.1"
        patterns = [
            r"creatinine\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(?:mg/dl)?",
            r"serum\s+creatinine\s*[:\-]?\s*(\d+(?:\.\d+)?)"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    val = float(match.group(1))
                    if 0.1 <= val <= 15.0:
                        return val
                except ValueError:
                    continue
        return None

    def _extract_hemoglobin(self, text: str) -> Optional[float]:
        # Matches: "Hemoglobin: 14.5 g/dL", "Hb: 13.2"
        patterns = [
            r"hemoglobin\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(?:g/dl|gm/dl)?",
            r"\bhb\b\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(?:g/dl|gm/dl)?"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    val = float(match.group(1))
                    if 2.0 <= val <= 25.0:
                        return val
                except ValueError:
                    continue
        return None

    def _extract_weight(self, text: str) -> Optional[float]:
        # Matches: "Weight: 72.5 kg", "Weight: 160 lbs"
        patterns = [
            r"weight\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(?:kg|lbs)?",
            r"wt\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(?:kg|lbs)?"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    val = float(match.group(1))
                    # Handle lb conversion to kg if text mentions 'lbs' or 'lb'
                    unit_match = re.search(rf"{pattern}\s*(lbs|lb)", text, re.IGNORECASE)
                    if unit_match:
                        val = val * 0.45359237 # Convert lbs to kg
                    if 10 <= val <= 350:
                        return round(val, 2)
                except ValueError:
                    continue
        return None

    def _extract_bmi(self, text: str) -> Optional[float]:
        # Matches: "BMI: 24.5", "Body Mass Index: 28.2"
        patterns = [
            r"bmi\s*[:\-]?\s*(\d+(?:\.\d+)?)",
            r"body\s+mass\s+index\s*[:\-]?\s*(\d+(?:\.\d+)?)"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    val = float(match.group(1))
                    if 10.0 <= val <= 60.0:
                        return val
                except ValueError:
                    continue
        return None

extraction_service = ExtractionService()
