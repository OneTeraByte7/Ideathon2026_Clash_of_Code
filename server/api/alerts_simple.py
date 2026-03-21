from fastapi import APIRouter
from typing import List, Dict, Any
from datetime import datetime
from db.simple_mongo import alerts
import uuid

router = APIRouter(prefix="/alerts", tags=["Alerts"])

# Mock alerts data
MOCK_ALERTS = [
    {
        "_id": "alert_001",
        "patient_id": "pat_002",
        "level": "critical",
        "message": "Sepsis critical: score 78.5. Factors: High lactate (3.8), Low BP (85), High RR (28)",
        "triggered_at": datetime.utcnow().isoformat(),
        "resolved": False
    },
    {
        "_id": "alert_002",
        "patient_id": "pat_001", 
        "level": "warning",
        "message": "Sepsis warning: score 45.2. Factors: High RR (22), Fever (38.1°C)",
        "triggered_at": datetime.utcnow().isoformat(),
        "resolved": False
    }
]

@router.get("/")
async def get_alerts(resolved: bool = False):
    """Get alerts"""
    try:
        db_alerts = await alerts.find_all({"resolved": resolved})
        if db_alerts:
            return db_alerts
        return [a for a in MOCK_ALERTS if a["resolved"] == resolved]
    except Exception:
        return [a for a in MOCK_ALERTS if a["resolved"] == resolved]

@router.post("/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """Resolve an alert"""
    try:
        result = await alerts.update_one(
            {"_id": alert_id},
            {"resolved": True, "resolved_at": datetime.utcnow().isoformat()}
        )
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}