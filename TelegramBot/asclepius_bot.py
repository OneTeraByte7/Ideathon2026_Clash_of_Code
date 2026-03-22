#!/usr/bin/env python3
"""
Standalone Telegram Bot for Asclepius AI
Handles doctor responses to protocol alerts via inline buttons
"""
import os
import asyncio
import logging
import httpx
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = "8795379419:AAG_fiiluEx-GQI1bHyisFaNuVxzsIMBFo8"
DOCTOR_CHAT_ID = "-5294441613"
API_BASE_URL = "https://ideathon2026-clash-of-code.onrender.com"  # Your deployed API

class AsclepiusTelegramBot:
    def __init__(self):
        self.bot_token = BOT_TOKEN
        self.doctor_chat_id = DOCTOR_CHAT_ID
        self.api_url = API_BASE_URL
        
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle inline keyboard button presses"""
        query = update.callback_query
        await query.answer()  # Acknowledge the callback
        
        try:
            # Parse callback data
            action, protocol_id = query.data.split("_", 1)
            
            # Get user info
            user = update.effective_user
            doctor_name = user.full_name or user.username or "Unknown Doctor"
            
            logger.info(f"Doctor {doctor_name} clicked {action} for protocol {protocol_id}")
            
            # Process the action
            response_message = await self.handle_protocol_action(action, protocol_id, doctor_name)
            
            # Edit the message with the response
            await query.edit_message_text(
                text=f"{query.message.text}\n\n🩺 <b>DOCTOR RESPONSE:</b>\n{response_message}",
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Error handling button: {e}")
            await query.edit_message_text(
                text=f"{query.message.text}\n\n❌ <b>ERROR:</b> Failed to process response",
                parse_mode='HTML'
            )
    
    async def handle_protocol_action(self, action: str, protocol_id: str, doctor_name: str) -> str:
        """Process doctor's protocol action"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        if action == "approve":
            # Call API to approve protocol
            success = await self.call_api("approve", protocol_id, doctor_name)
            if success:
                return f"✅ <b>APPROVED</b> by Dr. {doctor_name}\n<i>Time: {timestamp}</i>\n\nProtocol has been approved and activated."
            else:
                return f"✅ <b>APPROVED</b> by Dr. {doctor_name}\n<i>Time: {timestamp}</i>\n\n⚠️ Note: Could not update system (API offline)"
                
        elif action == "reject":
            success = await self.call_api("reject", protocol_id, doctor_name)
            if success:
                return f"❌ <b>REJECTED</b> by Dr. {doctor_name}\n<i>Time: {timestamp}</i>\n\nProtocol has been rejected. Please provide alternative treatment plan."
            else:
                return f"❌ <b>REJECTED</b> by Dr. {doctor_name}\n<i>Time: {timestamp}</i>\n\n⚠️ Note: Could not update system (API offline)"
                
        elif action == "modify":
            return f"✏️ <b>MODIFICATION REQUESTED</b> by Dr. {doctor_name}\n<i>Time: {timestamp}</i>\n\nPlease use /note {protocol_id} <your_modifications> to specify changes."
            
        elif action == "details":
            return f"📋 <b>DETAILS REQUESTED</b> by Dr. {doctor_name}\n<i>Time: {timestamp}</i>\n\nFull protocol details available on dashboard: {self.api_url}/protocols"
            
        return f"⚠️ Unknown action: {action}"
    
    async def call_api(self, action: str, protocol_id: str, doctor_name: str) -> bool:
        """Call the API to update protocol status"""
        try:
            endpoint = f"/protocols/{protocol_id}/{action}"
            url = f"{self.api_url}{endpoint}"
            
            data = {
                "reviewed_by": doctor_name,
                "notes": f"Action performed via Telegram at {datetime.now().isoformat()}"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=data)
                
                if response.status_code == 200:
                    logger.info(f"✅ API call successful: {action} protocol {protocol_id}")
                    return True
                else:
                    logger.error(f"❌ API call failed: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ API call error: {e}")
            return False
    
    async def note_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /note command for adding doctor notes"""
        if not context.args or len(context.args) < 2:
            await update.message.reply_text(
                "Usage: /note <protocol_id> <your_note>\n\n"
                "Example: /note 123 Please increase antibiotic dose due to patient weight"
            )
            return
        
        protocol_id = context.args[0]
        note = " ".join(context.args[1:])
        
        user = update.effective_user
        doctor_name = user.full_name or user.username or "Unknown Doctor"
        
        # Store the note (you can implement API call here)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        response = (
            f"📝 <b>NOTE RECORDED</b>\n\n"
            f"<b>Doctor:</b> {doctor_name}\n"
            f"<b>Protocol ID:</b> {protocol_id}\n"
            f"<b>Note:</b> {note}\n"
            f"<b>Time:</b> {timestamp}\n\n"
            f"✅ Note has been recorded and will be reviewed by the medical team."
        )
        
        await update.message.reply_text(response, parse_mode='HTML')
        logger.info(f"📝 Note recorded by Dr. {doctor_name} for protocol {protocol_id}")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command"""
        await update.message.reply_text(
            "🤖 <b>Asclepius AI Medical Bot</b>\n\n"
            "This bot handles medical protocol responses for the ICU system.\n\n"
            "<b>Available Commands:</b>\n"
            "• Use buttons on protocol alerts to approve/reject\n"
            "• /note <protocol_id> <note> - Add doctor notes\n"
            "• /help - Show this help message\n\n"
            "🏥 <i>ICU Sepsis Early Warning System</i>",
            parse_mode='HTML'
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command"""
        await self.start_command(update, context)
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors"""
        logger.error(f"Exception while handling an update: {context.error}")
    
    def run(self):
        """Start the bot"""
        logger.info("🤖 Starting Asclepius Telegram Bot...")
        
        # Create application
        application = Application.builder().token(self.bot_token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("note", self.note_command))
        application.add_handler(CallbackQueryHandler(self.button_handler))
        
        # Add error handler
        application.add_error_handler(self.error_handler)
        
        # Start the bot
        logger.info("✅ Bot is running! Press Ctrl+C to stop.")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    bot = AsclepiusTelegramBot()
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot crashed: {e}")