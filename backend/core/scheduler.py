"""
Scheduler — Asclepius AI
APScheduler background tasks:
  - Every 30s: monitor sweep (log worsening trends)
  - Every 5min: auto-resolve stale warning alerts
"""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from db.database import AsyncSessionLocal
from agents.monitor import run_monitor_sweep
from services.alert_service import auto_resolve_stale_alerts

logger = logging.getLogger("asclepius.scheduler")

_scheduler: AsyncIOScheduler | None = None


async def _monitor_job():
    async with AsyncSessionLocal() as db:
        summaries = await run_monitor_sweep(db)
        if summaries:
            rising = [s for s in summaries if s["trend"] == "rising"]
            if rising:
                logger.info(f"Monitor sweep: {len(rising)} patient(s) on rising trend")


async def _auto_resolve_job():
    async with AsyncSessionLocal() as db:
        count = await auto_resolve_stale_alerts(db)
        if count:
            logger.info(f"Auto-resolved {count} stale warning alert(s)")


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