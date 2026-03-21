"""
Agent 1: Continuous Monitor — Asclepius AI
Runs on a schedule (every 30 seconds in prod, configurable).
For each patient, pulls the latest vitals window and feeds
them to the risk scorer.

In the hackathon demo this is triggered by:
  - Manual POST /patients/{id}/vitals
  - Seed endpoints (🔵🟡🔴)
  - This scheduler (when running in background mode)
"""
import logging
from datetime import datetime, timezone, timedelta
from beanie import PydanticObjectId

from models.patient import Patient
from models.vital import Vital
from core.risk_engine import compute_risk, VitalReading

logger = logging.getLogger("asclepius.monitor")


async def analyze_patient_window(patient_id, window_minutes: int = 240) -> dict | None:
    """
    Pull last `window_minutes` of vitals for a patient.
    Returns a trend summary used by the risk scorer.
    """
    since = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)

    vitals = await Vital.find(
        Vital.patient_id == patient_id,
        Vital.recorded_at >= since
    ).sort([("recorded_at", 1)]).to_list()

    if not vitals:
        return None

    readings = [
        VitalReading(
            heart_rate=v.heart_rate,
            systolic_bp=v.systolic_bp,
            respiratory_rate=v.respiratory_rate,
            temperature=v.temperature,
            spo2=v.spo2,
            lactate=v.lactate,
        )
        for v in vitals
    ]

    # Score each reading in context of what came before it
    scored = []
    for i, reading in enumerate(readings):
        history = readings[:i]
        result = compute_risk(reading, history)
        scored.append({
            "timestamp": vitals[i].recorded_at.isoformat(),
            "risk_score": result.risk_score,
            "risk_level": result.risk_level,
            "qsofa": result.qsofa_score,
            "trend_penalty": result.trend_penalty,
        })

    # Trend direction: is score going up?
    first_score = scored[0]["risk_score"] if scored else 0
    last_score = scored[-1]["risk_score"] if scored else 0
    trend = "rising" if last_score > first_score + 5 else "falling" if last_score < first_score - 5 else "stable"

    return {
        "patient_id": str(patient_id),
        "window_minutes": window_minutes,
        "reading_count": len(vitals),
        "trend": trend,
        "score_start": first_score,
        "score_latest": last_score,
        "scored_readings": scored,
    }


async def run_monitor_sweep() -> list[dict]:
    """
    Sweep all patients: analyze their window and log anomalies.
    Called by APScheduler every 30 seconds.
    """
    patients = await Patient.find_all().to_list()

    summaries = []
    for patient in patients:
        summary = await analyze_patient_window(patient.id)
        if summary:
            if summary["trend"] == "rising" and summary["score_latest"] > 30:
                logger.warning(
                    f"⚠️  Patient {patient.name} (Bed {patient.bed_number}): "
                    f"score rising {summary['score_start']} → {summary['score_latest']}"
                )
            summaries.append(summary)

    return summaries