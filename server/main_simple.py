"""
Minimal Asclepius AI Server for Testing Throttling
Works without Beanie/Pydantic 2.x dependencies
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Asclepius AI - Minimal Server",
    description="Minimal server to test alert throttling system",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory storage
patients_db = [
    {
        "id": "patient_1",
        "name": "John Doe",
        "bed_number": "ICU-101",
        "diagnosis": "Pneumonia",
        "risk_level": "normal",
        "current_risk_score": 25.5
    },
    {
        "id": "patient_2", 
        "name": "Sarah Johnson",
        "bed_number": "ICU-102",
        "diagnosis": "Post-surgery",
        "risk_level": "warning",
        "current_risk_score": 65.0
    }
]

alerts_db = []

# Simple Throttling System
class SimpleThrottleService:
    def __init__(self):
        self.alert_throttle = {}
        self.throttle_interval = timedelta(seconds=15)
        self.max_alerts_per_window = 1
        
    def configure_throttling(self, interval_seconds: int = 15):
        self.throttle_interval = timedelta(seconds=interval_seconds)
        logger.info(f"⏱️ Alert throttling configured: {interval_seconds}s interval")
    
    def _is_alert_throttled(self, patient_id: str, alert_level: str = "critical") -> Dict[str, Any]:
        now = datetime.now()
        patient_key = f"{patient_id}_{alert_level}"
        
        if patient_key not in self.alert_throttle:
            self.alert_throttle[patient_key] = {
                "last_sent": now,
                "count": 1,
                "first_sent": now
            }
            return {"throttled": False, "reason": "first_alert"}
        
        throttle_data = self.alert_throttle[patient_key]
        time_since_last = now - throttle_data["last_sent"]
        
        if time_since_last < self.throttle_interval:
            throttle_data["count"] += 1
            remaining_time = self.throttle_interval - time_since_last
            
            logger.warning(f"⏱️ Alert throttled for patient {patient_id}: {remaining_time.seconds}s remaining")
            return {
                "throttled": True, 
                "reason": "within_throttle_window",
                "remaining_seconds": remaining_time.seconds,
                "attempts_blocked": throttle_data["count"] - 1
            }
        else:
            throttle_data["last_sent"] = now
            throttle_data["count"] = 1
            return {"throttled": False, "reason": "throttle_window_expired"}
    
    def send_critical_alert(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        patient_id = patient_data.get('id', 'unknown')
        
        # Check throttling
        throttle_check = self._is_alert_throttled(patient_id, "critical")
        if throttle_check["throttled"]:
            logger.warning(f"🚫 Critical alert throttled for patient {patient_id}")
            return {
                "status": "throttled",
                "message": f"Alert throttled - {throttle_check['remaining_seconds']}s remaining",
                "throttle_info": throttle_check,
                "patient_id": patient_id
            }
        
        # Simulate sending alert
        logger.info(f"🚨 Critical alert sent for patient {patient_id}")
        
        # Add to alerts database
        alert = {
            "id": f"alert_{len(alerts_db) + 1}",
            "patient_id": patient_id,
            "level": "critical",
            "message": f"Critical alert for {patient_data.get('name', 'Unknown')}",
            "triggered_at": datetime.now().isoformat(),
            "resolved": False
        }
        alerts_db.append(alert)
        
        return {
            "status": "success",
            "message": f"🚨 Critical alert sent for {patient_data.get('name', 'Unknown')}",
            "throttle_info": {
                "throttle_interval_seconds": self.throttle_interval.seconds,
                "next_alert_allowed_at": (datetime.now() + self.throttle_interval).isoformat()
            }
        }

# Initialize throttling service
throttle_service = SimpleThrottleService()

# Routes
@app.get("/")
async def root():
    return {
        "system": "Asclepius AI - Minimal",
        "status": "🟢 Online",
        "features": {
            "alert_throttling": "✅ Active",
            "simple_database": "✅ In-Memory",
            "test_endpoints": "✅ Available"
        },
        "throttle_config": {
            "interval_seconds": throttle_service.throttle_interval.seconds,
            "active_throttles": len(throttle_service.alert_throttle)
        }
    }

@app.get("/api/patients/")
async def list_patients():
    return patients_db

@app.get("/api/alerts/")
async def list_alerts():
    return alerts_db

@app.post("/api/patients/{patient_id}/trigger-critical")
async def trigger_critical_alert(patient_id: str):
    # Find patient
    patient = next((p for p in patients_db if p["id"] == patient_id), None)
    if not patient:
        return {"error": "Patient not found"}
    
    # Add some sample vitals
    patient_with_vitals = {
        **patient,
        "vitals": {
            "heart_rate": 120,
            "systolic_bp": 85,
            "respiratory_rate": 28,
            "temperature": 39.1,
            "spo2": 88,
            "lactate": 4.2
        }
    }
    
    # Send critical alert (with throttling)
    result = throttle_service.send_critical_alert(patient_with_vitals)
    return result

# Throttle configuration endpoints
@app.get("/api/throttle/config")
async def get_throttle_config():
    return {
        "interval_seconds": throttle_service.throttle_interval.seconds,
        "max_alerts_per_window": throttle_service.max_alerts_per_window,
        "active_throttles": len(throttle_service.alert_throttle),
        "description": f"Alerts are limited to {throttle_service.max_alerts_per_window} per {throttle_service.throttle_interval.seconds}s window per patient"
    }

@app.post("/api/throttle/config")
async def set_throttle_config(config: dict):
    interval_seconds = config.get("interval_seconds", 15)
    throttle_service.configure_throttling(interval_seconds)
    
    return {
        "status": "success",
        "message": f"Throttling configured: {interval_seconds}s interval",
        "config": {
            "interval_seconds": interval_seconds,
            "max_alerts_per_window": 1
        }
    }

@app.delete("/api/throttle/throttles")
async def clear_throttles():
    count = len(throttle_service.alert_throttle)
    throttle_service.alert_throttle.clear()
    
    return {
        "status": "success",
        "message": f"Cleared {count} active throttles",
        "cleared_count": count
    }

@app.get("/api/throttle/status/{patient_id}")
async def get_patient_throttle_status(patient_id: str):
    critical_key = f"{patient_id}_critical"
    
    if critical_key in throttle_service.alert_throttle:
        data = throttle_service.alert_throttle[critical_key]
        time_remaining = (data["last_sent"] + throttle_service.throttle_interval - datetime.now()).total_seconds()
        return {
            "patient_id": patient_id,
            "throttled": time_remaining > 0,
            "last_sent": data["last_sent"].isoformat(),
            "count_this_window": data["count"],
            "seconds_until_next_allowed": max(0, int(time_remaining))
        }
    else:
        return {
            "patient_id": patient_id,
            "throttled": False,
            "message": "No previous alerts - next alert will be sent immediately"
        }

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🏥 Starting Minimal Asclepius AI server...")
    logger.info("🔧 This version works without complex dependencies")
    logger.info("⏱️ Alert throttling system is active")
    
    uvicorn.run(
        "main_simple:app", 
        host="0.0.0.0", 
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )