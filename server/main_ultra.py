"""
Asclepius AI — Ultra-minimal version for Render deployment
Pure FastAPI with mock data, no external dependencies
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from datetime import datetime
import json

app = FastAPI(
    title="Asclepius AI",
    description="ICU Sepsis Early Warning System — Ultra-minimal Version",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data
MOCK_PATIENTS = [
    {
        "id": "pat_001",
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
        },
        "active_alerts": 1
    },
    {
        "id": "pat_002", 
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
        },
        "active_alerts": 2
    }
]

MOCK_ALERTS = [
    {
        "id": "alert_001",
        "patient_id": "pat_002",
        "level": "critical",
        "message": "Sepsis critical: score 78.5. Factors: High lactate (3.8), Low BP (85), High RR (28)",
        "triggered_at": "2024-01-01T12:00:00Z",
        "resolved": False
    },
    {
        "id": "alert_002",
        "patient_id": "pat_001", 
        "level": "warning",
        "message": "Sepsis warning: score 45.2. Factors: High RR (22), Fever (38.1°C)",
        "triggered_at": "2024-01-01T12:30:00Z",
        "resolved": False
    }
]

MOCK_PROTOCOLS = [
    {
        "id": "prot_001",
        "patient_id": "pat_002",
        "status": "pending",
        "risk_score": 78.5,
        "gemini_recommendation": "Immediate sepsis protocol: Start broad-spectrum antibiotics, fluid resuscitation",
        "antibiotic_suggestion": "Piperacillin-tazobactam 4.5g IV q6h",
        "immediate_actions": ["Blood cultures", "Lactate level", "IV access", "Fluid bolus"],
        "created_at": "2024-01-01T12:00:00Z"
    }
]

# Health endpoints
@app.get("/", tags=["Health"])
async def root():
    return {
        "system": "Asclepius AI",
        "status": "online",
        "version": "1.0.0 (ultra-minimal)",
        "mode": "mock_data",
        "docs": "/docs",
    }

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "mode": "ultra-minimal"}

# Patient endpoints
@app.get("/patients/", tags=["Patients"])
async def get_patients():
    return MOCK_PATIENTS

@app.get("/patients/{patient_id}", tags=["Patients"])
async def get_patient(patient_id: str):
    for patient in MOCK_PATIENTS:
        if patient["id"] == patient_id:
            return patient
    return {"error": "Patient not found"}

@app.get("/patients/{patient_id}/vitals", tags=["Patients"])
async def get_patient_vitals(patient_id: str, limit: int = 20):
    return []  # Return empty for now

# Alert endpoints
@app.get("/alerts/", tags=["Alerts"])
async def get_alerts(resolved: bool = False):
    return [a for a in MOCK_ALERTS if a["resolved"] == resolved]

# Protocol endpoints
@app.get("/protocols/pending", tags=["Protocols"])
async def get_pending_protocols():
    return [p for p in MOCK_PROTOCOLS if p["status"] == "pending"]

# Analytics endpoints
@app.get("/analytics/stats", tags=["Analytics"])
async def get_analytics():
    return {
        "total_patients": len(MOCK_PATIENTS),
        "critical_patients": len([p for p in MOCK_PATIENTS if p["risk_level"] == "critical"]),
        "warning_patients": len([p for p in MOCK_PATIENTS if p["risk_level"] == "warning"]),
        "normal_patients": len([p for p in MOCK_PATIENTS if p["risk_level"] == "normal"]),
        "active_alerts": len([a for a in MOCK_ALERTS if not a["resolved"]]),
        "protocols_pending": len([p for p in MOCK_PROTOCOLS if p["status"] == "pending"]),
    }

# Seed endpoints
@app.post("/seed/normal", tags=["Seed"])
async def seed_normal():
    return {"status": "success", "message": "Normal patients seeded (mock)"}

@app.post("/seed/warning", tags=["Seed"])
async def seed_warning():
    return {"status": "success", "message": "Warning patients seeded (mock)"}

@app.post("/seed/critical", tags=["Seed"])
async def seed_critical():
    return {"status": "success", "message": "Critical patients seeded (mock)"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)