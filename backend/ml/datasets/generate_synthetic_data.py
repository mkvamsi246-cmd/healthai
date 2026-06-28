import os
import numpy as np
import pandas as pd

def generate_patient_cohort(num_records=2000, seed=42):
    np.random.seed(seed)
    
    # Demographics
    age = np.random.randint(18, 85, size=num_records)
    gender = np.random.choice(["Male", "Female"], size=num_records)
    
    # Body dimensions
    height = np.random.normal(170, 10, size=num_records)
    # Adjust height slightly for females
    height[gender == "Female"] = np.random.normal(162, 7, size=num_records)[gender == "Female"]
    height = np.round(height, 1)
    
    # Weight
    weight = np.random.normal(75, 15, size=num_records)
    weight[gender == "Female"] = np.random.normal(65, 12, size=num_records)[gender == "Female"]
    weight = np.round(weight, 1)
    
    # Calculate BMI
    bmi = np.round(weight / ((height / 100) ** 2), 1)
    
    # Habits & history (binary variables)
    smoking = np.random.choice([0, 1], p=[0.75, 0.25], size=num_records)
    alcohol = np.random.choice([0, 1], p=[0.70, 0.30], size=num_records)
    exercise = np.random.choice([0, 1], p=[0.40, 0.60], size=num_records)
    family_history = np.random.choice([0, 1], p=[0.80, 0.20], size=num_records)
    
    # Vitals
    heart_rate = np.random.normal(72, 10, size=num_records)
    # Hypoxia correlation: normal is 95-100, sick is lower
    spo2 = np.random.choice(
        [np.random.uniform(95, 100), np.random.uniform(88, 94)], 
        p=[0.95, 0.05], 
        size=num_records
    )
    # Ensure SpO2 values are realistic floats and capped at 100.0
    spo2 = np.round(np.clip(spo2, 85.0, 100.0), 1)
    heart_rate = np.round(np.clip(heart_rate, 50, 120)).astype(int)

    # Blood Pressure (Systolic and Diastolic)
    systolic_bp = np.random.normal(122, 15, size=num_records)
    # Systolic increases slightly with age
    systolic_bp += (age - 40) * 0.25
    systolic_bp = np.round(np.clip(systolic_bp, 85, 200)).astype(int)
    
    diastolic_bp = np.round(systolic_bp * 0.66 + np.random.normal(0, 5, size=num_records)).astype(int)
    diastolic_bp = np.clip(diastolic_bp, 50, 120)

    # Biomarkers: Glycemic variables
    blood_sugar = np.random.normal(85, 15, size=num_records)
    # Some percentage are pre-diabetic or diabetic
    diabetic_idx = np.random.choice(num_records, size=int(num_records * 0.12), replace=False)
    blood_sugar[diabetic_idx] = np.random.normal(160, 40, size=len(diabetic_idx))
    blood_sugar = np.round(np.clip(blood_sugar, 60, 350), 1)
    
    # HbA1c is highly correlated with blood sugar
    hba1c = np.round(blood_sugar / 20.0 + np.random.normal(0, 0.3, size=num_records), 1)
    hba1c = np.clip(hba1c, 4.0, 14.0)

    # Biomarkers: Lipids
    hdl = np.random.normal(50, 10, size=num_records)
    hdl[gender == "Female"] += 5
    hdl = np.round(np.clip(hdl, 20, 95), 1)
    
    ldl = np.random.normal(110, 25, size=num_records)
    # Out of range lipids for some patients
    lipid_sick_idx = np.random.choice(num_records, size=int(num_records * 0.15), replace=False)
    ldl[lipid_sick_idx] = np.random.normal(170, 30, size=len(lipid_sick_idx))
    ldl = np.round(np.clip(ldl, 40, 280), 1)
    
    triglycerides = np.round(ldl * 1.2 + np.random.normal(0, 20, size=num_records), 1)
    triglycerides = np.clip(triglycerides, 40, 500)
    
    total_cholesterol = np.round(hdl + ldl + triglycerides * 0.2, 1)

    # Renal & Blood counts
    creatinine = np.random.normal(0.85, 0.15, size=num_records)
    kidney_sick_idx = np.random.choice(num_records, size=int(num_records * 0.08), replace=False)
    creatinine[kidney_sick_idx] = np.random.normal(1.9, 0.6, size=len(kidney_sick_idx))
    creatinine = np.round(np.clip(creatinine, 0.3, 8.0), 2)
    
    hemoglobin = np.random.normal(14.5, 1.2, size=num_records)
    hemoglobin[gender == "Female"] -= 1.5
    hemoglobin = np.round(np.clip(hemoglobin, 8.0, 18.0), 1)

    # Target Label Injections based on clinical indicators
    # ----------------------------------------------------
    # Risk Scores range [0.0, 1.0]
    
    # 1. Diabetes Risk Label
    db_score = (
        (blood_sugar - 70) / 100.0 * 0.4 +
        (hba1c - 4.5) / 3.0 * 0.4 +
        (bmi - 20) / 15.0 * 0.1 +
        family_history * 0.1
    )
    db_prob = 1 / (1 + np.exp(-db_score * 8.0 + 4.0)) # sigmoid
    diabetes_risk = np.zeros(num_records, dtype=int)
    diabetes_risk[db_prob > 0.4] = 1 # Moderate
    diabetes_risk[db_prob > 0.75] = 2 # High

    # 2. Heart Disease Risk Label
    hd_score = (
        (age - 30) / 50.0 * 0.2 +
        (ldl - 100) / 80.0 * 0.25 +
        (systolic_bp - 120) / 50.0 * 0.25 +
        (50 - hdl) / 30.0 * 0.1 +
        smoking * 0.1 +
        family_history * 0.1 -
        exercise * 0.05
    )
    hd_prob = 1 / (1 + np.exp(-hd_score * 8.0 + 3.5))
    heart_disease_risk = np.zeros(num_records, dtype=int)
    heart_disease_risk[hd_prob > 0.4] = 1 # Moderate
    heart_disease_risk[hd_prob > 0.75] = 2 # High

    # 3. Kidney Disease Risk Label
    kd_score = (
        (creatinine - 0.9) / 0.5 * 0.6 +
        (systolic_bp - 120) / 50.0 * 0.2 +
        (age - 35) / 45.0 * 0.2
    )
    kd_prob = 1 / (1 + np.exp(-kd_score * 10.0 + 4.0))
    kidney_disease_risk = np.zeros(num_records, dtype=int)
    kidney_disease_risk[kd_prob > 0.35] = 1 # Moderate
    kidney_disease_risk[kd_prob > 0.70] = 2 # High

    # 4. Stroke Risk Label
    st_score = (
        (systolic_bp - 120) / 40.0 * 0.45 +
        (diastolic_bp - 80) / 25.0 * 0.15 +
        (age - 35) / 45.0 * 0.2 +
        smoking * 0.1 +
        alcohol * 0.1
    )
    st_prob = 1 / (1 + np.exp(-st_score * 9.0 + 4.0))
    stroke_risk = np.zeros(num_records, dtype=int)
    stroke_risk[st_prob > 0.4] = 1 # Moderate
    stroke_risk[st_prob > 0.75] = 2 # High

    # Create DataFrame
    df = pd.DataFrame({
        "Age": age,
        "Gender": gender,
        "Height": height,
        "Weight": weight,
        "BMI": bmi,
        "Heart Rate": heart_rate,
        "Systolic BP": systolic_bp,
        "Diastolic BP": diastolic_bp,
        "Blood Sugar": blood_sugar,
        "HbA1c": hba1c,
        "HDL": hdl,
        "LDL": ldl,
        "Total Cholesterol": total_cholesterol,
        "Triglycerides": triglycerides,
        "Creatinine": creatinine,
        "Hemoglobin": hemoglobin,
        "SpO₂": spo2,
        "Smoking": smoking,
        "Alcohol": alcohol,
        "Exercise": exercise,
        "Family History": family_history,
        "heart_disease_risk": heart_disease_risk,
        "diabetes_risk": diabetes_risk,
        "kidney_disease_risk": kidney_disease_risk,
        "stroke_risk": stroke_risk
    })
    
    return df

if __name__ == "__main__":
    datasets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    os.makedirs(datasets_dir, exist_ok=True)
    
    csv_path = os.path.join(datasets_dir, "merged_dataset.csv")
    print(f"Generating clinical patient cohort of 2000 records...")
    df = generate_patient_cohort(num_records=2200, seed=42)
    
    df.to_csv(csv_path, index=False)
    print(f"Dataset successfully created and saved to: {csv_path}")
    print(df.head())
    print("\nClass distribution checks:")
    print("Heart Disease:", df['heart_disease_risk'].value_counts().to_dict())
    print("Diabetes:", df['diabetes_risk'].value_counts().to_dict())
    print("Kidney Disease:", df['kidney_disease_risk'].value_counts().to_dict())
    print("Stroke Risk:", df['stroke_risk'].value_counts().to_dict())
