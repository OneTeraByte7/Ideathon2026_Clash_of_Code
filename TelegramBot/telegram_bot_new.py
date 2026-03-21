from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes
import httpx
import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from telegram_service import BOT_TOKEN, NURSE_CHAT_ID, DOCTOR_CHAT_ID, send_doctor_decision_to_nurse

# Store for pending doctor decisions (in production use Redis/DB)
pending_protocols = {}


# 🔥 Handle doctor's button clicks (Approve/Reject/Modify)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    # Parse: approve_protocol_id_patient_id
    parts = data.split("_", 2)
    action = parts[0]  # approve, reject, modify
    protocol_id = parts[1] if len(parts) > 1 else None
    patient_id = parts[2] if len(parts) > 2 else None

    try:
        await query.answer()
    except Exception as e:
        print(f"⚠️ Callback answer error: {e}")

    if action == "approve":
        text = f"✅ **APPROVED** - Treatment protocol for patient approved.\n\nSending to nurse..."
        pending_protocols[protocol_id] = {"status": "approved", "notes": ""}
        
    elif action == "reject":
        text = f"❌ **REJECTED** - Protocol rejected.\n\nPlease send rejection reason with:\n/reject {protocol_id} <reason>"
        pending_protocols[protocol_id] = {"status": "rejected", "notes": ""}
        
    elif action == "modify":
        text = f"✏️ **MODIFY** - You are modifying the protocol.\n\nSend modifications with:\n/modify {protocol_id} <your modifications>"
        pending_protocols[protocol_id] = {"status": "modify", "notes": ""}
        
    else:
        text = "⚠️ Unknown action"

    try:
        await query.edit_message_text(text=text)
    except Exception as e:
        print(f"⚠️ Edit message error: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


# 📝 /reject command - Doctor rejects protocol
async def reject_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    parts = text.split(" ", 1)
    
    if len(parts) < 2:
        await update.message.reply_text("Usage: /reject <protocol_id> [reason]")
        return
    
    protocol_id = parts[0].replace("/reject", "").strip()
    reason = parts[1] if len(parts) > 1 else "No reason provided"
    
    # Update protocol via API
    await _update_protocol_via_api(protocol_id, "rejected", reason)
    
    reply = f"❌ Protocol {protocol_id} has been REJECTED.\n\nReason: {reason}\n\n✉️ Nurse has been notified."
    await update.message.reply_text(reply)


# ✏️ /modify command - Doctor modifies protocol
async def modify_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    parts = text.split(" ", 1)
    
    if len(parts) < 2:
        await update.message.reply_text("Usage: /modify <protocol_id> <modifications>")
        return
    
    protocol_id = parts[0].replace("/modify", "").strip()
    modifications = parts[1] if len(parts) > 1 else "No modifications"
    
    # Update protocol via API
    await _update_protocol_via_api(protocol_id, "modified", modifications)
    
    reply = f"✏️ Protocol {protocol_id} has been MODIFIED.\n\nChanges: {modifications}\n\n✉️ Nurse has been notified with updated protocol."
    await update.message.reply_text(reply)


# 👨‍⚕️ /status command - Check pending protocols
async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not pending_protocols:
        await update.message.reply_text("✅ No pending protocols.")
        return
    
    status_text = "📋 **Pending Protocols:**\n\n"
    for proto_id, info in pending_protocols.items():
        status_text += f"🔹 Protocol {proto_id}: {info['status']}\n"
    
    await update.message.reply_text(status_text)


# 🔗 Update protocol via backend API
async def _update_protocol_via_api(protocol_id: str, action: str, notes: str):
    """Call backend API to update protocol status."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"http://localhost:8000/protocols/{protocol_id}/review",
                json={
                    "action": action,
                    "reviewed_by": "Doctor (Telegram)",
                    "notes": notes
                },
                timeout=10
            )
            if response.status_code == 200:
                print(f"✅ Protocol {protocol_id} updated: {action}")
            else:
                print(f"⚠️ Failed to update protocol: {response.text}")
    except Exception as e:
        print(f"❌ API error: {e}")


# ❌ Error handler
async def error_handler(update, context):
    print(f"❌ Bot error: {context.error}")


# 🚀 Start bot
def start_bot():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not configured in .env")
        return
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler("reject", reject_handler))
    app.add_handler(CommandHandler("modify", modify_handler))
    app.add_handler(CommandHandler("status", status_handler))
    
    app.add_error_handler(error_handler)

    print("🤖 Telegram Bot Running...")
    print(f"📋 Nurse Chat: {NURSE_CHAT_ID}")
    print(f"👨‍⚕️ Doctor Chat: {DOCTOR_CHAT_ID}")
    app.run_polling()


if __name__ == "__main__":
    start_bot()
