from sqlalchemy import Column, Integer, DateTime, ForeignKey, Float, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class ComparisonHistory(Base):
    __tablename__ = "comparison_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    base_report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    compare_report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    
    comparison_data = Column(JSON, nullable=False) # Stores individual parameter comparison details
    overall_improvement_percentage = Column(Float, nullable=False)
    ai_summary = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="comparisons")
    base_report = relationship("Report", foreign_keys=[base_report_id])
    compare_report = relationship("Report", foreign_keys=[compare_report_id])
