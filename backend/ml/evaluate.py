import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc
from typing import Dict, List, Any

# Configure plotting aesthetics
sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 10, 'figure.titlesize': 14})

class ModelEvaluator:
    def __init__(self, results_dir: str = "results"):
        self.results_dir = results_dir
        os.makedirs(self.results_dir, exist_ok=True)

    def plot_correlation_heatmap(self, df: pd.DataFrame, filename: str = "correlation_heatmap.png"):
        """
        Plots a correlation heatmap for numerical attributes.
        """
        plt.figure(figsize=(14, 10))
        # Keep only numeric columns
        numeric_df = df.select_dtypes(include=[np.number])
        corr = numeric_df.corr()
        
        mask = np.triu(np.ones_like(corr, dtype=bool))
        sns.heatmap(
            corr, mask=mask, annot=True, fmt=".2f", cmap="coolwarm", 
            square=True, linewidths=.5, cbar_kws={"shrink": .8},
            annot_kws={"size": 7}
        )
        plt.title("Clinical Attributes Correlation Heatmap")
        plt.tight_layout()
        save_path = os.path.join(self.results_dir, filename)
        plt.savefig(save_path, dpi=300)
        plt.close()
        print(f"Heatmap visualization saved to: {save_path}")

    def plot_accuracy_comparison(self, model_metrics: Dict[str, Dict[str, float]], filename: str = "model_accuracy_comparison.png"):
        """
        Plots a bar chart comparing accuracy/F1 performance across all trained models.
        """
        plt.figure(figsize=(10, 6))
        
        # Prepare data for plotting
        models = list(model_metrics.keys())
        accuracies = [metrics["accuracy"] for metrics in model_metrics.values()]
        f1_scores = [metrics["f1_macro"] for metrics in model_metrics.values()]
        
        x = np.arange(len(models))
        width = 0.35
        
        plt.bar(x - width/2, accuracies, width, label='Accuracy', color='#1e3a8a')
        plt.bar(x + width/2, f1_scores, width, label='Macro F1-Score', color='#3b82f6')
        
        plt.ylabel('Score')
        plt.title('Classifier Models Performance Comparison')
        plt.xticks(x, models, rotation=15)
        plt.ylim(0, 1.05)
        plt.legend(loc='lower right')
        plt.tight_layout()
        
        save_path = os.path.join(self.results_dir, filename)
        plt.savefig(save_path, dpi=300)
        plt.close()
        print(f"Accuracy comparison visualization saved to: {save_path}")

    def plot_confusion_matrices(self, y_true: pd.DataFrame, y_pred: pd.DataFrame, target_cols: List[str], filename: str = "confusion_matrix.png"):
        """
        Plots grid of confusion matrices for each risk target.
        """
        n_targets = len(target_cols)
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        axes = axes.ravel()
        
        for idx, target in enumerate(target_cols):
            cm = confusion_matrix(y_true[target], y_pred[target])
            # Normalize confusion matrix
            cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
            
            sns.heatmap(
                cm_norm, annot=cm, fmt="d", cmap="Blues", ax=axes[idx], cbar=False,
                xticklabels=["Low", "Moderate", "High"], yticklabels=["Low", "Moderate", "High"]
            )
            axes[idx].set_title(f"Confusion Matrix: {target.replace('_', ' ').title()}")
            axes[idx].set_ylabel("True Label")
            axes[idx].set_xlabel("Predicted Label")
            
        plt.suptitle("Model Prediction Confusion Matrices Grid", y=0.98)
        plt.tight_layout()
        
        save_path = os.path.join(self.results_dir, filename)
        plt.savefig(save_path, dpi=300)
        plt.close()
        print(f"Confusion matrix grid saved to: {save_path}")

    def plot_roc_curves(self, classifier_pipelines: dict, X_test: pd.DataFrame, y_test: pd.DataFrame, target_cols: List[str], filename: str = "roc_curve.png"):
        """
        Plots multiclass ROC curves for all targets.
        """
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        axes = axes.ravel()
        
        # Color palettes
        colors = ['#10b981', '#f59e0b', '#ef4444'] # Green, Amber, Red
        
        for idx, target in enumerate(target_cols):
            pipeline = classifier_pipelines # The trained MultiOutput model pipeline
            ax = axes[idx]
            
            # Predict probabilities
            if hasattr(pipeline, "predict_proba"):
                # MultiOutputClassifier.predict_proba returns list of arrays
                # One array per target column
                probs = pipeline.predict_proba(X_test)[idx]
                
                # Plot ROC for each class (0=Low, 1=Moderate, 2=High)
                for class_val in range(probs.shape[1]):
                    # binarize target
                    y_test_bin = (y_test[target] == class_val).astype(int)
                    # Skip if class has no samples in test split
                    if y_test_bin.sum() == 0:
                        continue
                        
                    fpr, tpr, _ = roc_curve(y_test_bin, probs[:, class_val])
                    roc_auc = auc(fpr, tpr)
                    class_name = ["Low", "Moderate", "High"][class_val]
                    
                    ax.plot(fpr, tpr, color=colors[class_val], lw=2, label=f'{class_name} (AUC = {roc_auc:.2f})')
                    
            ax.plot([0, 1], [0, 1], 'k--', lw=1)
            ax.set_xlim([0.0, 1.0])
            ax.set_ylim([0.0, 1.05])
            ax.set_xlabel('False Positive Rate')
            ax.set_ylabel('True Positive Rate')
            ax.set_title(f'ROC Curves: {target.replace("_", " ").title()}')
            ax.legend(loc="lower right", fontsize=8)
            
        plt.suptitle("Target Risk Multi-Class ROC Curves", y=0.98)
        plt.tight_layout()
        
        save_path = os.path.join(self.results_dir, filename)
        plt.savefig(save_path, dpi=300)
        plt.close()
        print(f"ROC Curves visualization saved to: {save_path}")

    def plot_feature_importances(self, importances: np.ndarray, feature_names: List[str], filename: str = "feature_importance.png"):
        """
        Plots a bar chart of aggregate feature importances.
        """
        plt.figure(figsize=(10, 8))
        
        indices = np.argsort(importances)[::-1]
        sorted_features = [feature_names[i] for i in indices]
        sorted_importances = importances[indices]
        
        # Keep top 15 features
        top_n = min(15, len(feature_names))
        sns.barplot(x=sorted_importances[:top_n], y=sorted_features[:top_n], palette="Blues_r")
        
        plt.xlabel('Importance Value')
        plt.title('Top Engineered Feature Importances')
        plt.tight_layout()
        
        save_path = os.path.join(self.results_dir, filename)
        plt.savefig(save_path, dpi=300)
        plt.close()
        print(f"Feature importance visualization saved to: {save_path}")

    def generate_classification_report_str(self, y_true: pd.DataFrame, y_pred: pd.DataFrame, target_cols: List[str]) -> str:
        report_str = "==================================================\n"
        report_str += "CLASSIFICATION REPORTS GRID\n"
        report_str += "==================================================\n\n"
        
        for target in target_cols:
            report_str += f"Target: {target.replace('_', ' ').title()}\n"
            report_str += "--------------------------------------------------\n"
            report_str += classification_report(
                y_true[target], y_pred[target], 
                target_names=["Low", "Moderate", "High"],
                zero_division=0
            )
            report_str += "\n"
            
        return report_str

evaluator = ModelEvaluator()
