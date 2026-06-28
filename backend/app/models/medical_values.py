from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class MedicalValues(Base):
    __tablename__ = "medical_values"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), unique=True, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Demographics at the time of report
    age = Column(Integer, nullable=True)
    gender = Column(String(10), nullable=True)
    
    # Vital signs & biomarkers
    blood_sugar = Column(Float, nullable=True)          # Fasting blood sugar or random (mg/dL)
    hba1c = Column(Float, nullable=True)                # HbA1c (%)
    systolic_bp = Column(Integer, nullable=True)        # Blood Pressure Systolic (mmHg)
    diastolic_bp = Column(Integer, nullable=True)      # Blood Pressure Diastolic (mmHg)
    heart_rate = Column(Integer, nullable=True)         # Heart Rate (bpm)
    spo2 = Column(Float, nullable=True)                 # SpO2 (%)
    
    # Lipid panel
    hdl = Column(Float, nullable=True)                  # HDL cholesterol (mg/dL)
    ldl = Column(Float, nullable=True)                  # LDL cholesterol (mg/dL)
    triglycerides = Column(Float, nullable=True)        # Triglycerides (mg/dL)
    total_cholesterol = Column(Float, nullable=True)    # Total cholesterol (mg/dL)
    
    # Others
    creatinine = Column(Float, nullable=True)           # Creatinine (mg/dL)
    hemoglobin = Column(Float, nullable=True)           # Hemoglobin (g/dL)
    weight = Column(Float, nullable=True)               # Weight (kg)
    bmi = Column(Float, nullable=True)                  # Body Mass Index
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="medical_values")
    report = relationship("Report", back_populates="medical_values")
