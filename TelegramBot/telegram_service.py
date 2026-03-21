import requests
import sys
from pathlib import Path

# Add backend to path so we can import config
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from config import get_settings

settings = get_settings()

# Get from .env - Telegram Bot Configuration
BOT_TOKEN = settings.telegram_bot_token
NURSE_CHAT_ID = settings.telegram_nurse_chat_id
DOCTOR_CHAT_ID = settings.telegram_doctor_chat_id


async def send_warning_alert_to_nurse(patient_name: str, patient_id: str, bed_number: str, 
                                       risk_score: float, factors: list):
    """Send warning alert ONLY to nurse (no approval buttons)."""
    message = f"""
🟡 **WARNING ALERT** - Sepsis Risk Detected

👤 Patient: {patient_name}
🛏️ Bed: {bed_number}
⚠️ Risk Score: {risk_score}/100
📊 Factors: {', '.join(factors[:3])}

🕐 Time: Now
👨‍⚕️ Action: Nurse review recommended

Stay vigilant! Monitor vitals closely.
    """.strip()
    
    await _send_telegram_message(NURSE_CHAT_ID, message)


async def send_critical_alert_to_nurse_and_doctor(patient_name: str, patient_id: str, 
                                                    bed_number: str, risk_score: float, 
                                                    factors: list, protocol_id: str):
    """Send critical alert to BOTH nurse and doctor with approval buttons for doctor."""
    
    # Message to Nurse
    nurse_message = f"""
🔴 **CRITICAL ALERT** - Sepsis Risk CRITICAL

👤 Patient: {patient_name}
🛏️ Bed: {bed_number}
🚨 Risk Score: {risk_score}/100
📊 Factors: {', '.join(factors[:3])}

⏰ Time: Now
🩺 Status: AI protocol generated - Awaiting doctor approval
👨‍⚕️ Action: Doctor reviewing treatment plan

Standby for doctor decision...
    """.strip()
    
    await _send_telegram_message(NURSE_CHAT_ID, nurse_message)
    
    # Message to Doctor with Action Buttons
    doctor_message = f"""
🔴 **CRITICAL ALERT** - Doctor Action Required

👤 Patient: {patient_name}
🛏️ Bed: {bed_number}
🚨 Risk Score: {risk_score}/100
📊 Risk Factors: {', '.join(factors)}

📋 AI-Generated Protocol:
Click button below to review full protocol

⚠️ You can:
✅ APPROVE - Execute AI protocol as-is
❌ REJECT - Request alternative approach
✏️ MODIFY - Adjust protocol and send to nurse
    """.strip()
    
    await _send_telegram_message_with_buttons(DOCTOR_CHAT_ID, doctor_message, patient_id, protocol_id)


async def _send_telegram_message(chat_id: str, message: str):
    """Send plain text message to Telegram."""
    if not chat_id or not BOT_TOKEN:
        print("⚠️ Telegram not configured (missing chat_id or bot_token)")
        return
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=data, timeout=5)
        if response.status_code == 200:
            print(f"✅ Message sent to chat {chat_id}")
        else:
            print(f"⚠️ Failed to send message: {response.text}")
    except Exception as e:
        print(f"❌ Telegram error: {e}")


async def _send_telegram_message_with_buttons(chat_id: str, message: str, patient_id: str, protocol_id: str):
    """Send message with approve/reject/modify buttons to doctor."""
    if not chat_id or not BOT_TOKEN:
        print("⚠️ Telegram not configured")
        return
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": [
                [
                    {"text": "✅ Approve", "callback_data": f"approve_{protocol_id}_{patient_id}"},
                    {"text": "❌ Reject", "callback_data": f"reject_{protocol_id}_{patient_id}"}
                ],
                [
                    {"text": "✏️ Modify", "callback_data": f"modify_{protocol_id}_{patient_id}"}
                ]
            ]
        }
    }
    
    try:
        response = requests.post(url, json=data, timeout=5)
        if response.status_code == 200:
            print(f"✅ Protocol sent to doctor chat {chat_id}")
        else:
            print(f"⚠️ Failed to send protocol: {response.text}")
    except Exception as e:
        print(f"❌ Telegram error: {e}")


async def send_doctor_decision_to_nurse(patient_name: str, bed_number: str, decision: str, notes: str = ""):
    """Send doctor's decision to nurse chat."""
    if decision == "approved":
        status = "✅ APPROVED"
        emoji = "✅"
    elif decision == "rejected":
        status = "❌ REJECTED"
        emoji = "❌"
    else:  # modified
        status = "✏️ MODIFIED"
        emoji = "✏️"
    
    message = f"""
{emoji} **Protocol {status}**

👤 Patient: {patient_name}
🛏️ Bed: {bed_number}

📝 Doctor Notes: {notes if notes else "No additional notes"}

👨‍⚕️ Action: Implement protocol as decided by doctor
    """.strip()
    
    await _send_telegram_message(NURSE_CHAT_ID, message)