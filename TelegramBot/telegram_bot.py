from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes
import httpx
import asyncio
import json
from pathlib import Path
import sys
import os

# Add server directory to path for imports
server_path = Path(__file__).parent.parent / "server"
sys.path.insert(0, str(server_path))

from config import get_settings

settings = get_settings()

BOT_TOKEN = settings.telegram_bot_token
NURSE_CHAT_ID = settings.telegram_nurse_chat_id
DOCTOR_CHAT_ID = settings.telegram_doctor_chat_id

# Store pending protocols and notes
pending_protocols = {}
protocol_notes = {}

# 🔥 Handle button clicks
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    # Parse callback data: action_protocol_id_patient_id
    parts = data.split("_")
    if len(parts) < 3:
        await query.answer("Invalid button data")
        return
        
    action = parts[0]
    protocol_id = parts[1] if len(parts) > 1 else "unknown"
    patient_id = parts[2] if len(parts) > 2 else "unknown"

    # safe answer, ignore old callback errors
    try:
        await query.answer()
    except Exception as e:
        print("⚠️ callback-answer err:", e)

    chat_id = str(update.effective_chat.id)
    
    if action == "approve":
        # Doctor approved protocol
        await query.edit_message_text(
            text=f"✅ <b>PROTOCOL APPROVED</b>\n\n"
                 f"Patient ID: {patient_id}\n"
                 f"Protocol: {protocol_id}\n\n"
                 f"✅ Sending AI recommendation to nurse...",
            parse_mode="HTML"
        )
        
        # Send AI recommendation to nurse
        await send_ai_recommendation_to_nurse(patient_id, protocol_id)

    elif action == "reject":
        # Doctor rejected protocol
        await query.edit_message_text(
            text=f"❌ <b>PROTOCOL REJECTED</b>\n\n"
                 f"Patient ID: {patient_id}\n"
                 f"Protocol: {protocol_id}\n\n"
                 f"Please add a note with:\n"
                 f"<code>/note {patient_id} your_note_here</code>",
            parse_mode="HTML"
        )
        
        # Store rejection for note handling
        pending_protocols[patient_id] = {
            "action": "rejected",
            "protocol_id": protocol_id,
            "timestamp": context.application.update_queue
        }
        
        # Notify nurse to wait
        await notify_nurse_to_wait(patient_id, protocol_id)

    elif action == "modify":
        # Doctor wants to modify protocol
        await query.edit_message_text(
            text=f"✏️ <b>PROTOCOL MODIFICATION REQUESTED</b>\n\n"
                 f"Patient ID: {patient_id}\n"
                 f"Protocol: {protocol_id}\n\n"
                 f"Please add modification notes with:\n"
                 f"<code>/note {patient_id} your_modifications_here</code>",
            parse_mode="HTML"
        )
        
        # Store modification request
        pending_protocols[patient_id] = {
            "action": "modify",
            "protocol_id": protocol_id,
            "timestamp": context.application.update_queue
        }

    else:
        await query.edit_message_text("⚠️ Unknown action")


# 📝 /note command for doctor notes
async def note_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    parts = text.split(" ", 2)

    if len(parts) < 3:
        await update.message.reply_text(
            "Usage: /note <patient_id> <your note>\n"
            "Example: /note PAT001 Increase monitoring frequency",
            parse_mode="HTML"
        )
        return

    patient_id, note = parts[1], parts[2]
    
    # Check if there's a pending protocol for this patient
    if patient_id in pending_protocols:
        protocol_info = pending_protocols[patient_id]
        action = protocol_info["action"]
        protocol_id = protocol_info["protocol_id"]
        
        # Store the note
        protocol_notes[patient_id] = note
        
        if action == "rejected":
            # Send rejection notice with note to nurse
            await send_rejection_note_to_nurse(patient_id, protocol_id, note)
            reply = f"📝 <b>Rejection note sent to nurse</b>\n\n" \
                   f"Patient: {patient_id}\n" \
                   f"Note: {note}"
                   
        elif action == "modify":
            # Send modification note to nurse
            await send_modification_to_nurse(patient_id, protocol_id, note)
            reply = f"📝 <b>Modification sent to nurse</b>\n\n" \
                   f"Patient: {patient_id}\n" \
                   f"Modifications: {note}"
        
        # Clean up
        del pending_protocols[patient_id]
    else:
        # General note
        reply = f"📝 <b>General note recorded</b>\n\n" \
               f"Patient: {patient_id}\n" \
               f"Note: {note}"
        
        # Send to nurse as well
        await send_general_note_to_nurse(patient_id, note)

    await update.message.reply_text(reply, parse_mode="HTML")


async def send_ai_recommendation_to_nurse(patient_id: str, protocol_id: str):
    """Send AI protocol recommendation to nurse after doctor approval"""
    message = f"""✅ <b>AI PROTOCOL APPROVED</b>

<b>Patient ID:</b> {patient_id}
<b>Protocol:</b> {protocol_id}

🤖 <b>AI RECOMMENDATION:</b>
• Immediate blood cultures
• Start empirical antibiotics (Vancomycin + Piperacillin-Tazobactam)
• Fluid resuscitation 30ml/kg crystalloid
• Vasopressor support if needed
• Monitor lactate and vital signs q1h
• Reassess in 30 minutes

✅ <b>Doctor has approved this protocol</b>
Please implement immediately.

🏥 Asclepius AI System"""

    await send_telegram_message(NURSE_CHAT_ID, message)


async def notify_nurse_to_wait(patient_id: str, protocol_id: str):
    """Notify nurse that protocol was rejected and to wait for doctor's note"""
    message = f"""❌ <b>PROTOCOL REJECTED</b>

<b>Patient ID:</b> {patient_id}
<b>Protocol:</b> {protocol_id}

⏳ <b>Please wait for doctor's alternative instructions</b>

Doctor is preparing alternative treatment plan.
You will receive updated instructions shortly.

🏥 Asclepius AI System"""

    await send_telegram_message(NURSE_CHAT_ID, message)


async def send_rejection_note_to_nurse(patient_id: str, protocol_id: str, note: str):
    """Send doctor's rejection note with alternative instructions to nurse"""
    message = f"""📝 <b>DOCTOR'S ALTERNATIVE INSTRUCTIONS</b>

<b>Patient ID:</b> {patient_id}
<b>Rejected Protocol:</b> {protocol_id}

👨‍⚕️ <b>Doctor's Instructions:</b>
{note}

Please follow these alternative instructions instead of the AI protocol.

🏥 Asclepius AI System"""

    await send_telegram_message(NURSE_CHAT_ID, message)


async def send_modification_to_nurse(patient_id: str, protocol_id: str, modifications: str):
    """Send doctor's protocol modifications to nurse"""
    message = f"""✏️ <b>MODIFIED PROTOCOL</b>

<b>Patient ID:</b> {patient_id}
<b>Protocol:</b> {protocol_id}

🤖 <b>Original AI Recommendation:</b>
• Blood cultures + empirical antibiotics
• Fluid resuscitation
• Vasopressor support if needed

👨‍⚕️ <b>Doctor's Modifications:</b>
{modifications}

Please implement the modified protocol.

🏥 Asclepius AI System"""

    await send_telegram_message(NURSE_CHAT_ID, message)


async def send_general_note_to_nurse(patient_id: str, note: str):
    """Send general doctor note to nurse"""
    message = f"""📋 <b>DOCTOR'S NOTE</b>

<b>Patient ID:</b> {patient_id}

👨‍⚕️ <b>Note:</b>
{note}

🏥 Asclepius AI System"""

    await send_telegram_message(NURSE_CHAT_ID, message)


async def send_telegram_message(chat_id: str, message: str):
    """Send message to Telegram chat"""
    if not BOT_TOKEN or not chat_id:
        print("⚠️ Telegram not configured")
        return
        
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(url, json=data)
            if response.status_code == 200:
                print(f"✅ Message sent to {chat_id}")
            else:
                print(f"❌ Failed to send: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")


# Command to send warning alert (for testing)
async def warning_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send warning alert to nurse only"""
    message = f"""⚠️ <b>WARNING ALERT</b>

Patient monitoring shows elevated sepsis risk.
Please review vitals and increase monitoring frequency.

Sent by: Dr. {update.effective_user.first_name or 'Doctor'}
Time: {update.message.date}

🏥 Asclepius AI System"""

    await send_telegram_message(NURSE_CHAT_ID, message)
    await update.message.reply_text("⚠️ Warning alert sent to nurse", parse_mode="HTML")


# � Error reporting
async def error_handler(update, context):
    print("❌ Bot error:", context.error)


# 🚀 Start bot
def start_bot():
    if not BOT_TOKEN:
        print("❌ No Telegram bot token configured!")
        return
        
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler("note", note_handler))
    app.add_handler(CommandHandler("warning", warning_handler))
    
    app.add_error_handler(error_handler)

    print("🤖 Telegram Bot Running...")
    print(f"📱 Nurse Chat ID: {NURSE_CHAT_ID}")
    print(f"👨‍⚕️ Doctor Chat ID: {DOCTOR_CHAT_ID}")
    app.run_polling()


if __name__ == "__main__":
    start_bot()