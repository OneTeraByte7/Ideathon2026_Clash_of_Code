from beanie import Document
from pydantic import Field
from datetime import datetime, timezone
from typing import Optional
from beanie import PydanticObjectId


class Alert(Document):
    patient_id: PydanticObjectId
    vital_id: Optional[PydanticObjectId] = None
    
    level: str  # warning | critical
    risk_score: float
    message: str
    
    # Notification tracking
    nurse_notified: bool = False
    doctor_notified: bool = False
    nurse_notified_at: Optional[datetime] = None
    doctor_notified_at: Optional[datetime] = None
    
    # Resolution
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    
    triggered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings:
        name = "alerts"
        indexes = ["patient_id", "level", "resolved", "triggered_at"]