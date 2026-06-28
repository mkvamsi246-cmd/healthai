from app.database import Base
from app.models.user import User
from app.models.report import Report
from app.models.medical_values import MedicalValues
from app.models.prediction import Prediction
from app.models.comparison import ComparisonHistory

# Expose models for imports and migrations discovery
__all__ = ["Base", "User", "Report", "MedicalValues", "Prediction", "ComparisonHistory"]
