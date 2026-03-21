from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter(prefix="/protocols", tags=["Protocols"])

MOCK_PROTOCOLS = [
    {
        "_id": "prot_001",
        "patient_id": "pat_002",
        "status": "pending",
        "risk_score": 78.5,
        "gemini_recommendation": "Immediate sepsis protocol: Start broad-spectrum antibiotics, fluid resuscitation, obtain blood cultures",
        "antibiotic_suggestion": "Piperacillin-tazobactam 4.5g IV q6h",
        "immediate_actions": ["Blood cultures", "Lactate level", "IV access", "Fluid bolus 30ml/kg"],
        "created_at": "2024-01-01T12:00:00Z"
    }
]

@router.get("/pending")
async def get_pending_protocols():
    """Get pending protocols"""
    return [p for p in MOCK_PROTOCOLS if p["status"] == "pending"]

@router.post("/{protocol_id}/approve")
async def approve_protocol(protocol_id: str, data: Dict[str, Any]):
    """Approve a protocol"""
    return {"status": "approved", "protocol_id": protocol_id}