"""
Simple deployment-friendly main server for Render
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
import asyncio
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple FastAPI app
app = FastAPI(
    title="Asclepius AI - ICU Sepsis Early Warning System",
    description="AI-powered medical monitoring system",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data for deployment
MOCK_PATIENTS = [
    {
        "id": 1,
        "name": "Ramesh Kulkarni",
        "age": 62,
        "gender": "Male",
        "bed_number": "ICU-01",
        "diagnosis": "Post-abdominal surgery",
        "allergies": "Penicillin",
        "comorbidities": "Diabetes, Hypertension",
        "is_post_surgical": True,
        "is_immunocompromised": False,
        "current_risk_score": 87.5,
        "risk_level": "critical",
        "vitals": { 
            "heart_rate": 118, 
            "systolic_bp": 86, 
            "respiratory_rate": 29, 
            "temperature": 39.2, 
            "spo2": 88, 
            "lactate": 4.3 
        },
        "active_alerts": [
            { 
                "level": "critical", 
                "message": "Sepsis critical: score 87.5. Factors: Low SBP (86 mmHg), High RR (29 br/min), Very low SpO2 (88%)", 
                "at": datetime.now().isoformat()
            }
        ]
    },
    {
        "id": 2,
        "name": "Sunita Desai",
        "age": 45,
        "gender": "Female",
        "bed_number": "ICU-02",
        "diagnosis": "Pneumonia",
        "allergies": "",
        "comorbidities": "Asthma",
        "is_post_surgical": False,
        "is_immunocompromised": False,
        "current_risk_score": 54.2,
        "risk_level": "warning",
        "vitals": { 
            "heart_rate": 97, 
            "systolic_bp": 106, 
            "respiratory_rate": 22, 
            "temperature": 38.4, 
            "spo2": 93, 
            "lactate": 2.3 
        },
        "active_alerts": [
            { 
                "level": "warning", 
                "message": "Sepsis warning: score 54.2. Factors: High RR (22 br/min), High HR (97 bpm)", 
                "at": datetime.now().isoformat()
            }
        ]
    }
]

MOCK_ALERTS = [
    {
        "id": 1,
        "patient_id": 1,
        "level": "critical",
        "risk_score": 87.5,
        "message": "Sepsis critical: score 87.5. Factors: Low SBP (86 mmHg), High RR (29 br/min), Very low SpO2 (88%)",
        "nurse_notified": True,
        "doctor_notified": True,
        "resolved": False,
        "triggered_at": datetime.now().isoformat()
    }
]

MOCK_PROTOCOLS = [
    {
        "id": 1,
        "patient_id": 1,
        "alert_id": 1,
        "risk_score": 87.5,
        "status": "pending",
        "immediate_actions": "1. Obtain 2 sets of blood cultures before antibiotics\n2. Measure serum lactate (target <2 mmol/L)\n3. Administer 30 mL/kg IV crystalloid bolus (Normal Saline)\n4. Apply supplemental O2 — target SpO2 ≥94%\n5. Insert urinary catheter — monitor hourly output",
        "antibiotic_suggestion": "PENICILLIN ALLERGY NOTED — Piperacillin-Tazobactam EXCLUDED\n\nRecommend: Meropenem 1g IV q8h + Vancomycin 25 mg/kg IV loading dose",
        "rationale": "Post-surgical patient with septic shock requiring urgent intervention",
        "generated_at": datetime.now().isoformat()
    }
]

# Route handlers
@app.get("/")
async def root():
    return {
        "system": "Asclepius AI",
        "status": "🟢 Online",
        "version": "2.0.0",
        "mode": "deployment",
        "description": "ICU Sepsis Early Warning System",
        "endpoints": {
            "patients": "/patients/",
            "alerts": "/alerts/",
            "protocols": "/protocols/",
            "analytics": "/analytics/"
        }
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "system": "asclepius-ai"
    }

@app.get("/patients/")
async def get_patients():
    return MOCK_PATIENTS

@app.get("/patients/{patient_id}")
async def get_patient(patient_id: int):
    patient = next((p for p in MOCK_PATIENTS if p["id"] == patient_id), None)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@app.post("/patients/{patient_id}/trigger-critical")
async def trigger_critical_alert(patient_id: int):
    # Simulate Telegram notification
    logger.info(f"🚨 CRITICAL ALERT triggered for patient {patient_id}")
    logger.info("📤 Sending critical alert to nurse via Telegram...")
    logger.info("📤 Sending critical alert to doctor via Telegram...")
    logger.info("✅ Notifications sent!")
    
    return {
        "status": "success",
        "message": "🚨 Critical alert triggered! Doctor and Nurse notified via Telegram",
        "patient_id": patient_id,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/alerts/")
async def get_alerts(resolved: bool = False):
    if resolved:
        return []
    return MOCK_ALERTS

@app.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: int):
    return {"status": "resolved", "alert_id": alert_id}

@app.get("/protocols/pending")
async def get_pending_protocols():
    return MOCK_PROTOCOLS

@app.post("/protocols/{protocol_id}/approve")
async def approve_protocol(protocol_id: int, data: dict = None):
    return {"status": "approved", "protocol_id": protocol_id}

@app.post("/protocols/{protocol_id}/reject")
async def reject_protocol(protocol_id: int, data: dict = None):
    return {"status": "rejected", "protocol_id": protocol_id}

@app.get("/analytics/stats")
async def get_analytics_stats():
    return {
        "total_patients": 2,
        "critical_patients": 1,
        "warning_patients": 1,
        "normal_patients": 0,
        "active_alerts": 1,
        "protocols_pending": 1
    }

@app.get("/analytics/accuracy")
async def get_accuracy():
    return {
        "total_alerts": 1,
        "resolved_alerts": 0,
        "critical_alerts": 1,
        "warning_alerts": 0,
        "average_risk_score_at_alert": 87.5,
        "insights": [
            "System functioning normally in deployment mode",
            "Mock data being used for demonstration"
        ]
    }

@app.post("/seed/normal")
async def seed_normal():
    return {"status": "success", "message": "Normal patients seeded"}

@app.post("/seed/warning")
async def seed_warning():
    logger.info("📤 Sending warning alert to nurse via Telegram...")
    logger.info("✅ Nurse notified via Telegram")
    return {"status": "success", "message": "Warning patients seeded - Nurse notified via Telegram"}

@app.post("/seed/critical")
async def seed_critical():
    logger.info("📤 Sending critical alert to nurse via Telegram...")
    logger.info("📤 Sending critical alert to doctor via Telegram...")
    logger.info("✅ Doctor and Nurse notified via Telegram")
    return {"status": "success", "message": "Critical patients seeded - Doctor and Nurse notified via Telegram!"}

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🏥 Starting Asclepius AI server (Deployment Mode)...")
    uvicorn.run(
        "main_deploy:app", 
        host="0.0.0.0", 
        port=int(os.getenv("PORT", 8000)),
        reload=False
    )