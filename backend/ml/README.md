# HealthInsight AI - Machine Learning Pipeline

This module houses the machine learning models and pipeline for predicting cardiovascular, diabetic, renal, and stroke risk levels from clinical indicators.

---

## Folder Structure
- `datasets/`
  - `generate_synthetic_data.py`: Creates a realistic patient cohort CSV.
  - `merged_dataset.csv`: Compiled clinical records.
- `training/`
  - `train_model.py`: Orchestrates multi-model comparisons and selects the best estimator.
- `models/`: Saves the final compiled serializations (`health_model.pkl`, `feature_scaler.pkl`, `label_encoders.pkl`).
- `results/`: Contains text summaries and plots (heatmaps, ROC curves, confusion matrices).
- `preprocessing.py`: Implements numerical scalers and label encoders.
- `feature_engineering.py`: Computes composite indicators (MAP, Pulse Pressure, Health Index, Risk Score).
- `evaluate.py`: Formulates evaluation tables and plots.
- `predict.py`: Exposes `predict_health_risk(data)`.

---

## Pipeline Setup & Execution

### 1. Install Dependencies
```bash
# From the backend directory
pip install -r ml/requirements.txt
```

### 2. Generate Synthetic Patient Dataset
Run the data generator to create a 2,200+ patient dataset matching clinical distributions:
```bash
python ml/datasets/generate_synthetic_data.py
```

### 3. Run Pipeline Training & Selection
Compare model accuracy and macro F1 scores across Random Forest, XGBoost, SVM, Decision Tree, Extra Trees, and Logistic Regression, then save the best model:
```bash
python ml/training/train_model.py
```

Training will:
1. Engineer vital characteristics (BMI, MAP, Pulse Pressure).
2. Clean and impute empty items.
3. Balance classes using SMOTE.
4. Auto-select the winning estimator.
5. Save model weights to `ml/models/` and `ml/`.
6. Output evaluation charts to `ml/results/`.

---

## FastAPI Backend Integration
The FastAPI backend interfaces directly with this module by importing:
```python
from ml.predict import predict_health_risk
```
And passes structured clinical measurements:
```python
result = predict_health_risk({
    "age": 45,
    "gender": "Male",
    "blood_sugar": 145,
    "hba1c": 7.3,
    "systolic_bp": 145,
    "diastolic_bp": 90,
    "heart_rate": 90,
    "hdl": 40,
    "ldl": 170,
    "triglycerides": 250,
    "creatinine": 1.0,
    "hemoglobin": 13,
    "bmi": 28
})
```
It returns predicted risks (LOW, BORDERLINE, HIGH), a weighted Health Score (0-100), and top risk parameters.
