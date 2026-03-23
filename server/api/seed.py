"""
Seed API — Asclepius AI
Three endpoints for demo control:
  POST /seed/normal   → 🔵 Blue  — healthy vitals for all patients
  POST /seed/warning  → 🟡 Yellow — borderline sepsis vitals
  POST /seed/critical → 🔴 Red   — critical sepsis vitals

Each endpoint:
  1. Reads from data/seeds/{level}.csv  OR  uses inline defaults
  2. Ingests vitals for all active patients
  3. Triggers the full pipeline (risk score → alert → protocol → notifications)
  4. Sends Telegram notifications to medical staff
"""
import csv
import io
import os
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException

from models.patient import Patient
from services.vitals_service import ingest_vital
from services.telegram_service import telegram_service

router = APIRouter(prefix="/seed", tags=["Seed (Demo Control)"])

SEEDS_DIR = Path(__file__).parent.parent.parent / "data" / "seeds"

# Default vitals when no CSV uploaded
DEFAULTS = {
    "normal": {
        "heart_rate": 75.0,
        "systolic_bp": 120.0,
        "respiratory_rate": 16.0,
        "temperature": 37.0,
        "spo2": 98.0,
        "lactate": 1.0,
    },
    "warning": {
        "heart_rate": 98.0,
        "systolic_bp": 105.0,
        "respiratory_rate": 22.0,
        "temperature": 38.5,
        "spo2": 93.0,
        "lactate": 2.2,
    },
    "critical": {
        "heart_rate": 118.0,
        "systolic_bp": 88.0,
        "respiratory_rate": 28.0,
        "temperature": 39.2,
        "spo2": 88.0,
        "lactate": 4.1,
    },
}


async def _load_csv_vitals(level: str, csv_file: UploadFile | None) -> list[dict]:
    """Returns list of vital dicts from uploaded CSV or default CSV or hardcoded defaults."""
    # 1. Uploaded file takes priority
    if csv_file:
        content = await csv_file.read()
        reader = csv.DictReader(io.StringIO(content.decode()))
        return [_parse_row(row) for row in reader]

    # 2. Try pre-loaded seed file
    seed_path = SEEDS_DIR / f"{level}.csv"
    if seed_path.exists():
        with open(seed_path) as f:
            reader = csv.DictReader(f)
            return [_parse_row(row) for row in reader]

    # 3. Use hardcoded defaults (same for all patients)
    return [DEFAULTS[level]]


def _parse_row(row: dict) -> dict:
    return {
        "heart_rate": float(row["heart_rate"]),
        "systolic_bp": float(row["systolic_bp"]),
        "respiratory_rate": float(row["respiratory_rate"]),
        "temperature": float(row["temperature"]),
        "spo2": float(row["spo2"]),
        "lactate": float(row["lactate"]),
    }


async def _seed_all_patients(level: str, vitals_list: list[dict]) -> list[dict]:
    """Apply seed vitals to all active patients. Cycles through vitals_list if fewer rows than patients."""
    patients = await Patient.find_all().to_list()

    if not patients:
        raise HTTPException(400, "No patients in database. Create patients first.")

    outcomes = []
    for i, patient in enumerate(patients):
        vitals = vitals_list[i % len(vitals_list)]
        vital = await ingest_vital(patient.id, vitals, source=f"seed_{level}")
        outcomes.append({
            "patient_id": str(patient.id),
            "patient_name": patient.name,
            "bed": patient.bed_number,
            "risk_score": vital.risk_score,
            "risk_level": level,
            "vitals": vitals,
        })

    return outcomes


async def _send_telegram_notifications(level: str, outcomes: list[dict]) -> dict:
    """Send appropriate Telegram notifications based on seed level"""
    if level == "normal":
        return {"telegram": "No notifications sent for normal vitals"}
    
    telegram_results = {}
    
    try:
        if level == "warning":
            # Send to nurses only for warning
            message = f"""⚠️ <b>WARNING ALERT - SEED DATA</b>
            
<b>Alert Level:</b> WARNING 
<b>Patients Affected:</b> {len(outcomes)}
<b>Action:</b> Increased monitoring required

<b>Sample Patient Data:</b>
{outcomes[0]['patient_name']} ({outcomes[0]['bed']})
Risk Score: {outcomes[0]['risk_score']:.1f}

<b>⚠️ REVIEW ALL PATIENTS</b>
Check dashboard for complete status update.

<i>This is a demonstration alert from seed data</i>
🏥 Asclepius AI - ICU Sepsis Early Warning System"""
            
            telegram_results = await telegram_service.send_to_medical_team(message, level="warning")
        
        elif level == "critical":
            # Send to both nurses and doctors for critical
            critical_patients = [p for p in outcomes if p['risk_score'] > 70]
            
            message = f"""🚨 <b>CRITICAL ALERT - SEED DATA</b>
            
<b>Alert Level:</b> CRITICAL
<b>Patients in Critical State:</b> {len(critical_patients)}
<b>Total Patients Updated:</b> {len(outcomes)}

<b>Highest Risk Patient:</b>
{max(outcomes, key=lambda x: x['risk_score'])['patient_name']} ({max(outcomes, key=lambda x: x['risk_score'])['bed']})
Risk Score: {max(outcomes, key=lambda x: x['risk_score'])['risk_score']:.1f}

<b>🚨 IMMEDIATE ACTION REQUIRED</b>
• Review all patient protocols
• Check vital signs immediately  
• Prepare for potential interventions

<i>This is a demonstration alert from seed data</i>
🏥 Asclepius AI - ICU Sepsis Early Warning System"""
            
            telegram_results = await telegram_service.send_to_medical_team(message, level="critical", include_buttons=True)
        
        return {"telegram": telegram_results}
    
    except Exception as e:
        return {"telegram": {"error": str(e)}}


@router.post("/normal", summary="🔵 Seed Normal Vitals")
async def seed_normal(
    csv_file: UploadFile | None = File(default=None),
):
    """Inject healthy vitals — no alerts triggered."""
    vitals_list = await _load_csv_vitals("normal", csv_file)
    outcomes = await _seed_all_patients("normal", vitals_list)
    
    # No Telegram notifications for normal vitals
    telegram_status = {"telegram": "No notifications sent for normal vitals"}
    
    return {
        "seeded": "normal",
        "description": "🔵 All patients showing healthy vitals. No alerts triggered.",
        "patients_updated": len(outcomes),
        "results": outcomes,
        "notifications": telegram_status,
    }


@router.post("/warning", summary="🟡 Seed Warning Vitals")
async def seed_warning(
    csv_file: UploadFile | None = File(default=None),
):
    """Inject borderline vitals — nurse notifications triggered."""
    vitals_list = await _load_csv_vitals("warning", csv_file)
    outcomes = await _seed_all_patients("warning", vitals_list)
    
    # Send Telegram notifications
    telegram_status = await _send_telegram_notifications("warning", outcomes)
    
    return {
        "seeded": "warning",
        "description": "🟡 Borderline sepsis signals. Nurse notified via Telegram.",
        "patients_updated": len(outcomes),
        "results": outcomes,
        "notifications": telegram_status,
    }


@router.post("/critical", summary="🔴 Seed Critical Vitals")
async def seed_critical(
    csv_file: UploadFile | None = File(default=None),
):
    """Inject critical vitals — nurse + doctor notified, Gemini protocol generated."""
    vitals_list = await _load_csv_vitals("critical", csv_file)
    outcomes = await _seed_all_patients("critical", vitals_list)
    
    # Send Telegram notifications to medical team
    telegram_status = await _send_telegram_notifications("critical", outcomes)
    
    return {
        "seeded": "critical",
        "description": "🔴 Critical sepsis signals. Nurse + Doctor notified via Telegram. Gemini protocol generated.",
        "patients_updated": len(outcomes),
        "results": outcomes,
        "notifications": telegram_status,
    }