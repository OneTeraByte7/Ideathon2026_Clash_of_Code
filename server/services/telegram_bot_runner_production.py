"""
Asclepius AI - Production Telegram Bot Runner
Handles bot lifecycle and medical protocol interactions in production environment
"""
import asyncio
import logging
from typing import Dict, Any, Optional
import httpx
from telegram import Bot, Update
from telegram.ext import Application, ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes
from datetime import datetime

logger = logging.getLogger(__name__)

# Import settings
from config import get_settings
settings = get_settings()

BOT_TOKEN = settings.telegram_bot_token
NURSE_CHAT_ID = settings.telegram_nurse_chat_id  
DOCTOR_CHAT_ID = settings.telegram_doctor_chat_id

# Global storage for pending protocols (use Redis/Database in production)
pending_protocols: Dict[str, Dict[str, Any]] = {}

class TelegramBotRunner:
    """Production Telegram bot runner for Asclepius AI medical system"""
    
    def __init__(self):
        self.app: Optional[Application] = None
        self.bot: Optional[Bot] = None
        self.running = False
        self._polling_task = None
        
    def is_configured(self):
        """Check if bot is properly configured"""
        return bool(BOT_TOKEN and (NURSE_CHAT_ID or DOCTOR_CHAT_ID))
    
    async def start_bot(self):
        """Start the Telegram bot for production use"""
        if not self.is_configured():
            logger.warning("🤖 Telegram bot not configured - skipping bot startup")
            return False
            
        try:
            logger.info("🤖 Starting Asclepius AI Production Telegram Bot...")
            
            # Validate bot token
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
            self.app = ApplicationBuilder().token(BOT_TOKEN).build()
            
            # Add production handlers
            self.app.add_handler(CallbackQueryHandler(self.button_handler))
            self.app.add_handler(CommandHandler("note", self.note_handler))
            self.app.add_handler(CommandHandler("start", self.start_handler))
            self.app.add_handler(CommandHandler("status", self.status_handler))
            self.app.add_error_handler(self.error_handler)
            
            # Initialize and start application
            await self.app.initialize()
            await self.app.start()
            
            # Start polling
            self.running = True
            self._polling_task = asyncio.create_task(self._production_polling())
            
            logger.info("✅ Production Telegram bot started successfully")
            logger.info(f"📱 Nurse Chat ID: {NURSE_CHAT_ID}")
            logger.info(f"👨‍⚕️ Doctor Chat ID: {DOCTOR_CHAT_ID}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start Telegram bot: {e}")
            self.running = False
            return False
    
    async def _production_polling(self):
        """Production-grade polling implementation"""
        logger.info("🔄 Starting production Telegram polling...")
        offset = 0
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while self.running:
            try:
                # Get updates via Telegram API
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
                                    # Process each update
                                    update = Update.de_json(update_data, self.bot)
                                    if update:
                                        await self.app.process_update(update)
                                        offset = update.update_id + 1
                                except Exception as e:
                                    logger.error(f"Error processing update: {e}")
                                    
                            consecutive_errors = 0  # Reset on success
                        else:
                            logger.error(f"Telegram API error: {data}")
                            consecutive_errors += 1
                    else:
                        logger.error(f"HTTP error getting updates: {response.status_code}")
                        consecutive_errors += 1
                        
                # Stop if too many consecutive errors
                if consecutive_errors >= max_consecutive_errors:
                    logger.error("Too many consecutive errors, stopping polling")
                    break
                 
                await asyncio.sleep(1)  # Brief pause between polls
                 
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"❌ Polling error: {e}")
                if consecutive_errors >= max_consecutive_errors:
                    logger.error("Too many consecutive polling errors, stopping")
                    break
                await asyncio.sleep(5)  # Longer pause on error
                 
        logger.info("🛑 Production polling stopped")
        self.running = False
    
    async def stop_bot(self):
        """Stop the Telegram bot"""
        if self.running:
            logger.info("🛑 Stopping Telegram bot...")
            self.running = False
            
            try:
                if self._polling_task:
                    self._polling_task.cancel()
                    try:
                        await self._polling_task
                    except asyncio.CancelledError:
                        pass
                 
                if self.app:
                    await self.app.stop()
                    await self.app.shutdown()
                     
                logger.info("✅ Telegram bot stopped")
            except Exception as e:
                logger.error(f"❌ Error stopping Telegram bot: {e}")
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle doctor protocol approval/rejection buttons"""
        query = update.callback_query
        data = query.data
        
        logger.info(f"📱 Button clicked: '{data}' from chat {update.effective_chat.id}")
        
        try:
            await query.answer()
        except Exception as e:
            logger.warning(f"Callback answer error: {e}")

        # Parse callback data: action_protocol_id_patient_id
        parts = data.split("_")
        if len(parts) < 3:
            await query.edit_message_text("⚠️ Invalid button format")
            return

        action = parts[0]
        protocol_id = parts[1]
        patient_id = parts[2]
        
        # Get doctor info
        user = query.from_user
        doctor_name = user.full_name or user.username or f"Doctor_{user.id}"
        
        logger.info(f"🔍 Processing: {action} protocol {protocol_id} for patient {patient_id} by {doctor_name}")
        
        if action == "approve":
            await self._handle_approve(query, protocol_id, patient_id, doctor_name)
        elif action == "reject":
            await self._handle_reject(query, protocol_id, patient_id, doctor_name)
        elif action == "modify":
            await self._handle_modify(query, protocol_id, patient_id, doctor_name)
        else:
            await query.edit_message_text(f"⚠️ Unknown action: {action}")
    
    async def _handle_approve(self, query, protocol_id: str, patient_id: str, doctor_name: str):
        """Handle protocol approval"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        logger.info(f"✅ Protocol {protocol_id} approved by {doctor_name} for patient {patient_id}")
        
        await query.edit_message_text(
            text=f"✅ <b>PROTOCOL APPROVED</b>\n\n"
                 f"<b>Patient ID:</b> {patient_id}\n"
                 f"<b>Protocol:</b> {protocol_id}\n"
                 f"<b>Approved by:</b> Dr. {doctor_name}\n"
                 f"<b>Time:</b> {timestamp}\n\n"
                 f"✅ <b>Sending implementation instructions to nursing staff...</b>",
            parse_mode="HTML"
        )
        
        # Send implementation protocol to nurse
        await self._send_approved_protocol_to_nurse(patient_id, protocol_id, doctor_name)
    
    async def _handle_reject(self, query, protocol_id: str, patient_id: str, doctor_name: str):
        """Handle protocol rejection"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        logger.info(f"❌ Protocol {protocol_id} rejected by {doctor_name} for patient {patient_id}")
        
        await query.edit_message_text(
            text=f"❌ <b>PROTOCOL REJECTED</b>\n\n"
                 f"<b>Patient ID:</b> {patient_id}\n"
                 f"<b>Protocol:</b> {protocol_id}\n"
                 f"<b>Rejected by:</b> Dr. {doctor_name}\n"
                 f"<b>Time:</b> {timestamp}\n\n"
                 f"📝 <b>Please provide alternative instructions:</b>\n"
                 f"<code>/note {patient_id} your_alternative_instructions</code>",
            parse_mode="HTML"
        )
        
        # Store pending rejection
        pending_protocols[patient_id] = {
            "action": "rejected",
            "protocol_id": protocol_id,
            "doctor_name": doctor_name,
            "timestamp": timestamp
        }
        
        # Notify nurse to wait
        await self._notify_nurse_protocol_rejected(patient_id, protocol_id, doctor_name)
    
    async def _handle_modify(self, query, protocol_id: str, patient_id: str, doctor_name: str):
        """Handle protocol modification request"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        logger.info(f"✏️ Protocol {protocol_id} modification requested by {doctor_name} for patient {patient_id}")
        
        await query.edit_message_text(
            text=f"✏️ <b>PROTOCOL MODIFICATION REQUESTED</b>\n\n"
                 f"<b>Patient ID:</b> {patient_id}\n"
                 f"<b>Protocol:</b> {protocol_id}\n"
                 f"<b>Requested by:</b> Dr. {doctor_name}\n"
                 f"<b>Time:</b> {timestamp}\n\n"
                 f"📝 <b>Please specify modifications:</b>\n"
                 f"<code>/note {patient_id} your_modifications</code>",
            parse_mode="HTML"
        )
        
        # Store pending modification
        pending_protocols[patient_id] = {
            "action": "modify", 
            "protocol_id": protocol_id,
            "doctor_name": doctor_name,
            "timestamp": timestamp
        }

    async def note_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /note command for doctor instructions"""
        try:
            args = context.args
            if len(args) < 2:
                await update.message.reply_text(
                    "📝 <b>Usage:</b> /note &lt;patient_id&gt; &lt;your_instructions&gt;\n\n"
                    "<b>Examples:</b>\n"
                    "• <code>/note PAT001 Start vancomycin 1g q12h</code>\n"
                    "• <code>/note PAT002 Increase fluid rate, check lactate q2h</code>",
                    parse_mode="HTML"
                )
                return

            patient_id = args[0]
            instructions = " ".join(args[1:])
            
            user = update.effective_user
            doctor_name = user.full_name or user.username or f"Doctor_{user.id}"
            
            logger.info(f"📝 Doctor instructions from {doctor_name} for patient {patient_id}: {instructions}")
            
            # Check for pending protocol
            if patient_id in pending_protocols:
                protocol_info = pending_protocols[patient_id]
                action = protocol_info["action"]
                protocol_id = protocol_info["protocol_id"]
                
                if action == "rejected":
                    await self._send_alternative_instructions_to_nurse(patient_id, protocol_id, instructions, doctor_name)
                    reply_text = f"✅ <b>Alternative instructions sent to nurse</b>\n\n" \
                               f"<b>Patient:</b> {patient_id}\n" \
                               f"<b>Instructions:</b> {instructions}"
                elif action == "modify":
                    await self._send_modified_protocol_to_nurse(patient_id, protocol_id, instructions, doctor_name)
                    reply_text = f"✅ <b>Modified protocol sent to nurse</b>\n\n" \
                               f"<b>Patient:</b> {patient_id}\n" \
                               f"<b>Modifications:</b> {instructions}"
                
                # Clean up
                del pending_protocols[patient_id]
            else:
                # General instructions
                await self._send_general_instructions_to_nurse(patient_id, instructions, doctor_name)
                reply_text = f"✅ <b>Instructions sent to nursing staff</b>\n\n" \
                           f"<b>Patient:</b> {patient_id}\n" \
                           f"<b>Instructions:</b> {instructions}"

            await update.message.reply_text(reply_text, parse_mode="HTML")
            
        except Exception as e:
            logger.error(f"Error in note handler: {e}")
            await update.message.reply_text("❌ Error processing instructions. Please try again.")

    async def start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        chat_id = str(update.effective_chat.id)
        user_name = update.effective_user.full_name or update.effective_user.username or "Unknown"
        
        # Determine role
        if chat_id == DOCTOR_CHAT_ID:
            role = "👨‍⚕️ Doctor"
        elif chat_id == NURSE_CHAT_ID:
            role = "👩‍⚕️ Nurse"
        else:
            role = "❓ Unregistered"
        
        message = f"""🏥 <b>Asclepius AI - ICU Sepsis Early Warning System</b>

🤖 <b>Production Medical Alert Bot</b>

<b>User Information:</b>
• <b>Name:</b> {user_name}
• <b>Role:</b> {role}
• <b>Chat ID:</b> <code>{chat_id}</code>

<b>Available Commands:</b>
• <code>/note PAT001 instructions</code> - Send medical instructions
• <code>/status</code> - Check system status

<b>Automated Features:</b>
• Real-time critical sepsis alerts
• Protocol approval workflow
• Medical team communication

<b>System Status:</b> ✅ Production mode active

🏥 <i>Professional medical alert system</i>"""

        await update.message.reply_text(message, parse_mode="HTML")

    async def status_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        pending_count = len(pending_protocols)
        
        status_message = f"""📊 <b>Bot Status Report</b>

<b>Status:</b> ✅ Online (Production Mode)
<b>Pending Protocols:</b> {pending_count}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

<b>Configuration:</b>
• Bot Running: ✅ Active
• Nurse Chat: {'✅ Configured' if NURSE_CHAT_ID else '❌ Missing'}
• Doctor Chat: {'✅ Configured' if DOCTOR_CHAT_ID else '❌ Missing'}

<b>Features:</b>
• Critical alert workflow ✅
• Protocol approval buttons ✅
• Real-time notifications ✅

🏥 Asclepius AI - Production Environment"""
        
        await update.message.reply_text(status_message, parse_mode="HTML")

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle bot errors"""
        logger.error(f"Telegram bot error: {context.error}")
        
        # Notify user if possible
        if update and update.effective_chat:
            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="⚠️ A system error occurred. Please try again or contact support."
                )
            except Exception:
                pass  # Don't error in error handler
        
    # Helper methods for sending messages to nurse
    async def _send_approved_protocol_to_nurse(self, patient_id: str, protocol_id: str, doctor_name: str):
        """Send approved protocol implementation to nurse"""
        if not NURSE_CHAT_ID:
            logger.warning("No nurse chat ID configured")
            return
            
        message = f"""✅ <b>PROTOCOL APPROVED - IMPLEMENT IMMEDIATELY</b>

<b>Patient ID:</b> {patient_id}
<b>Protocol:</b> {protocol_id}
<b>Approved by:</b> Dr. {doctor_name}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

🚨 <b>SEPSIS PROTOCOL - TIME CRITICAL:</b>
• <b>Blood cultures:</b> Obtain before antibiotics (STAT)
• <b>Antibiotics:</b> Broad-spectrum within 1 hour
• <b>Fluids:</b> IV crystalloid 30ml/kg within 3 hours
• <b>Monitoring:</b> Vital signs every 15 minutes
• <b>Vasopressors:</b> If MAP &lt; 65 mmHg
• <b>Labs:</b> Recheck lactate in 2-4 hours

<b>⚡ BEGIN IMPLEMENTATION NOW</b>

🏥 Asclepius AI - ICU Sepsis Early Warning System"""

        await self._send_message_to_chat(NURSE_CHAT_ID, message)

    async def _notify_nurse_protocol_rejected(self, patient_id: str, protocol_id: str, doctor_name: str):
        """Notify nurse that protocol was rejected"""
        if not NURSE_CHAT_ID:
            return
            
        message = f"""❌ <b>PROTOCOL REJECTED - STANDBY</b>

<b>Patient ID:</b> {patient_id}
<b>Protocol:</b> {protocol_id}
<b>Rejected by:</b> Dr. {doctor_name}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

⏳ <b>DO NOT IMPLEMENT AI PROTOCOL</b>

Dr. {doctor_name} is preparing alternative instructions.
You will receive specific orders shortly.

<b>Continue standard monitoring while waiting.</b>

🏥 Asclepius AI - ICU Sepsis Early Warning System"""

        await self._send_message_to_chat(NURSE_CHAT_ID, message)

    async def _send_alternative_instructions_to_nurse(self, patient_id: str, protocol_id: str, instructions: str, doctor_name: str):
        """Send doctor's alternative instructions to nurse"""
        if not NURSE_CHAT_ID:
            return
            
        message = f"""📝 <b>ALTERNATIVE TREATMENT ORDERS</b>

<b>Patient ID:</b> {patient_id}
<b>Rejected Protocol:</b> {protocol_id}
<b>Doctor:</b> Dr. {doctor_name}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

👨‍⚕️ <b>DOCTOR'S ORDERS:</b>
{instructions}

<b>⚡ IMPLEMENT THESE ORDERS IMMEDIATELY</b>

🏥 Asclepius AI - ICU Sepsis Early Warning System"""

        await self._send_message_to_chat(NURSE_CHAT_ID, message)

    async def _send_modified_protocol_to_nurse(self, patient_id: str, protocol_id: str, modifications: str, doctor_name: str):
        """Send doctor's protocol modifications to nurse"""
        if not NURSE_CHAT_ID:
            return
            
        message = f"""✏️ <b>MODIFIED PROTOCOL</b>

<b>Patient ID:</b> {patient_id}
<b>Protocol:</b> {protocol_id}
<b>Modified by:</b> Dr. {doctor_name}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

🤖 <b>Base Protocol:</b> AI Sepsis Protocol
👨‍⚕️ <b>Doctor's Modifications:</b>
{modifications}

<b>⚡ IMPLEMENT MODIFIED PROTOCOL NOW</b>

🏥 Asclepius AI - ICU Sepsis Early Warning System"""

        await self._send_message_to_chat(NURSE_CHAT_ID, message)

    async def _send_general_instructions_to_nurse(self, patient_id: str, instructions: str, doctor_name: str):
        """Send general doctor instructions to nurse"""
        if not NURSE_CHAT_ID:
            return
            
        message = f"""📋 <b>DOCTOR'S INSTRUCTIONS</b>

<b>Patient ID:</b> {patient_id}
<b>Doctor:</b> Dr. {doctor_name}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

👨‍⚕️ <b>INSTRUCTIONS:</b>
{instructions}

🏥 Asclepius AI - ICU Sepsis Early Warning System"""

        await self._send_message_to_chat(NURSE_CHAT_ID, message)

    async def _send_message_to_chat(self, chat_id: str, message: str):
        """Send message to Telegram chat"""
        if not BOT_TOKEN or not chat_id or not self.app:
            logger.warning("Telegram not configured or bot not running")
            return
            
        try:
            await self.app.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
            logger.info(f"✅ Message sent to chat {chat_id}")
        except Exception as e:
            logger.error(f"❌ Failed to send message: {e}")

# Global bot runner instance
telegram_bot_runner = TelegramBotRunner()