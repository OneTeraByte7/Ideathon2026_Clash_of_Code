from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from models.patient import Patient
from models.vital import Vital
from services.telegram_service import telegram_service

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
    patients = await Patient.find_all().sort([("bed_number", 1)]).to_list()
    
    # Enrich each patient with latest vitals and active alerts
    enriched_patients = []
    for p in patients:
        # Get latest vital
        latest_vital = await Vital.find(Vital.patient_id == p.id).sort([("recorded_at", -1)]).limit(1).to_list()
        
        # Get active alerts
        from models.alert import Alert
        active_alerts = await Alert.find(Alert.patient_id == p.id, Alert.resolved == False).sort([("triggered_at", -1)]).limit(3).to_list()
        
        # Convert patient to dict and enrich
        patient_dict = p.model_dump()
        patient_dict["vitals"] = {
            "heart_rate": latest_vital[0].heart_rate if latest_vital else None,
            "systolic_bp": latest_vital[0].systolic_bp if latest_vital else None,
            "respiratory_rate": latest_vital[0].respiratory_rate if latest_vital else None,
            "temperature": latest_vital[0].temperature if latest_vital else None,
            "spo2": latest_vital[0].spo2 if latest_vital else None,
            "lactate": latest_vital[0].lactate if latest_vital else None,
        }
        patient_dict["active_alerts"] = [
            {"level": a.level, "message": a.message, "at": a.triggered_at.isoformat()}
            for a in active_alerts
        ]
        
        enriched_patients.append(patient_dict)
    
    return enriched_patients


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
    vitals = await Vital.find(Vital.patient_id == PydanticObjectId(patient_id)).sort([("recorded_at", -1)]).limit(limit).to_list()
    return vitals


@router.post("/{patient_id}/trigger-critical")
async def trigger_critical_alert(patient_id: str):
    """
    🚨 TRIGGER CRITICAL ALERT - FOR DEMO PURPOSES
    
    Manually triggers a critical alert for the specified patient
    and sends Telegram notifications to medical staff.
    """
    from beanie import PydanticObjectId
    from datetime import datetime
    
    # Get patient data
    try:
        patient = await Patient.get(PydanticObjectId(patient_id))
    except:
        raise HTTPException(400, "Invalid patient ID format")
        
    if not patient:
        raise HTTPException(404, "Patient not found")
    
    # Get latest vital signs
    latest_vital = await Vital.find(
        Vital.patient_id == PydanticObjectId(patient_id)
    ).sort([("recorded_at", -1)]).limit(1).to_list()
    
    # Create patient dict for Telegram service
    patient_dict = {
        "id": str(patient.id),
        "name": patient.name,
        "bed_number": patient.bed_number,
        "current_risk_score": latest_vital[0].risk_score if latest_vital else 85.0,
        "diagnosis": patient.diagnosis,
        "vitals": {
            "heart_rate": latest_vital[0].heart_rate if latest_vital else 118,
            "systolic_bp": latest_vital[0].systolic_bp if latest_vital else 86,
            "respiratory_rate": latest_vital[0].respiratory_rate if latest_vital else 29,
            "temperature": latest_vital[0].temperature if latest_vital else 39.2,
            "spo2": latest_vital[0].spo2 if latest_vital else 88,
            "lactate": latest_vital[0].lactate if latest_vital else 4.3,
        }
    }
    
    # Send critical alert to medical team
    try:
        telegram_results = await telegram_service.send_critical_alert(patient_dict)
        
        return {
            "status": "success",
            "message": f"🚨 Critical alert triggered for {patient.name}!",
            "patient": {
                "id": str(patient.id),
                "name": patient.name,
                "bed_number": patient.bed_number,
                "risk_score": patient_dict["current_risk_score"]
            },
            "telegram_notifications": telegram_results,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "success", 
            "message": f"🚨 Critical alert logged for {patient.name}",
            "patient": {
                "id": str(patient.id),
                "name": patient.name,
                "bed_number": patient.bed_number,
            },
            "telegram_notifications": {"error": str(e)},
            "note": "Alert processed but Telegram notification failed"
        }


@router.post("/{patient_id}/trigger-warning")
async def trigger_warning_alert(patient_id: str):
    """
    ⚠️ TRIGGER WARNING ALERT - Send to nurse only
    
    Manually triggers a warning alert for the specified patient
    and sends Telegram notification to nurse only.
    """
    from beanie import PydanticObjectId
    from datetime import datetime
    
    # Get patient data
    try:
        patient = await Patient.get(PydanticObjectId(patient_id))
    except:
        raise HTTPException(400, "Invalid patient ID format")
        
    if not patient:
        raise HTTPException(404, "Patient not found")
    
    # Get latest vital signs
    latest_vital = await Vital.find(
        Vital.patient_id == PydanticObjectId(patient_id)
    ).sort([("recorded_at", -1)]).limit(1).to_list()
    
    # Create patient dict for Telegram service
    patient_dict = {
        "id": str(patient.id),
        "name": patient.name,
        "bed_number": patient.bed_number,
        "current_risk_score": latest_vital[0].risk_score if latest_vital else 65.0,
        "diagnosis": patient.diagnosis,
        "vitals": {
            "heart_rate": latest_vital[0].heart_rate if latest_vital else 95,
            "systolic_bp": latest_vital[0].systolic_bp if latest_vital else 105,
            "respiratory_rate": latest_vital[0].respiratory_rate if latest_vital else 22,
            "temperature": latest_vital[0].temperature if latest_vital else 38.1,
            "spo2": latest_vital[0].spo2 if latest_vital else 94,
            "lactate": latest_vital[0].lactate if latest_vital else 2.8,
        }
    }
    
    # Send warning alert to nurse only
    try:
        telegram_results = await telegram_service.send_warning_alert(patient_dict)
        
        return {
            "status": "success",
            "message": f"⚠️ Warning alert sent to nurse for {patient.name}",
            "patient": {
                "id": str(patient.id),
                "name": patient.name,
                "bed_number": patient.bed_number,
                "risk_score": patient_dict["current_risk_score"]
            },
            "telegram_notifications": telegram_results,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "success", 
            "message": f"⚠️ Warning alert logged for {patient.name}",
            "patient": {
                "id": str(patient.id),
                "name": patient.name,
                "bed_number": patient.bed_number,
            },
            "telegram_notifications": {"error": str(e)},
            "note": "Alert processed but Telegram notification failed"
        }


@router.delete("/{patient_id}")
async def delete_patient(patient_id: str):
    from beanie import PydanticObjectId
    patient = await Patient.get(PydanticObjectId(patient_id))
    if not patient:
        raise HTTPException(404, "Patient not found")
    await patient.delete()
    return {"deleted": patient_id}