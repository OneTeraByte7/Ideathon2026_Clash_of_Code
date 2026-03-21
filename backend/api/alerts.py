from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone

from models.alert import Alert

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("/")
async def list_alerts(
    level: str | None = None,
    resolved: bool = False,
    limit: int = 50,
):
    query_filter = {"resolved": resolved}
    if level:
        query_filter["level"] = level
    
    alerts = await Alert.find(query_filter).sort("-triggered_at").limit(limit).to_list()
    return [alert.dict() for alert in alerts]


@router.get("/patient/{patient_id}")
async def patient_alerts(patient_id: str):
    from beanie import PydanticObjectId
    alerts = await Alert.find(Alert.patient_id == PydanticObjectId(patient_id)).sort("-triggered_at").limit(20).to_list()
    return [alert.dict() for alert in alerts]


@router.patch("/{alert_id}/resolve")
async def resolve_alert(alert_id: str, resolved_by: str):
    from beanie import PydanticObjectId
    alert = await Alert.get(PydanticObjectId(alert_id))
    if not alert:
        raise HTTPException(404, "Alert not found")
    alert.resolved = True
    alert.resolved_at = datetime.now(timezone.utc)
    alert.resolved_by = resolved_by
    await alert.save()
    return {"resolved": alert_id, "by": resolved_by}