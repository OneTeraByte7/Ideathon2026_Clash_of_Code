"""
Alert Throttling Configuration API
Allows configuring alert throttling parameters
"""
from fastapi import APIRouter
from pydantic import BaseModel
from services.telegram_service import telegram_service

router = APIRouter(prefix="/throttle", tags=["Throttle"])


class ThrottleConfig(BaseModel):
    interval_seconds: int = 15
    max_alerts_per_window: int = 1


@router.get("/config")
async def get_throttle_config():
    """Get current throttling configuration"""
    return {
        "interval_seconds": telegram_service.throttle_interval.seconds,
        "max_alerts_per_window": telegram_service.max_alerts_per_window,
        "active_throttles": len(telegram_service.alert_throttle),
        "description": f"Alerts are limited to {telegram_service.max_alerts_per_window} per {telegram_service.throttle_interval.seconds}s window per patient"
    }


@router.post("/config")
async def set_throttle_config(config: ThrottleConfig):
    """Configure alert throttling parameters"""
    telegram_service.configure_throttling(
        interval_seconds=config.interval_seconds,
        max_alerts_per_window=config.max_alerts_per_window
    )
    
    return {
        "status": "success",
        "message": f"Throttling configured: {config.interval_seconds}s interval, max {config.max_alerts_per_window} alerts per window",
        "config": {
            "interval_seconds": config.interval_seconds,
            "max_alerts_per_window": config.max_alerts_per_window
        }
    }


@router.delete("/throttles")
async def clear_throttles():
    """Clear all active throttles (emergency override)"""
    count = len(telegram_service.alert_throttle)
    telegram_service.alert_throttle.clear()
    
    return {
        "status": "success",
        "message": f"Cleared {count} active throttles",
        "cleared_count": count
    }


@router.get("/status/{patient_id}")
async def get_patient_throttle_status(patient_id: str):
    """Check throttle status for a specific patient"""
    critical_key = f"{patient_id}_critical"
    warning_key = f"{patient_id}_warning"
    
    status = {
        "patient_id": patient_id,
        "critical_alerts": {},
        "warning_alerts": {},
        "throttle_config": {
            "interval_seconds": telegram_service.throttle_interval.seconds,
            "max_alerts_per_window": telegram_service.max_alerts_per_window
        }
    }
    
    if critical_key in telegram_service.alert_throttle:
        data = telegram_service.alert_throttle[critical_key]
        from datetime import datetime
        time_remaining = (data["last_sent"] + telegram_service.throttle_interval - datetime.now()).total_seconds()
        status["critical_alerts"] = {
            "throttled": time_remaining > 0,
            "last_sent": data["last_sent"].isoformat(),
            "count_this_window": data["count"],
            "seconds_until_next_allowed": max(0, int(time_remaining))
        }
    else:
        status["critical_alerts"] = {
            "throttled": False,
            "message": "No previous alerts - next alert will be sent immediately"
        }
    
    if warning_key in telegram_service.alert_throttle:
        data = telegram_service.alert_throttle[warning_key]
        from datetime import datetime
        time_remaining = (data["last_sent"] + telegram_service.throttle_interval - datetime.now()).total_seconds()
        status["warning_alerts"] = {
            "throttled": time_remaining > 0,
            "last_sent": data["last_sent"].isoformat(),
            "count_this_window": data["count"],
            "seconds_until_next_allowed": max(0, int(time_remaining))
        }
    else:
        status["warning_alerts"] = {
            "throttled": False,
            "message": "No previous alerts - next alert will be sent immediately"
        }
    
    return status