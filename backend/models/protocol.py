from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from db.database import Base


class Protocol(Base):
    __tablename__ = "protocols"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=True)

    risk_score = Column(Float)
    gemini_recommendation = Column(Text)    # Full Gemini markdown output
    antibiotic_suggestion = Column(Text)    # Extracted antibiotic plan
    immediate_actions = Column(Text)        # Bullet list of actions
    rationale = Column(Text)               # Clinical reasoning

    # Doctor review workflow
    status = Column(String(20), default="pending")  # pending | approved | modified | rejected
    reviewed_by = Column(String(100), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    doctor_notes = Column(Text, nullable=True)

    # After doctor approves, nurse is notified
    nurse_notified = Column(Boolean, default=False)
    nurse_notified_at = Column(DateTime, nullable=True)

    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    patient = relationship("Patient", back_populates="protocols")