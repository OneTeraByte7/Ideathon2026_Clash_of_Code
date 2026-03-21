from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone

from models.protocol import Protocol
from services.vitals_service import approve_protocol

router = APIRouter(prefix="/protocols", tags=["Protocols"])


class ReviewRequest(BaseModel):
    reviewed_by: str
    notes: str = ""
    action: str = "approved"  # approved | modified | rejected


@router.get("/")
async def list_protocols(
    status: str | None = None,
    limit: int = 20,
):
    query_filter = {}
    if status:
        query_filter["status"] = status
    protocols = await Protocol.find(query_filter).sort("-generated_at").limit(limit).to_list()
    return protocols


@router.get("/pending")
async def pending_protocols():
    """All protocols awaiting doctor review."""
    protocols = await Protocol.find(Protocol.status == "pending").sort("-generated_at").to_list()
    return protocols


@router.get("/{protocol_id}")
async def get_protocol(protocol_id: str):
    from beanie import PydanticObjectId
    protocol = await Protocol.get(PydanticObjectId(protocol_id))
    if not protocol:
        raise HTTPException(404, "Protocol not found")
    return protocol


@router.patch("/{protocol_id}/review")
async def review_protocol(
    protocol_id: str,
    body: ReviewRequest,
):
    """
    Doctor reviews and approves/rejects the Gemini-generated protocol.
    On approval → nurse is automatically notified to implement.
    """
    from beanie import PydanticObjectId
    protocol = await Protocol.get(PydanticObjectId(protocol_id))
    if not protocol:
        raise HTTPException(404, "Protocol not found")
    if protocol.status != "pending":
        raise HTTPException(400, f"Protocol already {protocol.status}")

    if body.action == "approved":
        updated = await approve_protocol(PydanticObjectId(protocol_id), body.reviewed_by, body.notes)
        return {
            "status": "approved",
            "protocol_id": protocol_id,
            "nurse_notified": updated.nurse_notified,
            "message": "Protocol approved. Nurse has been notified to implement orders.",
        }

    # Modified or rejected — update status without nurse notification
    protocol.status = body.action
    protocol.reviewed_by = body.reviewed_by
    protocol.reviewed_at = datetime.now(timezone.utc)
    protocol.doctor_notes = body.notes
    await protocol.save()
    return {"status": body.action, "protocol_id": protocol_id}


@router.get("/patient/{patient_id}")
async def patient_protocols(patient_id: str):
    from beanie import PydanticObjectId
    protocols = await Protocol.find(Protocol.patient_id == PydanticObjectId(patient_id)).sort("-generated_at").limit(10).to_list()
    return protocols