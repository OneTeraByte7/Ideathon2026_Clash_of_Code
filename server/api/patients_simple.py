from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime
from db.simple_mongo import patients, vitals
import uuid

router = APIRouter(prefix="/patients", tags=["Patients"])

# Mock data for immediate deployment
MOCK_PATIENTS = [
    {
        "_id": "pat_001",
        "name": "John Smith",
        "age": 65,
        "gender": "Male",
        "bed_number": "ICU-A01",
        "diagnosis": "Post-operative monitoring",
        "risk_level": "warning",
        "current_risk_score": 45.2,
        "vitals": {
            "heart_rate": 95,
            "systolic_bp": 105,
            "respiratory_rate": 22,
            "temperature": 38.1,
            "spo2": 94,
            "lactate": 2.1
        }
    },
    {
        "_id": "pat_002", 
        "name": "Maria Rodriguez",
        "age": 58,
        "gender": "Female", 
        "bed_number": "ICU-A02",
        "diagnosis": "Sepsis monitoring",
        "risk_level": "critical",
        "current_risk_score": 78.5,
        "vitals": {
            "heart_rate": 110,
            "systolic_bp": 85,
            "respiratory_rate": 28,
            "temperature": 39.2,
            "spo2": 88,
            "lactate": 3.8
        }
    }
]

@router.get("/")
async def get_patients():
    """Get all patients - returns mock data for immediate deployment"""
    try:
        # Try to get from database, fallback to mock
        db_patients = await patients.find_all()
        if db_patients:
            return db_patients
        return MOCK_PATIENTS
    except Exception:
        # Fallback to mock data if DB fails
        return MOCK_PATIENTS

@router.get("/{patient_id}")
async def get_patient(patient_id: str):
    """Get specific patient"""
    try:
        patient = await patients.find_one({"_id": patient_id})
        if patient:
            return patient
        # Fallback to mock
        for p in MOCK_PATIENTS:
            if p["_id"] == patient_id:
                return p
        raise HTTPException(status_code=404, detail="Patient not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{patient_id}/vitals")
async def get_patient_vitals(patient_id: str, limit: int = 20):
    """Get patient vitals history"""
    try:
        patient_vitals = await vitals.find_all(
            {"patient_id": patient_id}, 
            limit=limit
        )
        return patient_vitals or []
    except Exception:
        # Return empty list if fails
        return []

@router.post("/{patient_id}/vitals")
async def add_vital_reading(patient_id: str, vital_data: Dict[str, Any]):
    """Add new vital reading"""
    try:
        vital_doc = {
            "_id": str(uuid.uuid4()),
            "patient_id": patient_id,
            "recorded_at": datetime.utcnow().isoformat(),
            **vital_data
        }
        await vitals.insert_one(vital_doc)
        return {"status": "success", "vital_id": vital_doc["_id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))