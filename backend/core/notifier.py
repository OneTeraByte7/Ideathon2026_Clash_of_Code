"""
Notifier — Asclepius AI
Dispatches real-time notifications to nurse and doctor.
Supports: webhooks (Slack/Teams/custom), extensible to SMS.

Warning  → Nurse only
Critical → Nurse + Doctor
"""
import httpx
import logging
from datetime import datetime, timezone
from config import get_settings

logger = logging.getLogger("asclepius.notifier")
settings = get_settings()


def _build_nurse_payload(patient_name: str, bed: str, risk_score: float, factors: list, level: str) -> dict:
    emoji = "🟡" if level == "warning" else "🔴"
    return {
        "text": (
            f"{emoji} *Sepsis {level.upper()} — {patient_name} (Bed {bed})*\n"
            f"Risk Score: *{risk_score}/100*\n"
            f"Factors: {', '.join(factors[:3]) or 'See dashboard'}\n"
            f"Time: {datetime.now(timezone.utc).strftime('%H:%M UTC')}\n"
            f"Action: {'Monitor closely & prepare for escalation' if level == 'warning' else 'IMMEDIATE assessment required — Doctor notified'}"
        )
    }


def _build_doctor_payload(patient_name: str, bed: str, risk_score: float, factors: list, protocol_id: int) -> dict:
    return {
        "text": (
            f"🔴 *CRITICAL SEPSIS ALERT — {patient_name} (Bed {bed})*\n"
            f"Risk Score: *{risk_score}/100*\n"
            f"Factors: {', '.join(factors)}\n"
            f"AI Protocol ID #{protocol_id} ready for review.\n"
            f"⚡ Tap to review & approve medication protocol."
        )
    }


async def notify_nurse(
    patient_name: str,
    bed: str,
    risk_score: float,
    factors: list,
    level: str,
) -> bool:
    payload = _build_nurse_payload(patient_name, bed, risk_score, factors, level)
    return await _dispatch(settings.nurse_webhook_url, payload, "Nurse")


async def notify_doctor(
    patient_name: str,
    bed: str,
    risk_score: float,
    factors: list,
    protocol_id: int,
) -> bool:
    payload = _build_doctor_payload(patient_name, bed, risk_score, factors, protocol_id)
    return await _dispatch(settings.doctor_webhook_url, payload, "Doctor")


async def notify_nurse_protocol_approved(
    patient_name: str,
    bed: str,
    protocol_id: int,
    doctor_notes: str,
) -> bool:
    payload = {
        "text": (
            f"✅ *Protocol Approved — {patient_name} (Bed {bed})*\n"
            f"Protocol #{protocol_id} approved by doctor.\n"
            f"Notes: {doctor_notes or 'No additional notes'}\n"
            f"Please implement the medication orders now."
        )
    }
    return await _dispatch(settings.nurse_webhook_url, payload, "Nurse (protocol approved)")


async def _dispatch(url: str, payload: dict, recipient: str) -> bool:
    if not url:
        logger.warning(f"No webhook URL configured for {recipient}. Skipping notification.")
        logger.info(f"[SIMULATED] {recipient} notification: {payload['text'][:100]}...")
        return True  # Simulate success in dev

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.post(url, json=payload)
            r.raise_for_status()
            logger.info(f"✅ {recipient} notified via webhook.")
            return True
    except Exception as e:
        logger.error(f"❌ Failed to notify {recipient}: {e}")
        return False