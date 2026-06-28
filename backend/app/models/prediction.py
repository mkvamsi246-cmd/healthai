from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), unique=True, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    heart_disease_risk = Column(String(20), nullable=False) # e.g. LOW, BORDERLINE, HIGH
    diabetes_risk = Column(String(20), nullable=False)
    kidney_disease_risk = Column(String(20), nullable=False)
    stroke_risk = Column(String(20), nullable=False)
    health_score = Column(Integer, nullable=False)          # Score 0-100
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="predictions")
    report = relationship("Report", back_populates="prediction")
