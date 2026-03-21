from fastapi import APIRouter, WebSocket
import json
import asyncio

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    try:
        while True:
            # Send mock real-time data
            data = {
                "type": "patient_update",
                "patients": [
                    {
                        "id": "pat_001",
                        "risk_score": 45.2,
                        "risk_level": "warning",
                        "vitals": {"heart_rate": 95, "spo2": 94}
                    },
                    {
                        "id": "pat_002", 
                        "risk_score": 78.5,
                        "risk_level": "critical",
                        "vitals": {"heart_rate": 110, "spo2": 88}
                    }
                ]
            }
            await websocket.send_text(json.dumps(data))
            await asyncio.sleep(5)  # Send updates every 5 seconds
    except Exception:
        pass