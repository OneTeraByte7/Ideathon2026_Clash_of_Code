"""
Alert Service — Asclepius AI
Query helpers for alert management.
Keeps business logic out of API routers.
"""
from datetime import datetime, timezone, timedelta

from models.alert import Alert
from models.patient import Patient


async def get_active_alerts(limit: int = 50) -> list[Alert]:
    alerts = await Alert.find(Alert.resolved == False).sort([("triggered_at", -1)]).limit(limit).to_list()
    return alerts


async def get_alerts_by_level(level: str, limit: int = 20) -> list[Alert]:
    alerts = await Alert.find(Alert.level == level, Alert.resolved == False).sort([("triggered_at", -1)]).limit(limit).to_list()
    return alerts


async def get_alert_stats() -> dict:
    total = len(await Alert.find_all().to_list())
    active = len(await Alert.find(Alert.resolved == False).to_list())
    critical_active = len(await Alert.find(Alert.level == "critical", Alert.resolved == False).to_list())
    warning_active = len(await Alert.find(Alert.level == "warning", Alert.resolved == False).to_list())

    # Alerts in last hour
    since = datetime.now(timezone.utc) - timedelta(hours=1)
    last_hour = len(await Alert.find(Alert.triggered_at >= since).to_list())

    return {
        "total_ever": total,
        "active": active,
        "critical_active": critical_active,
        "warning_active": warning_active,
        "fired_last_hour": last_hour,
    }


async def auto_resolve_stale_alerts(stale_after_minutes: int = 120) -> int:
    """
    Auto-resolve warning alerts older than stale_after_minutes where
    patient's risk level has since returned to normal.
    Returns count of resolved alerts.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=stale_after_minutes)
    stale = await Alert.find(
        Alert.resolved == False,
        Alert.level == "warning",
        Alert.triggered_at < cutoff,
    ).to_list()
    
    count = 0
    for alert in stale:
        patient = await Patient.get(alert.patient_id)
        if patient and patient.risk_level == "normal":
            alert.resolved = True
            alert.resolved_at = datetime.now(timezone.utc)
            alert.resolved_by = "system_auto"
            await alert.save()
            count += 1
    return count