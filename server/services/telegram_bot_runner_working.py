"""
Asclepius AI - Working Telegram Bot Runner 
Fixed all import and compatibility issues
"""
import asyncio
import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime
import httpx
from telegram import Bot, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

logger = logging.getLogger(__name__)

# Load settings from environment variables directly to avoid import issues
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
NURSE_CHAT_ID = os.getenv('TELEGRAM_NURSE_CHAT_ID')
DOCTOR_CHAT_ID = os.getenv('TELEGRAM_DOCTOR_CHAT_ID')

# Global storage for pending protocols
pending_protocols: Dict[str, Dict[str, Any]] = {}

class TelegramBotRunner:
    """Working Telegram bot runner - all issues fixed"""
    
    def __init__(self):
        self.app: Optional[Application] = None
        self.bot: Optional[Bot] = None
        self.running = False
        self._polling_task = None
        
    def is_configured(self):
        """Check if bot is properly configured"""
        configured = bool(BOT_TOKEN and (NURSE_CHAT_ID or DOCTOR_CHAT_ID))
        if not configured:
            logger.warning("❌ Telegram bot not configured - check environment variables:")
            logger.warning(f"   TELEGRAM_BOT_TOKEN: {'✅' if BOT_TOKEN else '❌'}")
            logger.warning(f"   TELEGRAM_NURSE_CHAT_ID: {'✅' if NURSE_CHAT_ID else '❌'}")
            logger.warning(f"   TELEGRAM_DOCTOR_CHAT_ID: {'✅' if DOCTOR_CHAT_ID else '❌'}")
        return configured
    
    async def start_bot(self):
        """Start the Telegram bot"""
        if not self.is_configured():
            logger.warning("🤖 Telegram bot not configured - check .env file")
            return False
            
        try:
            logger.info("🤖 Starting Telegram bot...")
            
            # Test bot token
            test_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
            async with httpx.AsyncClient(timeout=10.0) as client:
                test_response = await client.get(test_url)
                if test_response.status_code != 200:
                    logger.error(f"❌ Invalid bot token: {test_response.text}")
                    return False
                
                bot_info = test_response.json().get("result", {})
                logger.info(f"✅ Bot token valid: @{bot_info.get('username', 'Unknown')}")
            
            # Create bot and application
            self.bot = Bot(token=BOT_TOKEN)
            
            # Use Application.builder() for compatibility
            builder = Application.builder()
            builder.token(BOT_TOKEN)
            self.app = builder.build()
            
            # Add handlers
            self.app.add_handler(CallbackQueryHandler(self.button_handler))
            self.app.add_handler(CommandHandler("note", self.note_handler))
            self.app.add_handler(CommandHandler("start", self.start_handler))
            self.app.add_handler(CommandHandler("status", self.status_handler))
            self.app.add_error_handler(self.error_handler)
            
            # Initialize application
            await self.app.initialize()
            
            # Start manual polling
            self.running = True
            self._polling_task = asyncio.create_task(self._manual_polling())
            
            logger.info("✅ Telegram bot started successfully")
            logger.info(f"📱 Nurse Chat ID: {NURSE_CHAT_ID}")
            logger.info(f"👨‍⚕️ Doctor Chat ID: {DOCTOR_CHAT_ID}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start Telegram bot: {e}")
            self.running = False
            return False
    
    async def _manual_polling(self):
        """Manual polling to avoid Updater issues"""
        logger.info("🔄 Starting manual polling...")
        offset = 0
        consecutive_errors = 0
        
        while self.running:
            try:
                updates_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
                params = {
                    "offset": offset,
                    "timeout": 10,
                    "allowed_updates": ["message", "callback_query"]
                }
                
                async with httpx.AsyncClient(timeout=15.0) as client:
                    response = await client.get(updates_url, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("ok"):
                            updates = data.get("result", [])
                            
                            for update_data in updates:
                                try:
                                    update = Update.de_json(update_data, self.bot)
                                    if update:
                                        asyncio.create_task(self.app.process_update(update))
                                        offset = update.update_id + 1
                                except Exception as e:
                                    logger.error(f"Error processing update: {e}")
                                    
                            consecutive_errors = 0
                        else:
                            consecutive_errors += 1
                    else:
                        consecutive_errors += 1
                        
                if consecutive_errors >= 5:
                    logger.error("Too many consecutive errors, stopping")
                    break
                 
                await asyncio.sleep(1)
                 
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"❌ Polling error: {e}")
                if consecutive_errors >= 5:
                    break
                await asyncio.sleep(3)
                 
        self.running = False
    
    async def stop_bot(self):
        """Stop the Telegram bot"""
        if self.running:
            logger.info("🛑 Stopping Telegram bot...")
            self.running = False
            
            try:
                if self._polling_task:
                    self._polling_task.cancel()
                    await asyncio.sleep(1)
                 
                if self.app:
                    await self.app.shutdown()
                     
                logger.info("✅ Telegram bot stopped")
            except Exception as e:
                logger.error(f"❌ Error stopping bot: {e}")
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button clicks"""
        query = update.callback_query
        data = query.data
        
        logger.info(f"📱 Button clicked: '{data}'")
        
        try:
            await query.answer()
        except Exception:
            pass

        parts = data.split("_")
        if len(parts) < 3:
            await query.edit_message_text("⚠️ Invalid button format")
            return

        action, protocol_id, patient_id = parts[0], parts[1], parts[2]
        user = query.from_user
        doctor_name = user.full_name or user.username or f"Doctor_{user.id}"
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        if action == "approve":
            await query.edit_message_text(
                f"✅ <b>PROTOCOL APPROVED</b>\n\n"
                f"Patient: {patient_id}\nProtocol: {protocol_id}\n"
                f"Approved by: Dr. {doctor_name}\nTime: {timestamp}\n\n"
                f"✅ Implementation instructions sent to nurse",
                parse_mode="HTML"
            )
            await self._send_approved_protocol(patient_id, protocol_id, doctor_name)
            
        elif action == "reject":
            await query.edit_message_text(
                f"❌ <b>PROTOCOL REJECTED</b>\n\n"
                f"Patient: {patient_id}\nProtocol: {protocol_id}\n"
                f"Rejected by: Dr. {doctor_name}\nTime: {timestamp}\n\n"
                f"Use: /note {patient_id} your_instructions",
                parse_mode="HTML"
            )
            pending_protocols[patient_id] = {
                "action": "rejected", "protocol_id": protocol_id,
                "doctor_name": doctor_name, "timestamp": timestamp
            }
            await self._notify_nurse_rejected(patient_id, protocol_id, doctor_name)
            
        elif action == "modify":
            await query.edit_message_text(
                f"✏️ <b>PROTOCOL MODIFICATION REQUESTED</b>\n\n"
                f"Patient: {patient_id}\nProtocol: {protocol_id}\n"
                f"Requested by: Dr. {doctor_name}\nTime: {timestamp}\n\n"
                f"Use: /note {patient_id} your_modifications",
                parse_mode="HTML"
            )
            pending_protocols[patient_id] = {
                "action": "modify", "protocol_id": protocol_id,
                "doctor_name": doctor_name, "timestamp": timestamp
            }

    async def note_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /note command"""
        try:
            if len(context.args) < 2:
                await update.message.reply_text(
                    "Usage: /note <patient_id> <instructions>",
                    parse_mode="HTML"
                )
                return

            patient_id = context.args[0]
            instructions = " ".join(context.args[1:])
            user = update.effective_user
            doctor_name = user.full_name or user.username or f"Doctor_{user.id}"
            
            if patient_id in pending_protocols:
                info = pending_protocols[patient_id]
                if info["action"] == "rejected":
                    await self._send_alternative_instructions(patient_id, info["protocol_id"], instructions, doctor_name)
                elif info["action"] == "modify":
                    await self._send_modified_protocol(patient_id, info["protocol_id"], instructions, doctor_name)
                del pending_protocols[patient_id]
            else:
                await self._send_general_instructions(patient_id, instructions, doctor_name)

            await update.message.reply_text(
                f"✅ Instructions sent to nursing staff\nPatient: {patient_id}",
                parse_mode="HTML"
            )
            
        except Exception as e:
            logger.error(f"Error in note handler: {e}")
            await update.message.reply_text("❌ Error processing note.")

    async def start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        chat_id = str(update.effective_chat.id)
        role = "👨‍⚕️ Doctor" if chat_id == DOCTOR_CHAT_ID else "👩‍⚕️ Nurse" if chat_id == NURSE_CHAT_ID else "❓ Unknown"
        
        message = f"""🏥 <b>Asclepius AI - ICU Sepsis Early Warning System</b>

🤖 <b>Production Medical Alert Bot</b>

Role: {role}
Chat ID: <code>{chat_id}</code>

Commands:
• /note PAT001 instructions - Send medical instructions
• /status - Check system status

System Status: ✅ Production mode active"""

        await update.message.reply_text(message, parse_mode="HTML")

    async def status_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        pending_count = len(pending_protocols)
        
        status = f"""📊 <b>Bot Status Report</b>

Status: ✅ Online (Production Mode)
Pending Protocols: {pending_count}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

Configuration:
• Nurse Chat: {'✅' if NURSE_CHAT_ID else '❌'}
• Doctor Chat: {'✅' if DOCTOR_CHAT_ID else '❌'}"""
        
        await update.message.reply_text(status, parse_mode="HTML")

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle bot errors"""
        logger.error(f"Bot error: {context.error}")

    async def _send_approved_protocol(self, patient_id: str, protocol_id: str, doctor_name: str):
        """Send approved protocol to nurse"""
        if not NURSE_CHAT_ID:
            return
            
        message = f"""✅ <b>PROTOCOL APPROVED - IMPLEMENT NOW</b>

Patient: {patient_id}
Protocol: {protocol_id}
Approved by: Dr. {doctor_name}

🚨 SEPSIS PROTOCOL:
• Blood cultures (STAT)
• Broad-spectrum antibiotics within 1 hour
• IV fluids 30ml/kg within 3 hours
• Monitor vitals q15min
• Vasopressors if MAP < 65 mmHg

⚡ BEGIN IMPLEMENTATION IMMEDIATELY"""

        await self._send_message(NURSE_CHAT_ID, message)

    async def _notify_nurse_rejected(self, patient_id: str, protocol_id: str, doctor_name: str):
        """Notify nurse of rejection"""
        if not NURSE_CHAT_ID:
            return
            
        message = f"""❌ <b>PROTOCOL REJECTED - STANDBY</b>

Patient: {patient_id}
Protocol: {protocol_id}
Rejected by: Dr. {doctor_name}

⏳ DO NOT IMPLEMENT AI PROTOCOL
Wait for alternative instructions."""

        await self._send_message(NURSE_CHAT_ID, message)

    async def _send_alternative_instructions(self, patient_id: str, protocol_id: str, instructions: str, doctor_name: str):
        """Send alternative instructions"""
        if not NURSE_CHAT_ID:
            return
            
        message = f"""📝 <b>ALTERNATIVE TREATMENT ORDERS</b>

Patient: {patient_id}
Doctor: Dr. {doctor_name}

👨‍⚕️ ORDERS:
{instructions}

⚡ IMPLEMENT THESE ORDERS IMMEDIATELY"""

        await self._send_message(NURSE_CHAT_ID, message)

    async def _send_modified_protocol(self, patient_id: str, protocol_id: str, modifications: str, doctor_name: str):
        """Send modified protocol"""
        if not NURSE_CHAT_ID:
            return
            
        message = f"""✏️ <b>MODIFIED PROTOCOL</b>

Patient: {patient_id}
Modified by: Dr. {doctor_name}

Modifications:
{modifications}

⚡ IMPLEMENT MODIFIED PROTOCOL"""

        await self._send_message(NURSE_CHAT_ID, message)

    async def _send_general_instructions(self, patient_id: str, instructions: str, doctor_name: str):
        """Send general instructions"""
        if not NURSE_CHAT_ID:
            return
            
        message = f"""📋 <b>DOCTOR'S INSTRUCTIONS</b>

Patient: {patient_id}
Doctor: Dr. {doctor_name}

Instructions:
{instructions}"""

        await self._send_message(NURSE_CHAT_ID, message)

    async def _send_message(self, chat_id: str, message: str):
        """Send message to chat"""
        if not self.bot:
            return
            
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
            logger.info(f"✅ Message sent to {chat_id}")
        except Exception as e:
            logger.error(f"❌ Failed to send message: {e}")

# Global instance
telegram_bot_runner = TelegramBotRunner()