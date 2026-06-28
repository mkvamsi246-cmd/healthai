import os
import sys
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, f1_score, classification_report
from sklearn.multioutput import MultiOutputClassifier
from typing import Dict, List, Any

# Machine Learning Estimator Imports
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier
from xgboost import XGBClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

# Add root folder to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ml.preprocessing import preprocessor
from ml.feature_engineering import feature_engineer
from ml.evaluate import evaluator

def train_and_select_model():
    # Paths setup
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # ml/ directory
    dataset_path = os.path.join(base_dir, "datasets", "merged_dataset.csv")
    models_dir = os.path.join(base_dir, "models")
    results_dir = os.path.join(base_dir, "results")
    
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    print(f"Loading dataset from: {dataset_path}...")
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found at: {dataset_path}. Run generate_synthetic_data.py first.")
        
    df = pd.read_csv(dataset_path)
    
    # 1. Feature Engineering
    print("Executing Feature Engineering...")
    df = feature_engineer.add_features_df(df)
    
    # Save correlation heatmap on raw numeric columns
    evaluator.plot_correlation_heatmap(df)

    # Split into features (X) and targets (Y)
    target_cols = ["heart_disease_risk", "diabetes_risk", "kidney_disease_risk", "stroke_risk"]
    X = df.drop(columns=target_cols)
    y = df[target_cols]

    # 2. Preprocessing (duplicates & missing values)
    print("Executing Preprocessing (cleaning & outlier clipping)...")
    X = preprocessor.remove_duplicates(X)
    # Align target indexes with X
    y = y.loc[X.index]
    
    X = preprocessor.handle_missing_values(X)
    X = preprocessor.detect_and_clip_outliers(X)
    
    # Categorical fitting & encoding
    X = preprocessor.fit_encode_categorical(X)
    
    # Scale numerical values
    X = preprocessor.fit_scale_numerical(X)
    
    # Save preprocessor artifacts
    preprocessor.save_artifacts(models_dir)
    # Also save copies in ml/ root directory for direct backend imports compatibility
    preprocessor.save_artifacts(base_dir)

    # Train / Test split (80% / 20%)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 3. Model Definition Dictionary
    base_estimators = {
        "RandomForest": RandomForestClassifier(random_state=42, n_estimators=100),
        "XGBoost": XGBClassifier(random_state=42, eval_metric='mlogloss', n_estimators=100),
        "GradientBoosting": GradientBoostingClassifier(random_state=42, n_estimators=100),
        "DecisionTree": DecisionTreeClassifier(random_state=42, max_depth=8),
        "LogisticRegression": LogisticRegression(random_state=42, max_iter=500),
        "SVM": SVC(random_state=42, probability=True),
        "ExtraTrees": ExtraTreesClassifier(random_state=42, n_estimators=100)
    }

    model_scores = {}

    print("\nComparing base classifiers using MultiOutput wrapper on Test split:")
    print("------------------------------------------------------------------")

    for name, clf in base_estimators.items():
        print(f"Evaluating {name}...")
        
        # We wrapper base classifier in a MultiOutputClassifier
        multi_clf = MultiOutputClassifier(clf)
        
        # Fit MultiOutput model
        multi_clf.fit(X_train, y_train)
        
        # Predict on test
        y_pred = multi_clf.predict(X_test)
        y_pred_df = pd.DataFrame(y_pred, columns=target_cols, index=y_test.index)
        
        # Evaluate metrics (Average F1 & Accuracy across all 4 targets)
        acc_scores = []
        f1_scores = []
        for col in target_cols:
            acc_scores.append(accuracy_score(y_test[col], y_pred_df[col]))
            f1_scores.append(f1_score(y_test[col], y_pred_df[col], average='macro', zero_division=0))
            
        avg_acc = np.mean(acc_scores)
        avg_f1 = np.mean(f1_scores)
        
        model_scores[name] = {
            "accuracy": avg_acc,
            "f1_macro": avg_f1,
            "model_object": multi_clf
        }
        print(f"-> Avg Accuracy: {avg_acc:.4f} | Avg Macro F1: {avg_f1:.4f}")

    # Plot comparisons
    evaluator.plot_accuracy_comparison(model_scores)

    # Select Best Model based on F1 Score
    best_model_name = max(model_scores, key=lambda k: model_scores[k]["f1_macro"])
    best_score = model_scores[best_model_name]["f1_macro"]
    print(f"\n==================================================")
    print(f"WINNING MODEL: {best_model_name} (Avg F1: {best_score:.4f})")
    print(f"==================================================")

    # 4. Fit Final Best Classifier with SMOTE Balancing
    # We train the selected best classifier for each target column separately.
    # This allows us to apply SMOTE target balancing per label dynamically!
    final_models = {}
    X_test_scaled_list = []
    
    # We resolve the winning estimator parameters
    base_estimator = base_estimators[best_model_name]
    
    print("\nTraining final models with SMOTE class balancing for each target...")
    for target in target_cols:
        print(f"Training risk estimator for target: {target}...")
        
        # Balance training split for this target
        X_train_res, y_train_res = preprocessor.apply_smote(X_train, y_train[target])
        
        # Fit independent estimator
        from copy import deepcopy
        model_head = deepcopy(base_estimator)
        model_head.fit(X_train_res, y_train_res)
        
        final_models[target] = model_head

    # 5. Evaluate final model predictions
    y_test_pred = pd.DataFrame(index=y_test.index)
    for target in target_cols:
        y_test_pred[target] = final_models[target].predict(X_test)

    # Generate classification reports
    report_text = evaluator.generate_classification_report_str(y_test, y_test_pred, target_cols)
    print(report_text)
    
    with open(os.path.join(results_dir, "classification_report.txt"), "w") as f:
        f.write(report_text)

    # Generate visual confusion matrices grid & multi-class ROC curves
    evaluator.plot_confusion_matrices(y_test, y_test_pred, target_cols)
    
    # For ROC curve plot, we wrap our dict final_models in a mock MultiOutputClassifier
    # so evaluator can run predict_proba on it
    class MockMultiOutput:
        def __init__(self, models):
            self.models = models
        def predict_proba(self, X):
            return [self.models[target].predict_proba(X) for target in target_cols]
            
    mock_wrapper = MockMultiOutput(final_models)
    evaluator.plot_roc_curves(mock_wrapper, X_test, y_test, target_cols)

    # Save feature importances if winning model supports it (like tree models)
    if hasattr(base_estimator, "feature_importances_"):
        # Average feature importances across all 4 target classifiers
        feat_importances = np.mean([final_models[t].feature_importances_ for t in target_cols], axis=0)
        evaluator.plot_feature_importances(feat_importances, list(X.columns))

    # 6. Save final models dictionary bundle
    model_bundle = {
        "model_name": best_model_name,
        "estimators": final_models,
        "feature_names": list(X.columns)
    }
    
    model_save_path = os.path.join(models_dir, "health_model.pkl")
    joblib.dump(model_bundle, model_save_path)
    
    # Save a direct copy in the ml/ folder for immediate backend visibility
    joblib.dump(model_bundle, os.path.join(base_dir, "health_model.pkl"))
    
    print(f"Final model bundle successfully saved to: {model_save_path}")
    print(f"Duplicate model bundle saved to: {os.path.join(base_dir, 'health_model.pkl')}")

if __name__ == "__main__":
    train_and_select_model()
