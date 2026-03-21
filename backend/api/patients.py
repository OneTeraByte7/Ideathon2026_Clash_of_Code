from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

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
async def create_patient(data: PatientCreate):
    patient = Patient(**data.model_dump())
    await patient.insert()
    return patient


@router.get("/")
async def list_patients():
    patients = await Patient.find_all().sort("bed_number", 1).to_list()
    return patients


@router.get("/{patient_id}")
async def get_patient(patient_id: str):
    from beanie import PydanticObjectId
    patient = await Patient.get(PydanticObjectId(patient_id))
    if not patient:
        raise HTTPException(404, "Patient not found")
    return patient


@router.post("/{patient_id}/vitals")
async def record_vitals(patient_id: str, data: VitalCreate):
    """Manually record vitals for a patient and get risk assessment."""
    from beanie import PydanticObjectId
    from services.vitals_service import ingest_vital
    
    patient = await Patient.get(PydanticObjectId(patient_id))
    if not patient:
        raise HTTPException(404, "Patient not found")

    vital = await ingest_vital(PydanticObjectId(patient_id), data.model_dump(), source="manual")
    return {
        "vital_id": str(vital.id),
        "risk_score": vital.risk_score,
        "qsofa": vital.qsofa_score,
        "sofa_partial": vital.sofa_score,
        "risk_level": (await Patient.get(PydanticObjectId(patient_id))).risk_level,
    }


@router.get("/{patient_id}/vitals")
async def get_vitals_history(
    patient_id: str,
    limit: int = 20,
):
    from beanie import PydanticObjectId
    vitals = await Vital.find(Vital.patient_id == PydanticObjectId(patient_id)).sort("-recorded_at").limit(limit).to_list()
    return vitals


@router.delete("/{patient_id}")
async def delete_patient(patient_id: str):
    from beanie import PydanticObjectId
    patient = await Patient.get(PydanticObjectId(patient_id))
    if not patient:
        raise HTTPException(404, "Patient not found")
    await patient.delete()
    return {"deleted": patient_id}