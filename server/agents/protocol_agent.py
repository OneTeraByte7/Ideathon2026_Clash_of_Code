"""
Agent 3: Protocol Agent — Asclepius AI
Orchestrates the full clinical protocol generation pipeline:

  1. Fetch patient context (allergies, comorbidities, renal function proxy)
  2. Fetch latest vitals snapshot
  3. Call Gemini with RAG (Surviving Sepsis Campaign guidelines embedded)
  4. Persist protocol to DB with status=pending
  5. Doctor reviews → approves → nurse notified

Designed to run autonomously when risk_score crosses critical threshold (≥70).
"""
import logging
from datetime import datetime, timezone

from models.patient import Patient
from models.vital import Vital
from models.alert import Alert
from models.protocol import Protocol
from core.gemini_client import generate_sepsis_protocol

logger = logging.getLogger("asclepius.protocol_agent")


def _build_patient_context(patient: Patient) -> dict:
    return {
        "name": patient.name,
        "age": patient.age,
        "gender": patient.gender,
        "diagnosis": patient.diagnosis,
        "allergies": patient.allergies or "None known",
        "comorbidities": patient.comorbidities or "None",
        "is_post_surgical": patient.is_post_surgical,
        "is_immunocompromised": patient.is_immunocompromised,
    }


def _build_vitals_snapshot(vital: Vital) -> dict:
    return {
        "heart_rate": vital.heart_rate,
        "systolic_bp": vital.systolic_bp,
        "respiratory_rate": vital.respiratory_rate,
        "temperature": vital.temperature,
        "spo2": vital.spo2,
        "lactate": vital.lactate,
    }


async def generate_and_persist_protocol(
    patient: Patient,
    vital: Vital,
    alert: Alert,
    risk_score: float,
    contributing_factors: list[str],
) -> Protocol:
    """
    Main entry point: generate Gemini protocol and persist to DB.
    Called by vitals_service when a critical alert fires.
    """
    logger.info(f"Generating protocol for {patient.name} (score={risk_score})")

    patient_ctx = _build_patient_context(patient)
    vitals_snap = _build_vitals_snapshot(vital)

    # Call Gemini with RAG
    protocol_data = await generate_sepsis_protocol(
        patient_context=patient_ctx,
        risk_score=risk_score,
        vitals=vitals_snap,
        contributing_factors=contributing_factors,
    )

    protocol = Protocol(
        patient_id=patient.id,
        alert_id=alert.id,
        risk_score=risk_score,
        gemini_recommendation=protocol_data["full_recommendation"],
        antibiotic_suggestion=protocol_data["antibiotic_suggestion"],
        immediate_actions=protocol_data["immediate_actions"],
        rationale=protocol_data["rationale"],
        status="pending",
    )

    await protocol.insert()

    logger.info(f"Protocol #{protocol.id} generated for {patient.name} — awaiting doctor review")
    return protocol


async def get_pending_protocols_summary() -> dict:
    """Quick summary for dashboard widget."""
    from models.protocol import Protocol as ProtocolModel

    total = len(await ProtocolModel.find_all().to_list())
    pending = len(await ProtocolModel.find(ProtocolModel.status == "pending").to_list())
    approved = len(await ProtocolModel.find(ProtocolModel.status == "approved").to_list())

    return {
        "total_protocols": total,
        "pending_review": pending,
        "approved": approved,
        "requires_attention": pending > 0,
    }