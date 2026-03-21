from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from db.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    vital_id = Column(Integer, ForeignKey("vitals.id"), nullable=True)

    level = Column(String(10), nullable=False)     # warning | critical
    risk_score = Column(Float, nullable=False)
    message = Column(Text)

    # Notification tracking
    nurse_notified = Column(Boolean, default=False)
    doctor_notified = Column(Boolean, default=False)
    nurse_notified_at = Column(DateTime, nullable=True)
    doctor_notified_at = Column(DateTime, nullable=True)

    # Resolution
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String(50), nullable=True)

    triggered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    patient = relationship("Patient", back_populates="alerts")