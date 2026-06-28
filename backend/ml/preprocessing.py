import os
import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from imblearn.over_sampling import SMOTE

class Preprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.numeric_features = [
            "Age", "Height", "Weight", "BMI", "Heart Rate", "Systolic BP", "Diastolic BP", 
            "Blood Sugar", "HbA1c", "HDL", "LDL", "Total Cholesterol", "Triglycerides", 
            "Creatinine", "Hemoglobin", "SpO₂", "Pulse Pressure", "MAP", "Health Index", "Risk Score"
        ]
        self.categorical_features = ["Gender"]
        self.binary_features = ["Smoking", "Alcohol", "Exercise", "Family History"]

    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        before = len(df)
        df = df.drop_duplicates()
        after = len(df)
        if before > after:
            print(f"Removed {before - after} duplicate records.")
        return df

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        # Numeric columns get median imputation
        for col in df.columns:
            if col in self.numeric_features or df[col].dtype in [np.float64, np.int64]:
                if df[col].isnull().any():
                    df[col] = df[col].fillna(df[col].median())
            elif col in self.categorical_features or col in self.binary_features:
                if df[col].isnull().any():
                    df[col] = df[col].fillna(df[col].mode()[0])
        return df

    def detect_and_clip_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clips extreme outliers outside 1.5 * IQR to limit skewness in model metrics.
        """
        df = df.copy()
        for col in self.numeric_features:
            if col in df.columns:
                q1 = df[col].quantile(0.25)
                q3 = df[col].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 2.5 * iqr
                upper_bound = q3 + 2.5 * iqr
                df[col] = np.clip(df[col], lower_bound, upper_bound)
        return df

    def fit_encode_categorical(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        for col in self.categorical_features:
            if col in df.columns:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
        return df

    def transform_encode_categorical(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        for col in self.categorical_features:
            if col in df.columns and col in self.label_encoders:
                le = self.label_encoders[col]
                # Handle unseen values gracefully by selecting first class if unknown
                df[col] = df[col].astype(str).map(
                    lambda s: le.transform([s])[0] if s in le.classes_ else le.transform([le.classes_[0]])[0]
                )
        return df

    def fit_scale_numerical(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        existing_num_cols = [c for c in self.numeric_features if c in df.columns]
        if existing_num_cols:
            scaled_vals = self.scaler.fit_transform(df[existing_num_cols])
            df[existing_num_cols] = scaled_vals
        return df

    def transform_scale_numerical(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        existing_num_cols = [c for c in self.numeric_features if c in df.columns]
        if existing_num_cols:
            scaled_vals = self.scaler.transform(df[existing_num_cols])
            df[existing_num_cols] = scaled_vals
        return df

    def apply_smote(self, X: pd.DataFrame, y: pd.Series) -> tuple[pd.DataFrame, pd.Series]:
        """
        Balances targets using SMOTE. Handles classes with few items gracefully.
        """
        # Ensure we have more than 1 class
        if len(np.unique(y)) <= 1:
            return X, y
            
        # Standard SMOTE settings
        class_counts = y.value_counts()
        min_class_size = class_counts.min()
        
        # If the minimum class has fewer than 6 samples, adjust k_neighbors
        k = min(5, max(1, min_class_size - 1))
        
        try:
            smote = SMOTE(random_state=42, k_neighbors=k)
            X_res, y_res = smote.fit_resample(X, y)
            return pd.DataFrame(X_res, columns=X.columns), pd.Series(y_res, name=y.name)
        except Exception as e:
            print(f"SMOTE balancing failed for target {y.name}: {e}. Retaining original distribution.")
            return X, y

    def save_artifacts(self, models_dir: str):
        """
        Saves feature_scaler.pkl and label_encoders.pkl to model folder.
        """
        os.makedirs(models_dir, exist_ok=True)
        scaler_path = os.path.join(models_dir, "feature_scaler.pkl")
        encoders_path = os.path.join(models_dir, "label_encoders.pkl")
        
        joblib.dump(self.scaler, scaler_path)
        joblib.dump(self.label_encoders, encoders_path)
        print(f"Preprocessor scaler saved to: {scaler_path}")
        print(f"Preprocessor label encoders saved to: {encoders_path}")

preprocessor = Preprocessor()
