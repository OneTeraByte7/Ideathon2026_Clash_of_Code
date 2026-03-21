"""
WebSocket — Asclepius AI
Streams live patient data to the ICU dashboard every 5 seconds.
Frontend connects to ws://host/ws/icu to receive updates.
"""
import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from db.database import AsyncSessionLocal
from models.patient import Patient
from models.vital import Vital
from models.alert import Alert
from sqlalchemy import desc

router = APIRouter(tags=["WebSocket"])

# Track connected clients
_connections: list[WebSocket] = []


async def broadcast(data: dict):
    """Push update to all connected dashboards."""
    dead = []
    for ws in _connections:
        try:
            await ws.send_json(data)
        except Exception:
            dead.append(ws)
    for ws in dead:
        _connections.remove(ws)


@router.websocket("/ws/icu")
async def icu_dashboard_stream(websocket: WebSocket):
    await websocket.accept()
    _connections.append(websocket)
    try:
        while True:
            snapshot = await _build_snapshot()
            await websocket.send_json(snapshot)
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        _connections.remove(websocket)


async def _build_snapshot() -> dict:
    async with AsyncSessionLocal() as db:
        patients = (await db.execute(select(Patient).order_by(Patient.bed_number))).scalars().all()

        patient_data = []
        for p in patients:
            # Latest vital
            latest_vital = (await db.execute(
                select(Vital)
                .where(Vital.patient_id == p.id)
                .order_by(desc(Vital.recorded_at))
                .limit(1)
            )).scalar_one_or_none()

            # Active alerts
            active_alerts = (await db.execute(
                select(Alert)
                .where(Alert.patient_id == p.id, Alert.resolved == False)
                .order_by(desc(Alert.triggered_at))
                .limit(3)
            )).scalars().all()

            patient_data.append({
                "id": p.id,
                "name": p.name,
                "bed": p.bed_number,
                "risk_score": p.current_risk_score,
                "risk_level": p.risk_level,
                "vitals": {
                    "heart_rate": latest_vital.heart_rate if latest_vital else None,
                    "systolic_bp": latest_vital.systolic_bp if latest_vital else None,
                    "respiratory_rate": latest_vital.respiratory_rate if latest_vital else None,
                    "temperature": latest_vital.temperature if latest_vital else None,
                    "spo2": latest_vital.spo2 if latest_vital else None,
                    "lactate": latest_vital.lactate if latest_vital else None,
                    "recorded_at": latest_vital.recorded_at.isoformat() if latest_vital else None,
                } if latest_vital else None,
                "active_alerts": [
                    {"level": a.level, "message": a.message, "at": a.triggered_at.isoformat()}
                    for a in active_alerts
                ],
            })

        return {
            "type": "icu_snapshot",
            "patients": patient_data,
            "critical_count": sum(1 for p in patients if p.risk_level == "critical"),
            "warning_count": sum(1 for p in patients if p.risk_level == "warning"),
        }