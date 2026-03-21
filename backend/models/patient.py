from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from db.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer)
    gender = Column(String(10))
    bed_number = Column(String(20), unique=True, index=True)
    diagnosis = Column(String(200))
    allergies = Column(String(500), default="")          # comma-separated
    comorbidities = Column(String(500), default="")      # comma-separated
    is_post_surgical = Column(Boolean, default=False)
    is_immunocompromised = Column(Boolean, default=False)
    current_risk_score = Column(Float, default=0.0)
    risk_level = Column(String(10), default="normal")    # normal | warning | critical
    admitted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    vitals = relationship("Vital", back_populates="patient", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="patient", cascade="all, delete-orphan")
    protocols = relationship("Protocol", back_populates="patient", cascade="all, delete-orphan")