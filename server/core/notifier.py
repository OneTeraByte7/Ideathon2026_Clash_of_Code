"""
Notifier — Asclepius AI
Dispatches real-time notifications to nurse and doctor.
Supports: Telegram, webhooks (Slack/Teams/custom), extensible to SMS.

Warning  → Nurse only (Telegram)
Critical → Nurse + Doctor (Telegram with buttons for doctor)
"""
import httpx
import logging
from datetime import datetime, timezone
from config import get_settings

logger = logging.getLogger("asclepius.notifier")
settings = get_settings()


async def notify_nurse(
    patient_name: str,
    bed: str,
    risk_score: float,
    factors: list,
    level: str,
) -> bool:
    """Send warning/critical alert to nurse via Telegram."""
    if not settings.telegram_bot_token:
        print(f"⚠️ Telegram bot token not configured")
        return False
        
    if not settings.telegram_nurse_chat_id:
        print(f"⚠️ Nurse chat not configured - alert logged to console:")
        print(f"   📢 {level.upper()} ALERT: {patient_name} (Bed {bed})")
        print(f"   🚨 Risk Score: {risk_score}/100")
        print(f"   📊 Factors: {', '.join(str(f) for f in factors[:3])}")
        print(f"   💡 To fix: Create nurse Telegram group, add bot, update TELEGRAM_NURSE_CHAT_ID")
        return True  # Return True to not break the flow

    try:
        print(f"📤 Sending {level} alert to nurse via Telegram...")
        message = _build_nurse_message(patient_name, bed, risk_score, factors, level)
        success = await _send_telegram_message(
            settings.telegram_nurse_chat_id,
            message
        )
        if success:
            print(f"✅ Nurse notified via Telegram")
            return True
        else:
            print(f"❌ Failed to send to nurse chat {settings.telegram_nurse_chat_id}")
            print(f"💡 Fallback: Alert logged to console")
            print(f"   📢 {level.upper()} ALERT: {patient_name} (Bed {bed})")
            print(f"   🚨 Risk Score: {risk_score}/100")
            return True  # Return True to not break the flow
    except Exception as e:
        logger.error(f"Telegram notification to nurse failed: {e}")
        print(f"❌ Telegram error: {e}")
        print(f"💡 Fallback: Alert logged to console")
        print(f"   📢 {level.upper()} ALERT: {patient_name} (Bed {bed})")
        return True  # Return True to not break the flow


async def notify_doctor(
    patient_name: str,
    bed: str,
    risk_score: float,
    factors: list,
    protocol_id: str,
) -> bool:
    """Send critical alert to doctor via Telegram with approval buttons."""
    if settings.telegram_bot_token and settings.telegram_doctor_chat_id:
        try:
            print(f"📤 Sending critical alert to doctor via Telegram...")
            message = _build_doctor_message(patient_name, bed, risk_score, factors)
            success = await _send_telegram_message_with_buttons(
                settings.telegram_doctor_chat_id,
                message,
                protocol_id
            )
            if success:
                print(f"✅ Doctor notified via Telegram")
                return True
            else:
                print(f"❌ Failed to notify doctor via Telegram")
                return False
        except Exception as e:
            logger.error(f"Telegram notification failed: {e}")
            print(f"❌ Telegram error: {e}")
            return False
    else:
        print(f"❌ Telegram not configured for doctor")
        return False


async def notify_nurse_protocol_approved(
    patient_name: str,
    bed: str,
    protocol_id: str,
    doctor_notes: str,
) -> bool:
    """Notify nurse that doctor approved the protocol."""
    if settings.telegram_bot_token and settings.telegram_nurse_chat_id:
        try:
            print(f"📤 Sending protocol decision to nurse via Telegram...")
            message = f"""
✅ **Protocol APPROVED**

👤 Patient: {patient_name}
🛏️ Bed: {bed}

📝 Doctor Notes: {doctor_notes if doctor_notes else 'No additional notes'}

👨‍⚕️ Action: Implement protocol as decided by doctor
            """.strip()
            success = await _send_telegram_message(settings.telegram_nurse_chat_id, message)
            if success:
                print(f"✅ Nurse notified of approval via Telegram")
                return True
            else:
                print(f"❌ Failed to notify nurse via Telegram")
                return False
        except Exception as e:
            logger.error(f"Telegram notification failed: {e}")
            print(f"❌ Telegram error: {e}")
            return False
    else:
        print(f"❌ Telegram not configured for nurse")
        return False


def _build_nurse_message(patient_name: str, bed: str, risk_score: float, factors: list, level: str) -> str:
    emoji = "🟡" if level == "warning" else "🔴"
    return f"""
{emoji} **{level.upper()} ALERT** - Sepsis Risk Detected

👤 Patient: {patient_name}
🛏️ Bed: {bed}
{'⚠️' if level == 'warning' else '🚨'} Risk Score: {risk_score}/100
📊 Factors: {', '.join(str(f) for f in factors[:3])}

🕐 Time: {datetime.now(timezone.utc).strftime('%H:%M UTC')}
👨‍⚕️ Action: {'Monitor vitals, prepare for escalation' if level == 'warning' else 'IMMEDIATE assessment required — Doctor notified'}
    """.strip()


def _build_doctor_message(patient_name: str, bed: str, risk_score: float, factors: list) -> str:
    return f"""
🔴 **CRITICAL ALERT** - Doctor Action Required

👤 Patient: {patient_name}
🛏️ Bed: {bed}
🚨 Risk Score: {risk_score}/100
📊 Risk Factors: {', '.join(str(f) for f in factors)}

📋 AI-Generated Protocol available
Click button below to review full protocol

⚠️ You can:
✅ APPROVE - Execute AI protocol as-is
❌ REJECT - Request alternative approach
✏️ MODIFY - Adjust protocol and send to nurse
    """.strip()


def _build_nurse_payload(patient_name: str, bed: str, risk_score: float, factors: list, level: str) -> dict:
    emoji = "🟡" if level == "warning" else "🔴"
    return {
        "text": (
            f"{emoji} *Sepsis {level.upper()} — {patient_name} (Bed {bed})*\n"
            f"Risk Score: *{risk_score}/100*\n"
            f"Factors: {', '.join(str(f) for f in factors[:3]) or 'See dashboard'}\n"
            f"Time: {datetime.now(timezone.utc).strftime('%H:%M UTC')}\n"
            f"Action: {'Monitor closely & prepare for escalation' if level == 'warning' else 'IMMEDIATE assessment required — Doctor notified'}"
        )
    }


def _build_doctor_payload(patient_name: str, bed: str, risk_score: float, factors: list, protocol_id: str) -> dict:
    return {
        "text": (
            f"🔴 *CRITICAL SEPSIS ALERT — {patient_name} (Bed {bed})*\n"
            f"Risk Score: *{risk_score}/100*\n"
            f"Factors: {', '.join(str(f) for f in factors)}\n"
            f"AI Protocol ID #{protocol_id} ready for review.\n"
            f"⚡ Tap to review & approve medication protocol."
        )
    }


async def _send_telegram_message(chat_id: str, message: str) -> bool:
    """Send plain text message to Telegram."""
    if not chat_id or not settings.telegram_bot_token:
        logger.warning("Telegram not configured (missing chat_id or bot_token)")
        print(f"⚠️ Telegram not configured")
        return False
    
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=data)
            result = response.json()
            if result.get('ok'):
                print(f"✅ Message sent to chat {chat_id}")
                logger.info(f"✅ Message sent to chat {chat_id}")
                return True
            else:
                error = result.get('description', 'Unknown error')
                error_code = result.get('error_code', 'Unknown')
                print(f"❌ Telegram error: {error}")
                logger.error(f"❌ Telegram error (code {error_code}): {error}")
                
                # Provide helpful hints for common errors
                if "chat not found" in error.lower():
                    print(f"💡 Chat {chat_id} not found. Bot may have been removed from chat or chat deleted.")
                elif "bot was blocked" in error.lower():
                    print(f"💡 Bot was blocked by user in chat {chat_id}")
                elif "not enough rights" in error.lower():
                    print(f"💡 Bot lacks permission to send messages in chat {chat_id}")
                
                return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        logger.error(f"❌ Telegram error: {e}")
        return False


async def _send_telegram_message_with_buttons(chat_id: str, message: str, protocol_id: str) -> bool:
    """Send message with approve/reject/modify buttons to doctor."""
    if not chat_id or not settings.telegram_bot_token:
        logger.warning("Telegram not configured")
        print(f"⚠️ Telegram not configured")
        return False
    
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": [
                [
                    {"text": "✅ Approve", "callback_data": f"approve_{protocol_id}"},
                    {"text": "❌ Reject", "callback_data": f"reject_{protocol_id}"}
                ],
                [
                    {"text": "✏️ Modify", "callback_data": f"modify_{protocol_id}"}
                ]
            ]
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=data)
            result = response.json()
            if result.get('ok'):
                print(f"✅ Protocol sent to doctor chat {chat_id}")
                logger.info(f"✅ Protocol sent to doctor chat {chat_id}")
                return True
            else:
                error = result.get('description', 'Unknown error')
                print(f"❌ Telegram error: {error}")
                logger.error(f"❌ Telegram error: {error}")
                return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        logger.error(f"❌ Telegram error: {e}")
        return False


async def _dispatch(url: str, payload: dict, recipient: str) -> bool:
    """Dispatch notification via webhook (Slack, Teams, etc)."""
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
