"""
Vitals Service — Asclepius AI
Handles ingestion of a new vital reading:
1. Persist to DB
2. Compute risk score
3. Update patient risk level
4. Trigger alert + protocol if threshold crossed
"""
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import logging

from models.patient import Patient
from models.vital import Vital
from models.alert import Alert
from models.protocol import Protocol
from core.risk_engine import compute_risk, VitalReading
from core.notifier import notify_nurse, notify_doctor, notify_nurse_protocol_approved
from core.gemini_client import generate_sepsis_protocol
from config import get_settings

logger = logging.getLogger("asclepius.vitals_service")
settings = get_settings()


async def ingest_vital(db: AsyncSession, patient_id: int, data: dict, source: str = "monitor") -> Vital:
    """Core pipeline: receive vitals → score → alert if needed."""

    # 1. Fetch recent history for trend analysis (last 3 readings)
    history_rows = await db.execute(
        select(Vital)
        .where(Vital.patient_id == patient_id)
        .order_by(desc(Vital.recorded_at))
        .limit(3)
    )
    history_vitals = history_rows.scalars().all()
    history = [
        VitalReading(
            heart_rate=v.heart_rate,
            systolic_bp=v.systolic_bp,
            respiratory_rate=v.respiratory_rate,
            temperature=v.temperature,
            spo2=v.spo2,
            lactate=v.lactate,
        )
        for v in reversed(history_vitals)
    ]

    # 2. Compute risk
    current = VitalReading(**{k: data[k] for k in VitalReading.__dataclass_fields__})
    result = compute_risk(current, history)

    # 3. Persist vital
    vital = Vital(
        patient_id=patient_id,
        heart_rate=data["heart_rate"],
        systolic_bp=data["systolic_bp"],
        respiratory_rate=data["respiratory_rate"],
        temperature=data["temperature"],
        spo2=data["spo2"],
        lactate=data["lactate"],
        risk_score=result.risk_score,
        sofa_score=result.sofa_partial,
        qsofa_score=result.qsofa_score,
        source=source,
    )
    db.add(vital)
    await db.flush()

    # 4. Update patient risk
    patient = await db.get(Patient, patient_id)
    old_level = patient.risk_level
    patient.current_risk_score = result.risk_score
    patient.risk_level = result.risk_level
    patient.updated_at = datetime.now(timezone.utc)

    # 5. Trigger alert only if level changed or escalated
    if result.risk_level != "normal" and result.risk_level != old_level:
        await _trigger_alert(db, patient, vital, result)

    await db.commit()
    await db.refresh(vital)
    return vital


async def _trigger_alert(db: AsyncSession, patient: Patient, vital: Vital, result) -> None:
    alert = Alert(
        patient_id=patient.id,
        vital_id=vital.id,
        level=result.risk_level,
        risk_score=result.risk_score,
        message=f"Sepsis {result.risk_level}: score {result.risk_score}. Factors: {', '.join(result.contributing_factors[:3])}",
    )
    db.add(alert)
    await db.flush()

    # Notify nurse always (warning + critical)
    nurse_ok = await notify_nurse(
        patient_name=patient.name,
        bed=patient.bed_number,
        risk_score=result.risk_score,
        factors=result.contributing_factors,
        level=result.risk_level,
    )
    alert.nurse_notified = nurse_ok
    alert.nurse_notified_at = datetime.now(timezone.utc) if nurse_ok else None

    # Critical: generate protocol + notify doctor
    if result.risk_level == "critical":
        vitals_dict = {
            "heart_rate": vital.heart_rate,
            "systolic_bp": vital.systolic_bp,
            "respiratory_rate": vital.respiratory_rate,
            "temperature": vital.temperature,
            "spo2": vital.spo2,
            "lactate": vital.lactate,
        }
        patient_ctx = {
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
            "diagnosis": patient.diagnosis,
            "allergies": patient.allergies,
            "comorbidities": patient.comorbidities,
            "is_post_surgical": patient.is_post_surgical,
            "is_immunocompromised": patient.is_immunocompromised,
        }

        protocol_data = await generate_sepsis_protocol(
            patient_context=patient_ctx,
            risk_score=result.risk_score,
            vitals=vitals_dict,
            contributing_factors=result.contributing_factors,
        )

        protocol = Protocol(
            patient_id=patient.id,
            alert_id=alert.id,
            risk_score=result.risk_score,
            gemini_recommendation=protocol_data["full_recommendation"],
            antibiotic_suggestion=protocol_data["antibiotic_suggestion"],
            immediate_actions=protocol_data["immediate_actions"],
            rationale=protocol_data["rationale"],
            status="pending",
        )
        db.add(protocol)
        await db.flush()

        doctor_ok = await notify_doctor(
            patient_name=patient.name,
            bed=patient.bed_number,
            risk_score=result.risk_score,
            factors=result.contributing_factors,
            protocol_id=protocol.id,
        )
        alert.doctor_notified = doctor_ok
        alert.doctor_notified_at = datetime.now(timezone.utc) if doctor_ok else None


async def approve_protocol(db: AsyncSession, protocol_id: int, reviewed_by: str, notes: str) -> Protocol:
    """Doctor approves protocol → notify nurse to implement."""
    protocol = await db.get(Protocol, protocol_id)
    if not protocol:
        raise ValueError(f"Protocol {protocol_id} not found")

    protocol.status = "approved"
    protocol.reviewed_by = reviewed_by
    protocol.reviewed_at = datetime.now(timezone.utc)
    protocol.doctor_notes = notes

    patient = await db.get(Patient, protocol.patient_id)
    nurse_ok = await notify_nurse_protocol_approved(
        patient_name=patient.name,
        bed=patient.bed_number,
        protocol_id=protocol_id,
        doctor_notes=notes,
    )
    protocol.nurse_notified = nurse_ok
    protocol.nurse_notified_at = datetime.now(timezone.utc) if nurse_ok else None

    await db.commit()
    await db.refresh(protocol)
    return protocol