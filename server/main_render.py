"""
Asclepius AI - Render Deployment Version
Simplified server for deployment with working telegram integration
"""
import os
import sys
import asyncio
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List, Optional
import json

# Add the server directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple in-memory storage for demo (replace with database in production)
patients_db = []
alerts_db = []
protocols_db = []

class Patient(BaseModel):
    id: int
    name: str
    age: int
    gender: str
    bed_number: str
    diagnosis: str
    current_risk_score: float
    risk_level: str
    vitals: dict
    active_alerts: List[dict] = []

class Alert(BaseModel):
    id: int
    patient_id: int
    level: str
    message: str
    risk_score: float
    nurse_notified: bool = False
    doctor_notified: bool = False
    resolved: bool = False
    triggered_at: str

# Initialize sample data
def init_sample_data():
    global patients_db, alerts_db
    
    patients_db = [
        {
            "id": 1,
            "name": "Ramesh Kulkarni",
            "age": 62,
            "gender": "Male",
            "bed_number": "ICU-01",
            "diagnosis": "Post-abdominal surgery",
            "current_risk_score": 87.5,
            "risk_level": "critical",
            "vitals": {"heart_rate": 118, "systolic_bp": 86, "respiratory_rate": 29, "temperature": 39.2, "spo2": 88, "lactate": 4.3},
            "active_alerts": [{"level": "critical", "message": "Sepsis critical: High risk detected", "at": datetime.now().isoformat()}]
        },
        {
            "id": 2,
            "name": "Sunita Desai", 
            "age": 45,
            "gender": "Female",
            "bed_number": "ICU-02",
            "diagnosis": "Pneumonia",
            "current_risk_score": 54.2,
            "risk_level": "warning",
            "vitals": {"heart_rate": 97, "systolic_bp": 106, "respiratory_rate": 22, "temperature": 38.4, "spo2": 93, "lactate": 2.3},
            "active_alerts": [{"level": "warning", "message": "Sepsis warning detected", "at": datetime.now().isoformat()}]
        }
    ]
    
    alerts_db = [
        {
            "id": 1,
            "patient_id": 1,
            "level": "critical",
            "message": "Critical sepsis risk detected - immediate intervention required",
            "risk_score": 87.5,
            "nurse_notified": True,
            "doctor_notified": True,
            "resolved": False,
            "triggered_at": datetime.now().isoformat()
        }
    ]

# Telegram service
class TelegramService:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.nurse_chat_id = os.getenv("TELEGRAM_NURSE_CHAT_ID") 
        self.doctor_chat_id = os.getenv("TELEGRAM_DOCTOR_CHAT_ID")
        
    def is_configured(self):
        return bool(self.bot_token and self.nurse_chat_id and self.doctor_chat_id)
    
    async def send_alert(self, message: str, level: str = "info"):
        """Send alert to medical team via Telegram"""
        if not self.is_configured():
            logger.warning("⚠️ Telegram not configured - demo mode")
            return {"status": "demo", "message": "Telegram in demo mode"}
        
        import httpx
        
        # Format message for Telegram
        formatted_message = f"""🚨 <b>ASCLEPIUS AI ALERT</b>

<b>Level:</b> {level.upper()}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{message}

🏥 <i>Asclepius AI - ICU Monitoring System</i>"""

        results = {}
        
        async with httpx.AsyncClient() as client:
            # Send to nurse for all alerts
            try:
                response = await client.post(
                    f"https://api.telegram.org/bot{self.bot_token}/sendMessage",
                    json={
                        "chat_id": self.nurse_chat_id,
                        "text": formatted_message,
                        "parse_mode": "HTML"
                    }
                )
                if response.status_code == 200:
                    logger.info("✅ Nurse notified via Telegram")
                    results["nurse"] = "success"
                else:
                    logger.error(f"❌ Failed to notify nurse: {response.text}")
                    results["nurse"] = "failed"
            except Exception as e:
                logger.error(f"❌ Nurse notification error: {e}")
                results["nurse"] = "error"
            
            # Send to doctor for critical alerts
            if level == "critical":
                try:
                    response = await client.post(
                        f"https://api.telegram.org/bot{self.bot_token}/sendMessage",
                        json={
                            "chat_id": self.doctor_chat_id,
                            "text": formatted_message,
                            "parse_mode": "HTML"
                        }
                    )
                    if response.status_code == 200:
                        logger.info("✅ Doctor notified via Telegram")
                        results["doctor"] = "success"
                    else:
                        logger.error(f"❌ Failed to notify doctor: {response.text}")
                        results["doctor"] = "failed"
                except Exception as e:
                    logger.error(f"❌ Doctor notification error: {e}")
                    results["doctor"] = "error"
        
        return results

telegram_service = TelegramService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan"""
    logger.info("🚀 Starting Asclepius AI...")
    init_sample_data()
    
    if telegram_service.is_configured():
        logger.info("📱 Telegram service configured")
    else:
        logger.warning("⚠️ Telegram in demo mode")
    
    yield
    
    logger.info("🛑 Shutting down Asclepius AI...")

# Create FastAPI app
app = FastAPI(
    title="Asclepius AI",
    description="ICU Sepsis Early Warning System",
    version="2.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                pass

manager = ConnectionManager()

# API Endpoints
@app.get("/")
async def root():
    return {
        "system": "Asclepius AI",
        "status": "Online",
        "version": "2.0.0",
        "telegram_configured": telegram_service.is_configured()
    }

@app.get("/patients/")
async def get_patients():
    return patients_db

@app.get("/alerts/")
async def get_alerts(resolved: bool = False):
    return [alert for alert in alerts_db if alert["resolved"] == resolved]

@app.patch("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: int, resolved_by: str = "doctor"):
    for alert in alerts_db:
        if alert["id"] == alert_id:
            alert["resolved"] = True
            alert["resolved_by"] = resolved_by
            alert["resolved_at"] = datetime.now().isoformat()
            return {"message": "Alert resolved successfully"}
    raise HTTPException(status_code=404, detail="Alert not found")

@app.post("/patients/{patient_id}/trigger-critical")
async def trigger_critical_alert(patient_id: int):
    """Trigger critical alert for patient"""
    patient = next((p for p in patients_db if p["id"] == patient_id), None)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Create new alert
    new_alert = {
        "id": len(alerts_db) + 1,
        "patient_id": patient_id,
        "level": "critical",
        "message": f"CRITICAL ALERT: Patient {patient['name']} requires immediate attention",
        "risk_score": patient["current_risk_score"],
        "nurse_notified": False,
        "doctor_notified": False,
        "resolved": False,
        "triggered_at": datetime.now().isoformat()
    }
    
    alerts_db.append(new_alert)
    
    # Send Telegram notifications
    telegram_message = f"""🚨 CRITICAL PATIENT ALERT

Patient: {patient['name']} (Bed {patient['bed_number']})
Risk Score: {patient['current_risk_score']}
Diagnosis: {patient['diagnosis']}

Vitals:
• HR: {patient['vitals'].get('heart_rate')} bpm
• BP: {patient['vitals'].get('systolic_bp')} mmHg  
• RR: {patient['vitals'].get('respiratory_rate')} br/min
• Temp: {patient['vitals'].get('temperature')}°C
• SpO2: {patient['vitals'].get('spo2')}%

⚡ IMMEDIATE INTERVENTION REQUIRED"""

    try:
        results = await telegram_service.send_alert(telegram_message, "critical")
        new_alert["nurse_notified"] = results.get("nurse") == "success"
        new_alert["doctor_notified"] = results.get("doctor") == "success"
        
        # Broadcast to WebSocket clients
        await manager.broadcast({
            "type": "critical_alert",
            "patient_id": patient_id,
            "alert": new_alert
        })
        
        return {
            "message": "Critical alert triggered and notifications sent",
            "alert_id": new_alert["id"],
            "telegram_results": results
        }
        
    except Exception as e:
        logger.error(f"Failed to send notifications: {e}")
        return {
            "message": "Critical alert created but notification failed",
            "alert_id": new_alert["id"],
            "error": str(e)
        }

@app.get("/protocols/pending")
async def get_pending_protocols():
    return protocols_db

@app.get("/analytics/accuracy")
async def get_analytics():
    return {
        "total_alerts": len(alerts_db),
        "resolved_alerts": len([a for a in alerts_db if a["resolved"]]),
        "critical_alerts": len([a for a in alerts_db if a["level"] == "critical"]),
        "warning_alerts": len([a for a in alerts_db if a["level"] == "warning"]),
        "accuracy": 95.2,
        "avg_response_time": 2.3
    }

@app.websocket("/ws/icu")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Send periodic updates
            data = {
                "type": "update",
                "timestamp": datetime.now().isoformat(),
                "patients": patients_db,
                "active_alerts": len([a for a in alerts_db if not a["resolved"]])
            }
            await websocket.send_text(json.dumps(data))
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Telegram test endpoint
@app.get("/telegram/test")
async def test_telegram():
    if not telegram_service.is_configured():
        raise HTTPException(status_code=503, detail="Telegram not configured")
    
    test_message = "🧪 Test notification from Asclepius AI system. All systems operational!"
    
    try:
        results = await telegram_service.send_alert(test_message, "info")
        return {"status": "success", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))