from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from agents.learning_agent import get_accuracy_report, get_patient_trend

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/accuracy")
async def accuracy_report(db: AsyncSession = Depends(get_db)):
    """Overall system prediction accuracy and insights."""
    return await get_accuracy_report(db)


@router.get("/trend/{patient_id}")
async def patient_risk_trend(patient_id: int, limit: int = 20, db: AsyncSession = Depends(get_db)):
    """Risk score timeline for a specific patient."""
    return await get_patient_trend(db, patient_id, limit)