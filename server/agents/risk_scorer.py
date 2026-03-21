"""
Agent 2: Risk Scorer — Asclepius AI
Autonomous escalation logic:
  0–39   → Normal   → No action
  40–69  → Warning  → Notify nurse
  70–100 → Critical → Notify nurse + doctor, generate Gemini protocol

This agent wraps the risk engine and adds:
  - Patient-context adaptation (post-surgical, immunocompromised)
  - Consecutive-alert deduplication (don't re-alert same level)
  - Escalation tracking
"""
import logging
from datetime import datetime, timezone, timedelta

from models.alert import Alert
from models.patient import Patient
from core.risk_engine import compute_risk, VitalReading, RiskResult

logger = logging.getLogger("asclepius.risk_scorer")

# If patient already has an active alert at this level in last N minutes, skip re-alerting
DEDUP_WINDOW_MINUTES = 30


def adapt_score_for_context(result: RiskResult, patient: Patient) -> RiskResult:
    """
    Adjust risk score upward for high-risk patient contexts.
    Post-surgical: +5 (wound infection risk)
    Immunocompromised: +8 (attenuated fever response masks sepsis)
    """
    bonus = 0
    factors = list(result.contributing_factors)

    if patient.is_post_surgical:
        bonus += 5
        factors.append("Post-surgical patient (+5 risk adjustment)")

    if patient.is_immunocompromised:
        bonus += 8
        factors.append("Immunocompromised patient (+8 risk adjustment — attenuated response)")

    new_score = min(result.risk_score + bonus, 100.0)
    new_level = "critical" if new_score >= 70 else "warning" if new_score >= 40 else "normal"

    return RiskResult(
        risk_score=new_score,
        risk_level=new_level,
        qsofa_score=result.qsofa_score,
        sofa_partial=result.sofa_partial,
        contributing_factors=factors,
        trend_penalty=result.trend_penalty,
    )


async def should_suppress_alert(patient_id, level: str) -> bool:
    """
    Return True if an identical-level alert was fired in the last DEDUP_WINDOW_MINUTES.
    Prevents alert fatigue from repeated identical signals.
    """
    since = datetime.now(timezone.utc) - timedelta(minutes=DEDUP_WINDOW_MINUTES)
    existing = await Alert.find(
        Alert.patient_id == patient_id,
        Alert.level == level,
        Alert.resolved == False,
        Alert.triggered_at >= since,
    ).limit(1).to_list()
    
    if existing:
        logger.info(f"Suppressing duplicate {level} alert for patient {patient_id} (dedup window active)")
        return True
    return False


async def score_and_escalate(
    patient: Patient,
    current_vital: VitalReading,
    history: list[VitalReading],
) -> RiskResult:
    """
    Full scoring pipeline with context adaptation.
    Returns final adapted RiskResult.
    Does NOT write to DB — that's handled by vitals_service.
    """
    raw_result = compute_risk(current_vital, history)
    adapted = adapt_score_for_context(raw_result, patient)

    logger.info(
        f"Patient {patient.name} | Raw: {raw_result.risk_score} "
        f"→ Adapted: {adapted.risk_score} ({adapted.risk_level}) | "
        f"qSOFA={adapted.qsofa_score} | Factors: {adapted.contributing_factors[:2]}"
    )

    return adapted