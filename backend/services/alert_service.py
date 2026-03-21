"""
Alert Service — Asclepius AI
Query helpers for alert management.
Keeps business logic out of API routers.
"""
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func

from models.alert import Alert
from models.patient import Patient


async def get_active_alerts(db: AsyncSession, limit: int = 50) -> list[Alert]:
    result = await db.execute(
        select(Alert)
        .where(Alert.resolved == False)
        .order_by(desc(Alert.triggered_at))
        .limit(limit)
    )
    return result.scalars().all()


async def get_alerts_by_level(db: AsyncSession, level: str, limit: int = 20) -> list[Alert]:
    result = await db.execute(
        select(Alert)
        .where(Alert.level == level, Alert.resolved == False)
        .order_by(desc(Alert.triggered_at))
        .limit(limit)
    )
    return result.scalars().all()


async def get_alert_stats(db: AsyncSession) -> dict:
    total = (await db.execute(select(func.count(Alert.id)))).scalar()
    active = (await db.execute(
        select(func.count(Alert.id)).where(Alert.resolved == False)
    )).scalar()
    critical_active = (await db.execute(
        select(func.count(Alert.id)).where(Alert.level == "critical", Alert.resolved == False)
    )).scalar()
    warning_active = (await db.execute(
        select(func.count(Alert.id)).where(Alert.level == "warning", Alert.resolved == False)
    )).scalar()

    # Alerts in last hour
    since = datetime.now(timezone.utc) - timedelta(hours=1)
    last_hour = (await db.execute(
        select(func.count(Alert.id)).where(Alert.triggered_at >= since)
    )).scalar()

    return {
        "total_ever": total,
        "active": active,
        "critical_active": critical_active,
        "warning_active": warning_active,
        "fired_last_hour": last_hour,
    }


async def auto_resolve_stale_alerts(db: AsyncSession, stale_after_minutes: int = 120) -> int:
    """
    Auto-resolve warning alerts older than stale_after_minutes where
    patient's risk level has since returned to normal.
    Returns count of resolved alerts.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=stale_after_minutes)
    result = await db.execute(
        select(Alert)
        .where(
            Alert.resolved == False,
            Alert.level == "warning",
            Alert.triggered_at < cutoff,
        )
    )
    stale = result.scalars().all()
    count = 0
    for alert in stale:
        patient = await db.get(Patient, alert.patient_id)
        if patient and patient.risk_level == "normal":
            alert.resolved = True
            alert.resolved_at = datetime.now(timezone.utc)
            alert.resolved_by = "system_auto"
            count += 1
    if count:
        await db.commit()
    return count