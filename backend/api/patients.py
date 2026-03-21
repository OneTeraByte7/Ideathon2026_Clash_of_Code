from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from db.database import get_db
from models.patient import Patient
from models.vital import Vital

router = APIRouter(prefix="/patients", tags=["Patients"])


class PatientCreate(BaseModel):
    name: str
    age: int
    gender: str
    bed_number: str
    diagnosis: str
    allergies: str = ""
    comorbidities: str = ""
    is_post_surgical: bool = False
    is_immunocompromised: bool = False


class VitalCreate(BaseModel):
    heart_rate: float
    systolic_bp: float
    respiratory_rate: float
    temperature: float
    spo2: float
    lactate: float


@router.post("/")
async def create_patient(data: PatientCreate, db: AsyncSession = Depends(get_db)):
    patient = Patient(**data.model_dump())
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return patient


@router.get("/")
async def list_patients(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Patient).order_by(Patient.bed_number))
    return result.scalars().all()


@router.get("/{patient_id}")
async def get_patient(patient_id: int, db: AsyncSession = Depends(get_db)):
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")
    return patient


@router.post("/{patient_id}/vitals")
async def record_vitals(patient_id: int, data: VitalCreate, db: AsyncSession = Depends(get_db)):
    """Manually record vitals for a patient and get risk assessment."""
    from services.vitals_service import ingest_vital
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")

    vital = await ingest_vital(db, patient_id, data.model_dump(), source="manual")
    return {
        "vital_id": vital.id,
        "risk_score": vital.risk_score,
        "qsofa": vital.qsofa_score,
        "sofa_partial": vital.sofa_score,
        "risk_level": (await db.get(Patient, patient_id)).risk_level,
    }


@router.get("/{patient_id}/vitals")
async def get_vitals_history(
    patient_id: int,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Vital)
        .where(Vital.patient_id == patient_id)
        .order_by(desc(Vital.recorded_at))
        .limit(limit)
    )
    return result.scalars().all()


@router.delete("/{patient_id}")
async def delete_patient(patient_id: int, db: AsyncSession = Depends(get_db)):
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")
    await db.delete(patient)
    await db.commit()
    return {"deleted": patient_id}