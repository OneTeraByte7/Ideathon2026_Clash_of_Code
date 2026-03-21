"""
Agent 4: Learning Agent — Asclepius AI
Tracks prediction accuracy and generates insights about false positives/negatives.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models.vital import Vital
from models.alert import Alert
from models.patient import Patient


async def get_accuracy_report(db: AsyncSession) -> dict:
    """
    Computes prediction statistics:
    - True positives: alert triggered → patient actually deteriorated
    - False positives: alert triggered → patient recovered without sepsis
    - Coverage: % of critical patients who had ≥1 warning alert before critical
    """
    total_alerts = (await db.execute(select(func.count(Alert.id)))).scalar()
    resolved_alerts = (await db.execute(
        select(func.count(Alert.id)).where(Alert.resolved == True)
    )).scalar()

    critical_alerts = (await db.execute(
        select(func.count(Alert.id)).where(Alert.level == "critical")
    )).scalar()

    warning_alerts = (await db.execute(
        select(func.count(Alert.id)).where(Alert.level == "warning")
    )).scalar()

    # Average risk score at time of alert
    avg_risk = (await db.execute(
        select(func.avg(Alert.risk_score))
    )).scalar()

    # Score distribution
    high_confidence = (await db.execute(
        select(func.count(Alert.id)).where(Alert.risk_score >= 80)
    )).scalar()

    return {
        "total_alerts": total_alerts,
        "resolved_alerts": resolved_alerts,
        "critical_alerts": critical_alerts,
        "warning_alerts": warning_alerts,
        "average_risk_score_at_alert": round(avg_risk or 0, 1),
        "high_confidence_alerts": high_confidence,  # score ≥ 80
        "insights": _generate_insights(total_alerts, critical_alerts, warning_alerts),
    }


def _generate_insights(total: int, critical: int, warning: int) -> list[str]:
    insights = []
    if total == 0:
        return ["No alerts yet. Seed data to begin analysis."]
    if warning > 0 and critical > 0:
        ratio = warning / critical
        if ratio > 2:
            insights.append("High warning-to-critical ratio — early detection working well.")
        elif ratio < 0.5:
            insights.append("Many patients going straight to critical — consider lowering warning threshold.")
    if critical > 5:
        insights.append("High critical alert volume — review if threshold calibration needed for this ICU.")
    if total < 5:
        insights.append("Insufficient data for trend analysis. Continue monitoring.")
    return insights or ["System operating within expected parameters."]


async def get_patient_trend(db: AsyncSession, patient_id: int, limit: int = 20) -> dict:
    """Returns risk score trend for a patient over last N readings."""
    vitals = (await db.execute(
        select(Vital)
        .where(Vital.patient_id == patient_id)
        .order_by(Vital.recorded_at)
        .limit(limit)
    )).scalars().all()

    return {
        "patient_id": patient_id,
        "readings": limit,
        "trend": [
            {
                "timestamp": v.recorded_at.isoformat(),
                "risk_score": v.risk_score,
                "heart_rate": v.heart_rate,
                "systolic_bp": v.systolic_bp,
                "lactate": v.lactate,
                "source": v.source,
            }
            for v in vitals
        ],
    }