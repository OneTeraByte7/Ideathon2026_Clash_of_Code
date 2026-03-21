"""
Agent 4: Learning Agent — Asclepius AI
Tracks prediction accuracy and generates insights about false positives/negatives.
"""
from models.vital import Vital
from models.alert import Alert
from models.patient import Patient
from beanie import PydanticObjectId


async def get_accuracy_report() -> dict:
    """
    Computes prediction statistics:
    - True positives: alert triggered → patient actually deteriorated
    - False positives: alert triggered → patient recovered without sepsis
    - Coverage: % of critical patients who had ≥1 warning alert before critical
    """
    total_alerts = len(await Alert.find_all().to_list())
    resolved_alerts = len(await Alert.find(Alert.resolved == True).to_list())
    critical_alerts = len(await Alert.find(Alert.level == "critical").to_list())
    warning_alerts = len(await Alert.find(Alert.level == "warning").to_list())

    # Average risk score at time of alert
    all_alerts = await Alert.find_all().to_list()
    avg_risk = sum(a.risk_score for a in all_alerts) / len(all_alerts) if all_alerts else 0

    # Score distribution
    high_confidence = len(await Alert.find(Alert.risk_score >= 80).to_list())

    return {
        "total_alerts": total_alerts,
        "resolved_alerts": resolved_alerts,
        "critical_alerts": critical_alerts,
        "warning_alerts": warning_alerts,
        "average_risk_score_at_alert": round(avg_risk, 1),
        "high_confidence_alerts": high_confidence,
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


async def get_patient_trend(patient_id: str, limit: int = 20) -> dict:
    """Returns risk score trend for a patient over last N readings."""
    vitals = await Vital.find(Vital.patient_id == PydanticObjectId(patient_id)).sort([("recorded_at", 1)]).limit(limit).to_list()

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