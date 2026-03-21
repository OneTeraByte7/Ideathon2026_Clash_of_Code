"""
Scheduler — Asclepius AI
APScheduler background tasks:
  - Every 30s: monitor sweep (log worsening trends)
  - Every 5min: auto-resolve stale warning alerts
"""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from agents.monitor import analyze_patient_window
from services.alert_service import auto_resolve_stale_alerts
from models.patient import Patient

logger = logging.getLogger("asclepius.scheduler")

_scheduler: AsyncIOScheduler | None = None


async def _monitor_job():
    """Sweep all patients and check for worsening trends"""
    try:
        patients = await Patient.find_all().to_list()
        rising_count = 0
        for patient in patients:
            summary = await analyze_patient_window(patient.id)
            if summary and summary.get("trend") == "rising":
                rising_count += 1
        if rising_count > 0:
            logger.info(f"Monitor sweep: {rising_count} patient(s) on rising trend")
    except Exception as e:
        logger.error(f"Monitor job failed: {e}")


async def _auto_resolve_job():
    """Auto-resolve stale warning alerts"""
    try:
        count = await auto_resolve_stale_alerts()
        if count:
            logger.info(f"Auto-resolved {count} stale warning alert(s)")
    except Exception as e:
        logger.error(f"Auto-resolve job failed: {e}")


def start_scheduler():
    global _scheduler
    _scheduler = AsyncIOScheduler()

    _scheduler.add_job(
        _monitor_job,
        trigger=IntervalTrigger(seconds=30),
        id="monitor_sweep",
        name="ICU Monitor Sweep",
        replace_existing=True,
    )

    _scheduler.add_job(
        _auto_resolve_job,
        trigger=IntervalTrigger(minutes=5),
        id="auto_resolve",
        name="Auto-resolve Stale Alerts",
        replace_existing=True,
    )

    _scheduler.start()
    logger.info("✅ Background scheduler started (monitor every 30s, auto-resolve every 5min)")
    return _scheduler


def stop_scheduler():
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped.")