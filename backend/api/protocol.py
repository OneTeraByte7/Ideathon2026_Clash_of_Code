from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel

from db.database import get_db
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
    db: AsyncSession = Depends(get_db),
):
    query = select(Protocol).order_by(desc(Protocol.generated_at)).limit(limit)
    if status:
        query = query.where(Protocol.status == status)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/pending")
async def pending_protocols(db: AsyncSession = Depends(get_db)):
    """All protocols awaiting doctor review."""
    result = await db.execute(
        select(Protocol)
        .where(Protocol.status == "pending")
        .order_by(desc(Protocol.generated_at))
    )
    return result.scalars().all()


@router.get("/{protocol_id}")
async def get_protocol(protocol_id: int, db: AsyncSession = Depends(get_db)):
    protocol = await db.get(Protocol, protocol_id)
    if not protocol:
        raise HTTPException(404, "Protocol not found")
    return protocol


@router.patch("/{protocol_id}/review")
async def review_protocol(
    protocol_id: int,
    body: ReviewRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Doctor reviews and approves/rejects the Gemini-generated protocol.
    On approval → nurse is automatically notified to implement.
    """
    protocol = await db.get(Protocol, protocol_id)
    if not protocol:
        raise HTTPException(404, "Protocol not found")
    if protocol.status != "pending":
        raise HTTPException(400, f"Protocol already {protocol.status}")

    if body.action == "approved":
        updated = await approve_protocol(db, protocol_id, body.reviewed_by, body.notes)
        return {
            "status": "approved",
            "protocol_id": protocol_id,
            "nurse_notified": updated.nurse_notified,
            "message": "Protocol approved. Nurse has been notified to implement orders.",
        }

    # Modified or rejected — update status without nurse notification
    from datetime import datetime, timezone
    protocol.status = body.action
    protocol.reviewed_by = body.reviewed_by
    protocol.reviewed_at = datetime.now(timezone.utc)
    protocol.doctor_notes = body.notes
    await db.commit()
    return {"status": body.action, "protocol_id": protocol_id}


@router.get("/patient/{patient_id}")
async def patient_protocols(patient_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Protocol)
        .where(Protocol.patient_id == patient_id)
        .order_by(desc(Protocol.generated_at))
        .limit(10)
    )
    return result.scalars().all()   