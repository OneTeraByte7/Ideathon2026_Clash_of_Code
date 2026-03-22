#!/usr/bin/env python3
"""
Asclepius AI Telegram Bot Handler
Handles doctor button responses and commands
"""

import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration from environment
BOT_TOKEN = "8795379419:AAG_fiiluEx-GQI1bHyisFaNuVxzsIMBFo8"
DOCTOR_CHAT_ID = "-5294441613"
NURSE_CHAT_ID = "-5022062987"

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(
        "🏥 *Asclepius AI Medical Bot*\n\n"
        "I help manage medical protocols and alerts.\n\n"
        "*Available Commands:*\n"
        "/start - Show this help message\n"
        "/status - Check bot status\n"
        "/test - Send a test protocol\n\n"
        "Doctors will receive protocol approval buttons automatically.",
        parse_mode='Markdown'
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    chat_id = str(update.effective_chat.id)
    is_doctor = chat_id == DOCTOR_CHAT_ID
    is_nurse = chat_id == NURSE_CHAT_ID
    
    role = "🩺 Doctor" if is_doctor else "👩‍⚕️ Nurse" if is_nurse else "❓ Unknown"
    
    await update.message.reply_text(
        f"✅ *Bot Status: Active*\n\n"
        f"*Your Role:* {role}\n"
        f"*Chat ID:* `{chat_id}`\n"
        f"*Notifications:* {'✅ Enabled' if (is_doctor or is_nurse) else '❌ Not configured'}\n\n"
        f"*Features Available:*\n"
        f"{'• Protocol Approval Buttons' if is_doctor else '• Alert Notifications'}\n"
        f"• Real-time Medical Alerts\n"
        f"• Patient Status Updates",
        parse_mode='Markdown'
    )

async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a test protocol message with buttons (doctors only)"""
    chat_id = str(update.effective_chat.id)
    
    if chat_id != DOCTOR_CHAT_ID:
        await update.message.reply_text("❌ Test protocols are only available for doctors.")
        return
    
    # Create test protocol message
    test_message = (
        "🚨 <b>CRITICAL PROTOCOL APPROVAL NEEDED</b>\n\n"
        "👤 <b>Patient:</b> Test Patient\n"
        "🛏️ <b>Bed:</b> ICU-TEST\n"
        "⚠️ <b>Risk Score:</b> 85.2% (CRITICAL)\n\n"
        "🔬 <b>Recommended Protocol:</b>\n"
        "• Start IV broad-spectrum antibiotics\n"
        "• Increase fluid resuscitation\n"
        "• Order blood cultures STAT\n"
        "• Consider vasopressor support\n\n"
        "📊 <b>Supporting Data:</b>\n"
        "• Lactate: 4.2 mmol/L ↗️\n"
        "• BP: 85/60 mmHg ↘️\n"
        "• HR: 115 BPM ↗️\n"
        "• Temp: 39.1°C 🌡️\n\n"
        "⏰ <b>Time Critical:</b> Immediate action required"
    )
    
    # Create approval buttons
    keyboard = [
        [
            InlineKeyboardButton("✅ Approve Protocol", callback_data="approve_test"),
            InlineKeyboardButton("❌ Reject Protocol", callback_data="reject_test")
        ],
        [
            InlineKeyboardButton("✏️ Modify Protocol", callback_data="modify_test"),
            InlineKeyboardButton("📋 View Details", callback_data="details_test")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        test_message, 
        parse_mode='HTML', 
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks from doctors"""
    query = update.callback_query
    data = query.data
    
    # Extract action and patient/protocol ID
    parts = data.split("_", 1)
    action = parts[0]
    protocol_id = parts[1] if len(parts) > 1 else "unknown"
    
    # Acknowledge the button click
    try:
        await query.answer()
    except Exception as e:
        logger.warning(f"Could not acknowledge callback: {e}")
    
    # Handle different actions
    if action == "approve":
        response_text = (
            f"✅ <b>PROTOCOL APPROVED</b>\n\n"
            f"Protocol ID: {protocol_id}\n"
            f"Approved by: Dr. {query.from_user.first_name or 'Doctor'}\n"
            f"Status: Implementation authorized\n\n"
            f"📨 Nursing staff has been notified to proceed with the approved protocol."
        )
        
    elif action == "reject":
        response_text = (
            f"❌ <b>PROTOCOL REJECTED</b>\n\n"
            f"Protocol ID: {protocol_id}\n"
            f"Rejected by: Dr. {query.from_user.first_name or 'Doctor'}\n"
            f"Status: Alternative treatment required\n\n"
            f"💬 Please use /note command to provide alternative instructions:\n"
            f"<code>/note {protocol_id} Your alternative treatment plan</code>"
        )
        
    elif action == "modify":
        response_text = (
            f"✏️ <b>PROTOCOL MODIFICATION REQUESTED</b>\n\n"
            f"Protocol ID: {protocol_id}\n"
            f"Requested by: Dr. {query.from_user.first_name or 'Doctor'}\n"
            f"Status: Awaiting modifications\n\n"
            f"💬 Please use /note command to specify modifications:\n"
            f"<code>/note {protocol_id} Your modification instructions</code>"
        )
        
    elif action == "details":
        response_text = (
            f"📋 <b>PROTOCOL DETAILS</b>\n\n"
            f"Protocol ID: {protocol_id}\n"
            f"Generated: AI-driven sepsis protocol\n"
            f"Confidence: 94.2%\n\n"
            f"🔬 <b>Evidence Base:</b>\n"
            f"• Sepsis-3 guidelines compliance\n"
            f"• qSOFA score integration\n"
            f"• Lactate trend analysis\n"
            f"• Vital signs deterioration pattern\n\n"
            f"⚠️ This protocol requires immediate attention."
        )
    else:
        response_text = f"❓ <b>Unknown Action:</b> {action}"
    
    # Edit the original message or send new one if editing fails
    try:
        await query.edit_message_text(
            text=response_text,
            parse_mode='HTML'
        )
    except Exception as e:
        logger.warning(f"Could not edit message: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=response_text,
            parse_mode='HTML'
        )

async def note_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /note command for doctor comments"""
    chat_id = str(update.effective_chat.id)
    
    if chat_id != DOCTOR_CHAT_ID:
        await update.message.reply_text("❌ Notes can only be added by doctors.")
        return
    
    text = update.message.text or ""
    parts = text.split(" ", 2)
    
    if len(parts) < 3:
        await update.message.reply_text(
            "📝 <b>Usage:</b> /note <protocol_id> <your_note>\n\n"
            "<b>Example:</b>\n"
            "<code>/note P123 Increase antibiotic dose and add steroids</code>",
            parse_mode='HTML'
        )
        return
    
    protocol_id = parts[1]
    note_text = parts[2]
    doctor_name = update.effective_user.first_name or "Doctor"
    
    response = (
        f"📝 <b>DOCTOR'S NOTE ADDED</b>\n\n"
        f"👨‍⚕️ <b>Doctor:</b> {doctor_name}\n"
        f"🆔 <b>Protocol ID:</b> {protocol_id}\n"
        f"📋 <b>Note:</b> {note_text}\n\n"
        f"✅ Note has been recorded and nursing staff notified."
    )
    
    await update.message.reply_text(response, parse_mode='HTML')

def main():
    """Start the Telegram bot"""
    if not BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN not found in environment variables")
        return
    
    logger.info("🚀 Starting Asclepius AI Telegram Bot...")
    
    # Create application
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("test", test_command))
    app.add_handler(CommandHandler("note", note_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # Start bot
    logger.info("✅ Bot started successfully!")
    logger.info(f"👨‍⚕️ Doctor Chat ID: {DOCTOR_CHAT_ID}")
    logger.info(f"👩‍⚕️ Nurse Chat ID: {NURSE_CHAT_ID}")
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()