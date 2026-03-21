from beanie import Document
from pydantic import Field
from datetime import datetime, timezone
from typing import Optional
from beanie import PydanticObjectId


class Vital(Document):
    """
    6 core sepsis prediction metrics:
    1. heart_rate       — tachycardia >90 bpm
    2. systolic_bp      — hypotension ≤100 mmHg
    3. respiratory_rate — tachypnea ≥22 breaths/min
    4. temperature      — fever >38.3°C or hypothermia <36°C
    5. spo2             — oxygen saturation <95%
    6. lactate          — hyperlactatemia >2 mmol/L
    """
    
    patient_id: PydanticObjectId
    
    # Core 6 metrics
    heart_rate: float  # bpm
    systolic_bp: float  # mmHg
    respiratory_rate: float  # breaths/min
    temperature: float  # Celsius
    spo2: float  # percentage
    lactate: float  # mmol/L
    
    # Computed scores
    risk_score: float = 0.0
    sofa_score: float = 0.0
    qsofa_score: int = 0
    
    source: str = "monitor"  # monitor | seed_normal | seed_warning | seed_critical
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings:
        name = "vitals"
        indexes = ["patient_id", "recorded_at", "risk_score"]