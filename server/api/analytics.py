from fastapi import APIRouter
from agents.learning_agent import get_accuracy_report, get_patient_trend

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/accuracy")
async def accuracy_report():
    """Overall system prediction accuracy and insights."""
    return await get_accuracy_report()


@router.get("/trend/{patient_id}")
async def patient_risk_trend(patient_id: str, limit: int = 20):
    """Risk score timeline for a specific patient."""
    return await get_patient_trend(patient_id, limit)