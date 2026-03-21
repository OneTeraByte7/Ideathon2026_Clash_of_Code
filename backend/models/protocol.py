from beanie import Document
from pydantic import Field
from datetime import datetime, timezone
from typing import Optional
from beanie import PydanticObjectId


class Protocol(Document):
    patient_id: PydanticObjectId
    alert_id: Optional[PydanticObjectId] = None
    
    risk_score: float
    gemini_recommendation: str  # Full Gemini markdown output
    antibiotic_suggestion: str  # Extracted antibiotic plan
    immediate_actions: str  # Bullet list of actions
    rationale: str  # Clinical reasoning
    
    # Doctor review workflow
    status: str = "pending"  # pending | approved | modified | rejected
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    doctor_notes: Optional[str] = None
    
    # After doctor approves, nurse is notified
    nurse_notified: bool = False
    nurse_notified_at: Optional[datetime] = None
    
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings:
        name = "protocols"
        indexes = ["patient_id", "status", "generated_at"]