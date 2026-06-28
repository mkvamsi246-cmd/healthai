import pandas as pd
import numpy as np
from typing import Dict, Any

class FeatureEngineer:
    def add_features_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Engineers composite features from raw clinical data.
        Returns a new DataFrame containing computed columns.
        """
        df = df.copy()
        
        # 1. Height & Weight parsing for BMI
        if "BMI" not in df.columns or df["BMI"].isnull().any():
            if "Weight" in df.columns and "Height" in df.columns:
                # height is in cm
                df["BMI"] = df["Weight"] / ((df["Height"] / 100) ** 2)
                df["BMI"] = df["BMI"].round(1)
        
        # 2. Pulse Pressure
        if "Systolic BP" in df.columns and "Diastolic BP" in df.columns:
            df["Pulse Pressure"] = df["Systolic BP"] - df["Diastolic BP"]
        else:
            df["Pulse Pressure"] = 40.0 # clinical default
            
        # 3. Mean Arterial Pressure (MAP)
        if "Systolic BP" in df.columns and "Diastolic BP" in df.columns:
            df["MAP"] = df["Diastolic BP"] + (df["Pulse Pressure"] / 3.0)
            df["MAP"] = df["MAP"].round(1)
        else:
            df["MAP"] = 93.3 # clinical default

        # 4. Health Index (A metric between 0 and 10 representing healthy vital baselines)
        df["Health Index"] = self._calculate_health_index_df(df)

        # 5. Risk Score (Accumulated biomarkers risk weightings)
        df["Risk Score"] = self._calculate_risk_score_df(df)

        return df

    def _calculate_health_index_df(self, df: pd.DataFrame) -> pd.Series:
        # Higher is better: normal vitals yield higher index points
        points = pd.Series(10.0, index=df.index)
        
        # Penalize values out of range
        if "Blood Sugar" in df.columns:
            points[df["Blood Sugar"] >= 126] -= 2.0
            points[df["Blood Sugar"] < 70] -= 1.0
        if "Systolic BP" in df.columns:
            points[df["Systolic BP"] >= 140] -= 2.0
        if "Diastolic BP" in df.columns:
            points[df["Diastolic BP"] >= 90] -= 1.0
        if "BMI" in df.columns:
            points[df["BMI"] >= 30.0] -= 2.0
            points[df["BMI"] < 18.5] -= 1.0
        if "Creatinine" in df.columns:
            points[df["Creatinine"] >= 1.5] -= 2.0
        if "SpO₂" in df.columns:
            # Heavy penalty for low SpO2
            points[df["SpO₂"] < 95.0] -= (95.0 - df["SpO₂"]) * 0.5
            
        return np.clip(points, 0.0, 10.0)

    def _calculate_risk_score_df(self, df: pd.DataFrame) -> pd.Series:
        # Higher is worse: counts cumulative severe clinical thresholds
        risk = pd.Series(0.0, index=df.index)
        
        if "Age" in df.columns:
            risk += (df["Age"] / 80.0) * 0.25 # baseline age risk
        if "Smoking" in df.columns:
            risk += df["Smoking"] * 0.15
        if "Alcohol" in df.columns:
            risk += df["Alcohol"] * 0.05
        if "Family History" in df.columns:
            risk += df["Family History"] * 0.15
        if "LDL" in df.columns:
            risk[(df["LDL"] >= 130) & (df["LDL"] < 160)] += 0.1
            risk[df["LDL"] >= 160] += 0.2
        if "HbA1c" in df.columns:
            risk[(df["HbA1c"] >= 5.7) & (df["HbA1c"] < 6.5)] += 0.1
            risk[df["HbA1c"] >= 6.5] += 0.25
        if "Exercise" in df.columns:
            risk -= df["Exercise"] * 0.05 # exercise reduces risk
            
        return np.clip(risk, 0.0, 1.0)

    def add_features_dict(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Engineers features for a single input dictionary (casing independent).
        """
        # Map record keys to match training casing
        mapping = {
            "age": "Age",
            "gender": "Gender",
            "height": "Height",
            "weight": "Weight",
            "bmi": "BMI",
            "heart_rate": "Heart Rate",
            "systolic_bp": "Systolic BP",
            "diastolic_bp": "Diastolic BP",
            "blood_sugar": "Blood Sugar",
            "hba1c": "HbA1c",
            "hdl": "HDL",
            "ldl": "LDL",
            "total_cholesterol": "Total Cholesterol",
            "cholesterol": "Total Cholesterol",
            "triglycerides": "Triglycerides",
            "creatinine": "Creatinine",
            "hemoglobin": "Hemoglobin",
            "spo2": "SpO₂",
            "smoking": "Smoking",
            "alcohol": "Alcohol",
            "exercise": "Exercise",
            "family_history": "Family History"
        }
        
        cleaned = {}
        for k, v in record.items():
            k_low = str(k).lower().strip()
            if k_low in mapping:
                cleaned[mapping[k_low]] = v
            else:
                cleaned[k] = v

        # Calculate values
        # Default missing vitals if not supplied
        height = cleaned.get("Height", 170.0)
        weight = cleaned.get("Weight", 70.0)
        
        if "BMI" not in cleaned or cleaned["BMI"] is None:
            cleaned["BMI"] = round(weight / ((height / 100) ** 2), 1)

        sys = cleaned.get("Systolic BP", 120)
        dia = cleaned.get("Diastolic BP", 80)
        cleaned["Pulse Pressure"] = sys - dia
        cleaned["MAP"] = round(dia + (cleaned["Pulse Pressure"] / 3.0), 1)

        # 4. Health Index (scalar)
        h_points = 10.0
        if "Blood Sugar" in cleaned and cleaned["Blood Sugar"] is not None:
            if cleaned["Blood Sugar"] >= 126: h_points -= 2.0
            elif cleaned["Blood Sugar"] < 70: h_points -= 1.0
        if "Systolic BP" in cleaned and cleaned["Systolic BP"] is not None:
            if cleaned["Systolic BP"] >= 140: h_points -= 2.0
        if "Diastolic BP" in cleaned and cleaned["Diastolic BP"] is not None:
            if cleaned["Diastolic BP"] >= 90: h_points -= 1.0
        if "BMI" in cleaned and cleaned["BMI"] is not None:
            if cleaned["BMI"] >= 30.0: h_points -= 2.0
            elif cleaned["BMI"] < 18.5: h_points -= 1.0
        if "Creatinine" in cleaned and cleaned["Creatinine"] is not None:
            if cleaned["Creatinine"] >= 1.5: h_points -= 2.0
        if "SpO₂" in cleaned and cleaned["SpO₂"] is not None:
            if cleaned["SpO₂"] < 95.0: h_points -= (95.0 - cleaned["SpO₂"]) * 0.5
            
        cleaned["Health Index"] = max(0.0, min(10.0, h_points))

        # 5. Risk Score (scalar)
        r_points = 0.0
        if "Age" in cleaned and cleaned["Age"] is not None:
            r_points += (cleaned["Age"] / 80.0) * 0.25
        if cleaned.get("Smoking") == 1:
            r_points += 0.15
        if cleaned.get("Alcohol") == 1:
            r_points += 0.05
        if cleaned.get("Family History") == 1:
            r_points += 0.15
        if "LDL" in cleaned and cleaned["LDL"] is not None:
            if cleaned["LDL"] >= 160: r_points += 0.2
            elif cleaned["LDL"] >= 130: r_points += 0.1
        if "HbA1c" in cleaned and cleaned["HbA1c"] is not None:
            if cleaned["HbA1c"] >= 6.5: r_points += 0.25
            elif cleaned["HbA1c"] >= 5.7: r_points += 0.1
        if cleaned.get("Exercise") == 1:
            r_points -= 0.05
            
        cleaned["Risk Score"] = max(0.0, min(1.0, r_points))
        
        return cleaned

feature_engineer = FeatureEngineer()
