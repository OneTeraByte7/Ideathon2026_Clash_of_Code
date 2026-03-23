"""
WebSocket — Asclepius AI
Streams live patient data to the ICU dashboard every 5 seconds.
Frontend connects to ws://host/ws/icu to receive updates.
"""
import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from models.patient import Patient
from models.vital import Vital
from models.alert import Alert

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
    client_ip = websocket.client.host if websocket.client else "unknown"
    print(f"📡 WebSocket connection from {client_ip}")
    
    await websocket.accept()
    _connections.append(websocket)
    
    try:
        # Send initial snapshot immediately
        initial_snapshot = await _build_snapshot()
        await websocket.send_json(initial_snapshot)
        print(f"✅ Initial snapshot sent to {client_ip}")
        
        # Keep connection alive with heartbeat
        heartbeat_count = 0
        
        while True:
            # Wait before sending next update
            await asyncio.sleep(5)
            
            try:
                # Send heartbeat every 6 cycles (30 seconds)
                if heartbeat_count % 6 == 0:
                    # Just send a small ping
                    await websocket.send_json({
                        "type": "heartbeat",
                        "timestamp": asyncio.get_event_loop().time()
                    })
                else:
                    # Send full snapshot
                    snapshot = await _build_snapshot()
                    await websocket.send_json(snapshot)
                
                heartbeat_count += 1
                
            except Exception as e:
                print(f"❌ Error sending to {client_ip}: {e}")
                break  # Exit loop to close connection
                
    except WebSocketDisconnect:
        print(f"🔌 WebSocket disconnected: {client_ip}")
    except Exception as e:
        print(f"❌ WebSocket error for {client_ip}: {e}")
    finally:
        # Clean up connection
        if websocket in _connections:
            _connections.remove(websocket)
            print(f"🧹 Cleaned up connection for {client_ip}")


async def _build_snapshot() -> dict:
    """Build ICU snapshot with error handling"""
    try:
        patients = await Patient.find_all().sort([("bed_number", 1)]).to_list()
    except Exception as e:
        print(f"Database error fetching patients: {e}")
        return {
            "type": "error",
            "message": "Database connection issues",
            "patients": [],
            "critical_count": 0,
            "warning_count": 0,
        }

    patient_data = []
    critical_count = 0
    warning_count = 0
    
    for p in patients:
        try:
            # Count risk levels
            if p.risk_level == "critical":
                critical_count += 1
            elif p.risk_level == "warning":
                warning_count += 1
                
            # Latest vital with error handling
            latest_vital = None
            try:
                vitals = await Vital.find(Vital.patient_id == p.id).sort([("recorded_at", -1)]).limit(1).to_list()
                latest_vital = vitals[0] if vitals else None
            except Exception as e:
                print(f"Error fetching vitals for patient {p.id}: {e}")

            # Active alerts with error handling
            active_alerts = []
            try:
                alerts = await Alert.find(Alert.patient_id == p.id, Alert.resolved == False).sort([("triggered_at", -1)]).limit(3).to_list()
                active_alerts = [
                    {"level": a.level, "message": a.message, "at": a.triggered_at.isoformat()}
                    for a in alerts
                ]
            except Exception as e:
                print(f"Error fetching alerts for patient {p.id}: {e}")

            patient_data.append({
                "id": str(p.id),
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
                "active_alerts": active_alerts,
            })
            
        except Exception as e:
            print(f"Error processing patient {p.id}: {e}")
            # Add minimal patient data
            patient_data.append({
                "id": str(p.id),
                "name": p.name,
                "bed": p.bed_number,
                "risk_score": 0,
                "risk_level": "unknown",
                "vitals": None,
                "active_alerts": [],
            })

    return {
        "type": "icu_snapshot",
        "patients": patient_data,
        "critical_count": critical_count,
        "warning_count": warning_count,
        "timestamp": asyncio.get_event_loop().time()
    }