from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from db.database import Base


class Vital(Base):
    """
    6 core sepsis prediction metrics:
    1. heart_rate       — tachycardia >90 bpm
    2. systolic_bp      — hypotension ≤100 mmHg
    3. respiratory_rate — tachypnea ≥22 breaths/min
    4. temperature      — fever >38.3°C or hypothermia <36°C
    5. spo2             — oxygen saturation <95%
    6. lactate          — hyperlactatemia >2 mmol/L
    """
    __tablename__ = "vitals"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)

    # Core 6 metrics
    heart_rate = Column(Float)           # bpm
    systolic_bp = Column(Float)          # mmHg
    respiratory_rate = Column(Float)     # breaths/min
    temperature = Column(Float)          # Celsius
    spo2 = Column(Float)                 # percentage
    lactate = Column(Float)              # mmol/L

    # Computed scores at time of reading
    risk_score = Column(Float, default=0.0)
    sofa_score = Column(Float, default=0.0)
    qsofa_score = Column(Integer, default=0)

    source = Column(String(20), default="monitor")  # monitor | seed_normal | seed_warning | seed_critical
    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    patient = relationship("Patient", back_populates="vitals")