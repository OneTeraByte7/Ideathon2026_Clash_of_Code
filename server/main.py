"""
Asclepius AI — Enhanced version with realistic data and Telegram integration
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from datetime import datetime, timedelta
import json
import asyncio
import os
import httpx

app = FastAPI(
    title="Asclepius AI",
    description="ICU Sepsis Early Warning System — Enhanced with Telegram",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Telegram configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_NURSE_CHAT_ID = os.getenv("TELEGRAM_NURSE_CHAT_ID", "")
TELEGRAM_DOCTOR_CHAT_ID = os.getenv("TELEGRAM_DOCTOR_CHAT_ID", "")

async def send_telegram_message(chat_id: str, message: str, parse_mode: str = "HTML"):
    """Send message via Telegram Bot API"""
    if not TELEGRAM_BOT_TOKEN or not chat_id:
        print(f"📤 Would send to chat {chat_id}: {message}")
        return {"status": "success", "message": "Demo mode - Telegram not configured"}
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": parse_mode
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)
            if response.status_code == 200:
                print(f"✅ Telegram message sent to {chat_id}")
                return {"status": "success"}
            else:
                print(f"❌ Telegram error: {response.text}")
                return {"status": "error", "message": response.text}
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        return {"status": "error", "message": str(e)}

# Realistic mock data - like the original
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
                "at": datetime.utcnow().isoformat()
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
                "at": datetime.utcnow().isoformat()
            }
        ]
    },
    {
        "id": 3,
        "name": "Arjun Mehta",
        "age": 71,
        "gender": "Male",
        "bed_number": "ICU-03",
        "diagnosis": "UTI with suspected sepsis",
        "allergies": "Sulfonamides",
        "comorbidities": "CKD Stage 3, Diabetes",
        "is_post_surgical": False,
        "is_immunocompromised": True,
        "current_risk_score": 19.0,
        "risk_level": "normal",
        "vitals": {
            "heart_rate": 74,
            "systolic_bp": 122,
            "respiratory_rate": 17,
            "temperature": 37.1,
            "spo2": 97,
            "lactate": 1.1
        },
        "active_alerts": []
    },
    {
        "id": 4,
        "name": "Priya Nair",
        "age": 38,
        "gender": "Female",
        "bed_number": "ICU-04",
        "diagnosis": "Post-cardiac surgery",
        "allergies": "",
        "comorbidities": "None",
        "is_post_surgical": True,
        "is_immunocompromised": False,
        "current_risk_score": 7.0,
        "risk_level": "normal",
        "vitals": {
            "heart_rate": 68,
            "systolic_bp": 118,
            "respiratory_rate": 14,
            "temperature": 36.8,
            "spo2": 99,
            "lactate": 0.9
        },
        "active_alerts": []
    },
    {
        "id": 5,
        "name": "Mohan Sharma",
        "age": 55,
        "gender": "Male",
        "bed_number": "ICU-05",
        "diagnosis": "Liver failure",
        "allergies": "Cephalosporins",
        "comorbidities": "Cirrhosis, Malnutrition",
        "is_post_surgical": False,
        "is_immunocompromised": True,
        "current_risk_score": 62.8,
        "risk_level": "warning",
        "vitals": {
            "heart_rate": 101,
            "systolic_bp": 104,
            "respiratory_rate": 23,
            "temperature": 38.6,
            "spo2": 92,
            "lactate": 2.5
        },
        "active_alerts": [
            {
                "level": "warning",
                "message": "Sepsis warning: score 62.8. Factors: High RR, immunocompromised (+8 adjustment)",
                "at": datetime.utcnow().isoformat()
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
        "message": "Sepsis critical: score 87.5. Factors: Low SBP (86 mmHg), High RR (29 br/min), Very low SpO2 (88%) — possible altered mentation",
        "nurse_notified": True,
        "doctor_notified": True,
        "resolved": False,
        "triggered_at": (datetime.utcnow().replace(microsecond=0) - timedelta(minutes=8)).isoformat()
    },
    {
        "id": 2,
        "patient_id": 2,
        "level": "warning",
        "risk_score": 54.2,
        "message": "Sepsis warning: score 54.2. Factors: High RR (22 br/min), High HR (97 bpm)",
        "nurse_notified": True,
        "doctor_notified": False,
        "resolved": False,
        "triggered_at": (datetime.utcnow().replace(microsecond=0) - timedelta(minutes=22)).isoformat()
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
        "antibiotic_suggestion": "PENICILLIN ALLERGY NOTED — Piperacillin-Tazobactam EXCLUDED\n\nRecommend: Meropenem 1g IV q8h (renal function unknown — reassess CrCl)\n+ Vancomycin 25 mg/kg IV loading dose (trough-guided)\n\nRationale: Post-surgical abdominal source, gram-negative + MRSA coverage needed",
        "rationale": "Post-abdominal surgery patient with compensated septic shock (SBP 86, lactate 4.3). Penicillin allergy requires carbapenem-based regimen. Immunocompetent but surgical site infection risk is high. Urgent source control evaluation within 6 hours.",
        "generated_at": (datetime.utcnow().replace(microsecond=0) - timedelta(minutes=5)).isoformat()
    }
]

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Simple WebSocket endpoint for real-time updates"""
    await websocket.accept()
    try:
        while True:
            # Send mock real-time data every 5 seconds
            data = {
                "type": "patient_update",
                "timestamp": datetime.utcnow().isoformat(),
                "patients": [
                    {
                        "id": "pat_001",
                        "risk_score": 45.2,
                        "risk_level": "warning",
                        "vitals": {"heart_rate": 95, "spo2": 94},
                        "active_alerts": 1
                    },
                    {
                        "id": "pat_002", 
                        "risk_score": 78.5,
                        "risk_level": "critical",
                        "vitals": {"heart_rate": 110, "spo2": 88},
                        "active_alerts": 2
                    }
                ]
            }
            await websocket.send_text(json.dumps(data))
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        print("WebSocket client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")

# Health endpoints
@app.get("/", tags=["Health"])
async def root():
    return {
        "system": "Asclepius AI",
        "status": "online",
        "version": "1.0.0 (ultra-minimal)",
        "mode": "mock_data",
        "docs": "/docs",
        "websocket": "/ws"
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

# Seed endpoints with Telegram notifications
@app.post("/seed/normal", tags=["Seed"])
async def seed_normal():
    return {"status": "success", "message": "Normal patients seeded (mock)"}

@app.post("/seed/warning", tags=["Seed"])
async def seed_warning():
    # Send notification to nurse
    message = "⚠️ <b>WARNING ALERT</b>\n\nNew warning-level patients added to ICU monitoring.\n\nPlease review dashboard for details.\n\n🏥 Asclepius AI System"
    
    result = await send_telegram_message(TELEGRAM_NURSE_CHAT_ID, message)
    
    return {
        "status": "success", 
        "message": "Warning patients seeded - Nurse notified via Telegram ✅",
        "telegram_status": result.get("status", "unknown")
    }

@app.post("/seed/critical", tags=["Seed"])
async def seed_critical():
    # Send critical alerts to both nurse and doctor
    critical_message = """🚨 <b>CRITICAL ALERT</b>
    
<b>Patient:</b> Ramesh Kulkarni (ICU-01)
<b>Risk Score:</b> 87.5 (CRITICAL)
<b>Condition:</b> Post-abdominal surgery with sepsis

<b>Critical Factors:</b>
• Low SBP: 86 mmHg
• High Respiratory Rate: 29 br/min  
• Very low SpO2: 88%
• High Lactate: 4.3 mmol/L

<b>IMMEDIATE ACTION REQUIRED</b>
Protocol generated - Review dashboard immediately.

🏥 Asclepius AI System"""

    # Send to both nurse and doctor
    nurse_result = await send_telegram_message(TELEGRAM_NURSE_CHAT_ID, critical_message)
    doctor_result = await send_telegram_message(TELEGRAM_DOCTOR_CHAT_ID, critical_message)
    
    return {
        "status": "success",
        "message": "🚨 Critical patients seeded - Doctor and Nurse notified via Telegram!",
        "nurse_notification": nurse_result.get("status", "unknown"),
        "doctor_notification": doctor_result.get("status", "unknown")
    }

# Trigger critical alert manually
@app.post("/patients/{patient_id}/trigger-critical", tags=["Patients"])
async def trigger_critical_alert(patient_id: int):
    # Find patient
    patient = None
    for p in MOCK_PATIENTS:
        if p["id"] == patient_id:
            patient = p
            break
    
    if not patient:
        return {"status": "error", "message": "Patient not found"}
    
    # Create critical alert message
    critical_message = f"""🚨 <b>CRITICAL ALERT TRIGGERED</b>
    
<b>Patient:</b> {patient['name']} ({patient['bed_number']})
<b>Risk Score:</b> {patient['current_risk_score']} (CRITICAL)
<b>Diagnosis:</b> {patient['diagnosis']}

<b>Current Vitals:</b>
• Heart Rate: {patient['vitals']['heart_rate']} bpm
• Blood Pressure: {patient['vitals']['systolic_bp']} mmHg
• Respiratory Rate: {patient['vitals']['respiratory_rate']} br/min
• Temperature: {patient['vitals']['temperature']}°C  
• SpO2: {patient['vitals']['spo2']}%
• Lactate: {patient['vitals']['lactate']} mmol/L

<b>🚨 IMMEDIATE INTERVENTION REQUIRED</b>
Review protocol on dashboard now!

🏥 Asclepius AI System"""

    # Send to both nurse and doctor
    print(f"📤 Sending critical alert for patient {patient['name']}")
    nurse_result = await send_telegram_message(TELEGRAM_NURSE_CHAT_ID, critical_message)
    doctor_result = await send_telegram_message(TELEGRAM_DOCTOR_CHAT_ID, critical_message)
    
    return {
        "status": "success",
        "message": f"🚨 Critical alert sent for {patient['name']}! Notifications sent to medical team.",
        "patient": patient['name'],
        "nurse_notification": nurse_result.get("status", "unknown"),
        "doctor_notification": doctor_result.get("status", "unknown")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)