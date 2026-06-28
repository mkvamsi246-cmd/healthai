import os
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, List

# Resolve base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "health_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "models", "feature_scaler.pkl")
ENCODER_PATH = os.path.join(BASE_DIR, "models", "label_encoders.pkl")

# Alternative path check (root ml/ folder)
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = os.path.join(BASE_DIR, "health_model.pkl")
if not os.path.exists(SCALER_PATH):
    SCALER_PATH = os.path.join(BASE_DIR, "feature_scaler.pkl")
if not os.path.exists(ENCODER_PATH):
    ENCODER_PATH = os.path.join(BASE_DIR, "label_encoders.pkl")

# Global loaded artifacts
_model_bundle = None
_scaler = None
_label_encoders = None

def _load_artifacts():
    global _model_bundle, _scaler, _label_encoders
    if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH) and os.path.exists(ENCODER_PATH):
        try:
            _model_bundle = joblib.load(MODEL_PATH)
            _scaler = joblib.load(SCALER_PATH)
            _label_encoders = joblib.load(ENCODER_PATH)
        except Exception as e:
            print(f"Error loading binary files in ml/predict.py: {e}")

# Load model files on initial import
_load_artifacts()

def predict_health_risk(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Exposes predict_health_risk(data) for direct FastAPI backend integrations.
    Returns predicted risk levels, health score, and top risk factors.
    """
    global _model_bundle, _scaler, _label_encoders
    
    # Check if models are loaded. If not, reload once
    if _model_bundle is None:
        _load_artifacts()

    # Pre-process raw fields (casing tolerant)
    from ml.feature_engineering import feature_engineer
    
    # 1. Feature Engineering
    engineered_record = feature_engineer.add_features_dict(data)
    
    # 2. Pre-process and scale values if models exist
    has_model = (_model_bundle is not None and _scaler is not None)
    
    feature_names = [
        "Age", "Gender", "Height", "Weight", "BMI", "Heart Rate", "Systolic BP", "Diastolic BP", 
        "Blood Sugar", "HbA1c", "HDL", "LDL", "Total Cholesterol", "Triglycerides", 
        "Creatinine", "Hemoglobin", "SpO₂", "Smoking", "Alcohol", "Exercise", "Family History",
        "Pulse Pressure", "MAP", "Health Index", "Risk Score"
    ]
    
    # Populate missing keys with default baselines
    baselines = {
        "Age": 35, "Gender": "Male", "Height": 170.0, "Weight": 70.0, "BMI": 24.2, 
        "Heart Rate": 72, "Systolic BP": 120, "Diastolic BP": 80, "Blood Sugar": 85.0, 
        "HbA1c": 5.0, "HDL": 50.0, "LDL": 100.0, "Total Cholesterol": 170.0, "Triglycerides": 120.0, 
        "Creatinine": 0.85, "Hemoglobin": 14.5, "SpO₂": 98.0, "Smoking": 0, "Alcohol": 0, 
        "Exercise": 1, "Family History": 0, "Pulse Pressure": 40, "MAP": 93.3, 
        "Health Index": 10.0, "Risk Score": 0.1
    }

    record_filled = {}
    for feat in feature_names:
        val = engineered_record.get(feat)
        if val is None or (isinstance(val, float) and pd.isna(val)):
            val = baselines[feat]
        record_filled[feat] = val

    # Pre-encode Gender directly on the python value before creating DataFrame to satisfy Pandas 3.0 types
    gender_raw = str(record_filled["Gender"]).strip().capitalize()
    if _label_encoders and "Gender" in _label_encoders:
        le = _label_encoders["Gender"]
        if gender_raw in le.classes_:
            gender_encoded = int(le.transform([gender_raw])[0])
        else:
            gender_encoded = int(le.transform([le.classes_[0]])[0])
    else:
        gender_encoded = 1 if gender_raw == "Male" else 0

    record_filled["Gender"] = gender_encoded

    # Convert to single-row DataFrame
    df_rec = pd.DataFrame([record_filled])

    # Reorder columns to match scaler fit format
    scaler_feature_names = [
        "Age", "Height", "Weight", "BMI", "Heart Rate", "Systolic BP", "Diastolic BP", 
        "Blood Sugar", "HbA1c", "HDL", "LDL", "Total Cholesterol", "Triglycerides", 
        "Creatinine", "Hemoglobin", "SpO₂", "Pulse Pressure", "MAP", "Health Index", "Risk Score"
    ]
    
    df_num = df_rec[scaler_feature_names].copy()
    
    # Scale numerical fields
    if _scaler:
        scaled_vals = _scaler.transform(df_num)
        df_rec[scaler_feature_names] = scaled_vals

    # Prepare features for model prediction
    # Combine (Gender, features, binary) in the exact order the training model expects
    training_feature_cols = [
        "Age", "Gender", "Height", "Weight", "BMI", "Heart Rate", "Systolic BP", "Diastolic BP", 
        "Blood Sugar", "HbA1c", "HDL", "LDL", "Total Cholesterol", "Triglycerides", 
        "Creatinine", "Hemoglobin", "SpO₂", "Smoking", "Alcohol", "Exercise", "Family History",
        "Pulse Pressure", "MAP", "Health Index", "Risk Score"
    ]
    
    X_input = df_rec[training_feature_cols]

    # Initialize empty predictions
    heart_disease_risk = "LOW"
    diabetes_risk = "LOW"
    kidney_disease_risk = "LOW"
    stroke_risk = "LOW"

    # Make Model Predictions if model exists
    if has_model and _model_bundle:
        try:
            estimators = _model_bundle["estimators"]
            # Predict values (0, 1, 2)
            mapping = {0: "LOW", 1: "BORDERLINE", 2: "HIGH"}
            
            heart_disease_risk = mapping.get(int(estimators["heart_disease_risk"].predict(X_input)[0]), "LOW")
            diabetes_risk = mapping.get(int(estimators["diabetes_risk"].predict(X_input)[0]), "LOW")
            kidney_disease_risk = mapping.get(int(estimators["kidney_disease_risk"].predict(X_input)[0]), "LOW")
            stroke_risk = mapping.get(int(estimators["stroke_risk"].predict(X_input)[0]), "LOW")
        except Exception as e:
            print(f"Prediction fallback due to error: {e}")
            # Dynamic fallback checks
            pass

    # 3. Calculate Clinical Health Score (0-100)
    health_score = _calculate_health_score(record_filled)

    # 4. Feature Importance Explanations (SHAP analysis & Fallback)
    feature_importance = _explain_risk_factors(record_filled, X_input, has_model)

    return {
        "heart_disease_risk": heart_disease_risk,
        "diabetes_risk": diabetes_risk,
        "kidney_disease_risk": kidney_disease_risk,
        "stroke_risk": stroke_risk,
        "health_score": int(health_score),
        "feature_importance": feature_importance
    }

def _calculate_health_score(vals: Dict[str, Any]) -> int:
    score = 100
    
    bs = vals.get("Blood Sugar", 85)
    hb = vals.get("HbA1c", 5.0)
    sys = vals.get("Systolic BP", 120)
    dia = vals.get("Diastolic BP", 80)
    bmi = vals.get("BMI", 24.0)
    hdl = vals.get("HDL", 50)
    ldl = vals.get("LDL", 100)
    tg = vals.get("Triglycerides", 120)
    creat = vals.get("Creatinine", 0.85)
    hem = vals.get("Hemoglobin", 14.5)
    hr = vals.get("Heart Rate", 72)

    # 1. Blood sugar & HbA1c
    if bs >= 126 or hb >= 6.5: score -= 15
    elif bs >= 100 or hb >= 5.7: score -= 5
    elif bs < 70: score -= 10
    
    # 2. Blood Pressure
    if sys >= 180 or dia >= 120: score -= 20
    elif sys >= 140 or dia >= 90: score -= 10
    elif sys >= 130 or dia >= 80: score -= 5
    elif sys < 90 or dia < 60: score -= 5
    
    # 3. BMI
    if bmi >= 30.0: score -= 10
    elif bmi >= 25.0: score -= 5
    elif bmi < 18.5: score -= 5
    
    # 4. Lipids
    if hdl < 40: score -= 10
    if ldl >= 160: score -= 10
    elif ldl >= 130: score -= 5
    if tg >= 200: score -= 10
    elif tg >= 150: score -= 5
    
    # 5. Kidney Creatinine
    if creat >= 1.5: score -= 20
    elif creat >= 1.2: score -= 10
    
    # 6. Hemoglobin
    if hem < 12.0: score -= 10
    elif hem > 17.5: score -= 5
    
    # 7. Heart Rate
    if hr < 50 or hr > 100: score -= 5

    return max(10, min(100, score))

def _explain_risk_factors(vals: Dict[str, Any], X_input: pd.DataFrame, has_model: bool) -> List[str]:
    """
    Returns list of the top risk factors. Use SHAP explainer if model is loaded,
    with a fast medical range analyzer fallback.
    """
    top_factors = []
    
    # Run SHAP explainer if shap library is available and models are present
    if has_model and _model_bundle:
        try:
            import shap
            estimators = _model_bundle["estimators"]
            # We construct explainer for our diabetes or heart model
            # We select the diabetes model as a representative for explanations
            model = estimators["diabetes_risk"]
            
            # Simple check if estimator has shap explainer compatibility
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X_input)
            
            # Retrieve feature importances for this single row
            # shape could be (n_classes, n_features) or (n_features,)
            if isinstance(shap_values, list):
                # multi-class list of arrays
                # Sum absolute shap values across classes to find high impacts
                row_shap = np.sum([np.abs(arr[0]) for arr in shap_values], axis=0)
            else:
                row_shap = np.abs(shap_values[0])
                
            sorted_idx = np.argsort(row_shap)[::-1]
            feature_names = _model_bundle["feature_names"]
            
            # Map top 4 features to verbal explanations
            for idx in sorted_idx[:5]:
                feat_name = feature_names[idx]
                feat_val = vals.get(feat_name)
                
                explanation = _map_feature_to_explanation(feat_name, feat_val)
                if explanation and explanation not in top_factors:
                    top_factors.append(explanation)
        except Exception:
            # Revert to clean rule-based fallback
            pass

    # Rule-based fallback (if SHAP is not installed, throws error, or is slow)
    if not top_factors:
        # Check standard biomarkers and append warning descriptions
        if vals.get("HbA1c", 5.0) >= 5.7: top_factors.append("High HbA1c")
        if vals.get("Blood Sugar", 85.0) >= 100: top_factors.append("High Blood Sugar")
        if vals.get("LDL", 100.0) >= 130: top_factors.append("High LDL")
        if vals.get("Systolic BP", 120) >= 130 or vals.get("Diastolic BP", 80) >= 80: top_factors.append("High Blood Pressure")
        if vals.get("BMI", 24.0) >= 25.0: top_factors.append("High BMI")
        if vals.get("Creatinine", 0.85) >= 1.2: top_factors.append("High Creatinine")
        if vals.get("Triglycerides", 120.0) >= 150: top_factors.append("High Triglycerides")
        if vals.get("SpO₂", 98.0) < 95: top_factors.append("Low Oxygen Saturation")
        if vals.get("Smoking") == 1: top_factors.append("Smoking Habitation")
        if vals.get("Family History") == 1: top_factors.append("Family Disease History")

    # If everything is perfectly normal
    if not top_factors:
        top_factors = ["Optimal Bio-parameters"]

    return top_factors[:4]

def _map_feature_to_explanation(feat_name: str, val: Any) -> str:
    if val is None:
        return ""
    
    if feat_name == "HbA1c" and val >= 5.7: return "High HbA1c"
    elif feat_name == "Blood Sugar" and val >= 100: return "High Blood Sugar"
    elif feat_name == "LDL" and val >= 130: return "High LDL"
    elif feat_name in ("Systolic BP", "Diastolic BP", "MAP", "Pulse Pressure") and val > 130: return "High Blood Pressure"
    elif feat_name == "BMI" and val >= 25.0: return "High BMI"
    elif feat_name == "Creatinine" and val >= 1.2: return "High Creatinine"
    elif feat_name == "Triglycerides" and val >= 150: return "High Triglycerides"
    elif feat_name == "SpO₂" and val < 95: return "Low Oxygen Saturation"
    elif feat_name == "Age" and val >= 55: return "Advanced Age"
    elif feat_name == "Smoking" and val == 1: return "Smoking Habitation"
    elif feat_name == "Family History" and val == 1: return "Family Disease History"
    
    return ""
