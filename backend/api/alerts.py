from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from datetime import datetime, timezone

from db.database import get_db
from models.alert import Alert

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("/")
async def list_alerts(
    level: str | None = None,
    resolved: bool = False,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    query = select(Alert).where(Alert.resolved == resolved).order_by(desc(Alert.triggered_at)).limit(limit)
    if level:
        query = query.where(Alert.level == level)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/patient/{patient_id}")
async def patient_alerts(patient_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Alert)
        .where(Alert.patient_id == patient_id)
        .order_by(desc(Alert.triggered_at))
        .limit(20)
    )
    return result.scalars().all()


@router.patch("/{alert_id}/resolve")
async def resolve_alert(alert_id: int, resolved_by: str, db: AsyncSession = Depends(get_db)):
    alert = await db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(404, "Alert not found")
    alert.resolved = True
    alert.resolved_at = datetime.now(timezone.utc)
    alert.resolved_by = resolved_by
    await db.commit()
    return {"resolved": alert_id, "by": resolved_by}