from beanie import Document
from pydantic import Field
from datetime import datetime, timezone
from typing import Optional


class Patient(Document):
    name: str
    age: int
    gender: str
    bed_number: str = Field(..., unique=True)
    diagnosis: str
    allergies: str = ""
    comorbidities: str = ""
    is_post_surgical: bool = False
    is_immunocompromised: bool = False
    current_risk_score: float = 0.0
    risk_level: str = "normal"  # normal | warning | critical
    admitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "patients"
        indexes = ["bed_number", "risk_level"]

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "age": 45,
                "gender": "Male",
                "bed_number": "ICU-101",
                "diagnosis": "Sepsis suspected",
                "allergies": "Penicillin",
                "comorbidities": "Diabetes",
                "is_post_surgical": False,
                "is_immunocompromised": False
            }
        }