"""
Telegram Bot Runner - Compatible Implementation
Handles bot lifecycle and button interactions with better compatibility
"""
import asyncio
import logging
from typing import Dict, Any, Optional
import httpx
from telegram import Bot, Update
from telegram.ext import Application, ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes

logger = logging.getLogger(__name__)

# Global storage for pending protocols
pending_protocols: Dict[str, Dict[str, Any]] = {}

# Import settings
from config import get_settings
settings = get_settings()

BOT_TOKEN = settings.telegram_bot_token
NURSE_CHAT_ID = settings.telegram_nurse_chat_id  
DOCTOR_CHAT_ID = settings.telegram_doctor_chat_id

class TelegramBotRunner:
    """Simplified Telegram bot that avoids problematic updater attributes"""
    
    def __init__(self):
        self.app: Optional[Application] = None
        self.bot: Optional[Bot] = None
        self.running = False
        self._polling_task = None
        
    def is_configured(self):
        """Check if bot is properly configured"""
        return bool(BOT_TOKEN and (NURSE_CHAT_ID or DOCTOR_CHAT_ID))
    
    async def start_bot(self):
        """Start the Telegram bot with compatible implementation"""
        if not self.is_configured():
            logger.warning("🤖 Telegram bot not configured - skipping bot startup")
            return False
            
        try:
            logger.info("🤖 Starting Telegram bot...")
            
            # Test bot token first
            test_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
            async with httpx.AsyncClient(timeout=10.0) as client:
                test_response = await client.get(test_url)
                if test_response.status_code != 200:
                    logger.error(f"❌ Invalid bot token: {test_response.text}")
                    return False
                
                bot_info = test_response.json().get("result", {})
                logger.info(f"✅ Bot token valid: @{bot_info.get('username', 'Unknown')}")
            
            # Create bot instance
            self.bot = Bot(token=BOT_TOKEN)
            
            # Create application with minimal settings to avoid attribute errors
            self.app = ApplicationBuilder().token(BOT_TOKEN).build()
            
            # Add handlers
            self.app.add_handler(CallbackQueryHandler(self.button_handler))
            self.app.add_handler(CommandHandler("note", self.note_handler))
            self.app.add_handler(CommandHandler("warning", self.warning_handler))
            self.app.add_handler(CommandHandler("start", self.start_handler))
            self.app.add_error_handler(self.error_handler)
            
            # Initialize application
            await self.app.initialize()
            await self.app.start()
            
            # Start custom polling to avoid updater issues
            self.running = True
            self._polling_task = asyncio.create_task(self._custom_polling())
            
            logger.info("✅ Telegram bot started successfully")
            logger.info(f"📱 Nurse Chat ID: {NURSE_CHAT_ID}")
            logger.info(f"👨‍⚕️ Doctor Chat ID: {DOCTOR_CHAT_ID}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start Telegram bot: {e}")
            self.running = False
            return False
    
    async def _custom_polling(self):
        """Custom polling implementation that avoids updater attribute issues"""
        logger.info("🔄 Starting custom Telegram polling...")
        offset = 0
        consecutive_errors = 0
        max_consecutive_errors = 3
        
        while self.running:
            try:
                # Get updates directly via HTTP API to avoid library issues
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
                                    # Process update through the application
                                    update = Update.de_json(update_data, self.bot)
                                    if update:
                                        await self.app.process_update(update)
                                        offset = update.update_id + 1
                                except Exception as e:
                                    logger.error(f"Error processing update: {e}")
                                    
                            # Reset error counter on successful poll
                            consecutive_errors = 0
                        else:
                            logger.error(f"Telegram API error: {data}")
                            consecutive_errors += 1
                    else:
                        logger.error(f"HTTP error getting updates: {response.status_code}")
                        consecutive_errors += 1
                        
                # Break if too many consecutive errors
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
                
        logger.info("🛑 Custom polling stopped")
        self.running = False
    
    async def stop_bot(self):
        """Stop the Telegram bot"""
        if self.running:
            logger.info("🛑 Stopping Telegram bot...")
            self.running = False
            
            try:
                # Cancel polling task
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
    
    # Bot handlers
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button clicks"""
        query = update.callback_query
        data = query.data
        
        logger.info(f"📱 Button clicked: '{data}' from chat {update.effective_chat.id}")
        
        try:
            await query.answer()
        except Exception as e:
            logger.warning(f"Callback answer error: {e}")

        # Parse callback data
        if data.startswith("approve"):
            action = "approve"
        elif data.startswith("reject"):
            action = "reject"  
        elif data.startswith("modify"):
            action = "modify"
        else:
            logger.error(f"❌ Unknown callback data: {data}")
            await query.edit_message_text(f"⚠️ Unknown action: {data}")
            return

        # Extract protocol and patient ID
        parts = data.split("_")
        protocol_id = parts[1] if len(parts) > 1 else "PROTO_DEFAULT"
        patient_id = parts[2] if len(parts) > 2 else "UNKNOWN"
        
        logger.info(f"🔍 Processed: action={action}, protocol={protocol_id}, patient={patient_id}")
        
        if action == "approve":
            logger.info(f"✅ Doctor approved protocol {protocol_id} for patient {patient_id}")
            await query.edit_message_text(
                text=f"✅ <b>PROTOCOL APPROVED</b>\n\n"
                     f"Patient ID: {patient_id}\n"
                     f"Protocol: {protocol_id}\n\n"
                     f"✅ Sending AI recommendation to nurse...",
                parse_mode="HTML"
            )
            
            await self.send_ai_recommendation_to_nurse(patient_id, protocol_id)

        elif action == "reject":
            logger.info(f"❌ Doctor rejected protocol {protocol_id} for patient {patient_id}")
            await query.edit_message_text(
                text=f"❌ <b>PROTOCOL REJECTED</b>\n\n"
                     f"Patient ID: {patient_id}\n"
                     f"Protocol: {protocol_id}\n\n"
                     f"Please add a note with:\n"
                     f"<code>/note {patient_id} your_note_here</code>",
                parse_mode="HTML"
            )
            
            pending_protocols[patient_id] = {
                "action": "rejected",
                "protocol_id": protocol_id
            }
            
            await self.notify_nurse_to_wait(patient_id, protocol_id)

        elif action == "modify":
            logger.info(f"✏️ Doctor wants to modify protocol {protocol_id} for patient {patient_id}")
            await query.edit_message_text(
                text=f"✏️ <b>PROTOCOL MODIFICATION REQUESTED</b>\n\n"
                     f"Patient ID: {patient_id}\n"
                     f"Protocol: {protocol_id}\n\n"
                     f"Please add modification notes with:\n"
                     f"<code>/note {patient_id} your_modifications_here</code>",
                parse_mode="HTML"
            )
            
            pending_protocols[patient_id] = {
                "action": "modify", 
                "protocol_id": protocol_id
            }

    async def note_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /note command"""
        try:
            args = context.args
            if len(args) < 2:
                await update.message.reply_text(
                    "❌ Usage: /note <patient_id> <your_note>\n"
                    "Example: /note PAT001 Start vancomycin 1g q12h",
                    parse_mode="HTML"
                )
                return

            patient_id = args[0]
            note_text = " ".join(args[1:])
            
            logger.info(f"📝 Doctor note for {patient_id}: {note_text}")
            
            # Send note to nurse
            if NURSE_CHAT_ID:
                message = f"""📝 <b>DOCTOR'S INSTRUCTIONS</b>

<b>Patient ID:</b> {patient_id}
<b>Instructions:</b> {note_text}

<i>Please implement these modifications to the treatment protocol.</i>

🏥 Asclepius AI - ICU Sepsis Early Warning System"""

                await self.bot.send_message(
                    chat_id=NURSE_CHAT_ID,
                    text=message,
                    parse_mode="HTML"
                )
                
                # Clear pending protocol
                if patient_id in pending_protocols:
                    del pending_protocols[patient_id]

            reply = f"✅ <b>NOTE SENT</b>\n\nYour instructions for {patient_id} have been sent to the nurse.\n\n<i>Note:</i> {note_text}"
            await update.message.reply_text(reply, parse_mode="HTML")
            
        except Exception as e:
            logger.error(f"Error in note handler: {e}")
            await update.message.reply_text("❌ Error processing note. Please try again.")

    async def start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        message = f"""🏥 <b>Asclepius AI - ICU Sepsis Early Warning System</b>

🤖 <b>Telegram Bot Active</b>

<b>Available Commands:</b>
• <code>/note PAT001 message</code> - Doctor instructions
• <code>/warning</code> - Test warning alert

<b>Chat Information:</b>
• Chat ID: <code>{update.effective_chat.id}</code>
• User: {update.effective_user.first_name or 'Unknown'}

<b>System Status:</b> ✅ Connected and ready for medical alerts

🏥 Medical alert workflow operational!"""

        await update.message.reply_text(message, parse_mode="HTML")

    async def warning_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /warning command for testing"""
        message = f"""⚠️ <b>WARNING ALERT</b>

<b>Test Alert</b> - Command initiated
<b>Chat ID:</b> {update.effective_chat.id}
<b>User:</b> {update.effective_user.first_name or 'Unknown'}

This is a test warning alert to verify the bot is working properly.

🏥 Asclepius AI System"""

        await update.message.reply_text(message, parse_mode="HTML")

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle bot errors"""
        logger.error(f"Telegram bot error: {context.error}")
        
    # Helper methods
    async def send_ai_recommendation_to_nurse(self, patient_id: str, protocol_id: str):
        """Send AI protocol recommendation to nurse"""
        if not NURSE_CHAT_ID:
            logger.warning("No nurse chat ID configured")
            return
            
        try:
            message = f"""🤖 <b>AI PROTOCOL APPROVED</b>

<b>Patient ID:</b> {patient_id}
<b>Protocol:</b> {protocol_id}

<b>📋 Recommended Actions:</b>
• Start broad-spectrum antibiotics within 1 hour
• Obtain blood cultures before antibiotics
• Administer IV fluids 30ml/kg within 3 hours  
• Monitor vital signs every 15 minutes
• Consider vasopressor support if needed
• Lactate level recheck in 2-4 hours

<b>⚡ Time Critical:</b> Begin implementation immediately

🏥 Asclepius AI - ICU Sepsis Early Warning System"""

            await self.bot.send_message(
                chat_id=NURSE_CHAT_ID,
                text=message,
                parse_mode="HTML"
            )
            logger.info(f"✅ AI recommendation sent to nurse for {patient_id}")
            
        except Exception as e:
            logger.error(f"Failed to send AI recommendation: {e}")

    async def notify_nurse_to_wait(self, patient_id: str, protocol_id: str):
        """Notify nurse to wait for doctor's note"""
        if not NURSE_CHAT_ID:
            return
            
        try:
            message = f"""⏳ <b>WAITING FOR DOCTOR'S NOTE</b>

<b>Patient ID:</b> {patient_id}
<b>Protocol:</b> {protocol_id}

The doctor has rejected the standard protocol and is preparing alternative instructions.

<i>Please wait for the doctor's note before proceeding.</i>

🏥 Asclepius AI - ICU Sepsis Early Warning System"""

            await self.bot.send_message(
                chat_id=NURSE_CHAT_ID,
                text=message,
                parse_mode="HTML"
            )
            
        except Exception as e:
            logger.error(f"Failed to notify nurse: {e}")

# Global instance
telegram_bot_runner = TelegramBotRunner()
import asyncio
import logging
from typing import Dict, Any, Optional
import httpx
from telegram import Bot, Update
from telegram.ext import Application, ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes

logger = logging.getLogger(__name__)

# Global storage for pending protocols
pending_protocols: Dict[str, Dict[str, Any]] = {}

# Global storage for protocol notes
protocol_notes: Dict[str, str] = {}

# Import settings
from config import get_settings
settings = get_settings()

BOT_TOKEN = settings.telegram_bot_token
NURSE_CHAT_ID = settings.telegram_nurse_chat_id  
DOCTOR_CHAT_ID = settings.telegram_doctor_chat_id

class TelegramBotRunner:
    """Simplified Telegram bot that avoids problematic updater attributes"""
    
    def __init__(self):
        self.app: Optional[Application] = None
        self.bot: Optional[Bot] = None
        self.running = False
        self._polling_task = None
        
    def is_configured(self):
        """Check if bot is properly configured"""
        return bool(BOT_TOKEN and (NURSE_CHAT_ID or DOCTOR_CHAT_ID))
    
    async def start_bot(self):
        """Start the Telegram bot with compatible implementation"""
        if not self.is_configured():
            logger.warning("🤖 Telegram bot not configured - skipping bot startup")
            return False
            
        try:
            logger.info("🤖 Starting Telegram bot...")
            
            # Test bot token first
            test_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
            async with httpx.AsyncClient(timeout=10.0) as client:
                test_response = await client.get(test_url)
                if test_response.status_code != 200:
                    logger.error(f"❌ Invalid bot token: {test_response.text}")
                    return False
                
                bot_info = test_response.json().get("result", {})
                logger.info(f"✅ Bot token valid: @{bot_info.get('username', 'Unknown')}")
            
            # Create bot instance
            self.bot = Bot(token=BOT_TOKEN)
            
            # Create application with minimal settings to avoid attribute errors
            try:
                self.app = ApplicationBuilder().token(BOT_TOKEN).build()
                logger.info("✅ Application builder created successfully")
            except Exception as e:
                logger.error(f"❌ Failed to create application: {e}")
                return False
            
            # Add handlers
            try:
                self.app.add_handler(CallbackQueryHandler(self.button_handler))
                self.app.add_handler(CommandHandler("note", self.note_handler))
                self.app.add_handler(CommandHandler("warning", self.warning_handler))
                self.app.add_handler(CommandHandler("start", self.start_handler))
                self.app.add_error_handler(self.error_handler)
                logger.info("✅ Handlers added successfully")
            except Exception as e:
                logger.error(f"❌ Failed to add handlers: {e}")
                return False
            
            # Initialize application
            try:
                await self.app.initialize()
                logger.info("✅ Application initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize application: {e}")
                return False
                
            try:
                await self.app.start()
                logger.info("✅ Application started")
            except Exception as e:
                logger.error(f"❌ Failed to start application: {e}")
                return False
            
            # Start custom polling to avoid updater issues
            self.running = True
            self._polling_task = asyncio.create_task(self._custom_polling())
            
            logger.info("✅ Telegram bot started successfully")
            logger.info(f"📱 Nurse Chat ID: {NURSE_CHAT_ID}")
            logger.info(f"👨‍⚕️ Doctor Chat ID: {DOCTOR_CHAT_ID}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start Telegram bot: {e}")
            self.running = False
            return False
    
    async def _custom_polling(self):
        """Custom polling implementation that avoids updater attribute issues"""
        logger.info("🔄 Starting custom Telegram polling...")
        offset = 0
        consecutive_errors = 0
        max_consecutive_errors = 3
        
        while self.running:
            try:
                # Get updates directly via HTTP API to avoid library issues
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
                                    # Process update through the application
                                    update = Update.de_json(update_data, self.bot)
                                    if update:
                                        await self.app.process_update(update)
                                        offset = update.update_id + 1
                                except Exception as e:
                                    logger.error(f"Error processing update: {e}")
                                    
                            # Reset error counter on successful poll
                            consecutive_errors = 0
                        else:
                            logger.error(f"Telegram API error: {data}")
                            consecutive_errors += 1
                    else:
                        logger.error(f"HTTP error getting updates: {response.status_code}")
                        consecutive_errors += 1
                        
                # Break if too many consecutive errors
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
                
        logger.info("🛑 Custom polling stopped")
        self.running = False
    
    async def stop_bot(self):
        """Stop the Telegram bot"""
        if self.running:
            logger.info("🛑 Stopping Telegram bot...")
            self.running = False
            
            try:
                # Cancel polling task
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
    
    # Bot handlers
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button clicks"""
        query = update.callback_query
        data = query.data
        
        logger.info(f"📱 Button clicked: '{data}' from chat {update.effective_chat.id}")
        
        try:
            await query.answer()
        except Exception as e:
            logger.warning(f"Callback answer error: {e}")

        # Parse callback data
        if data.startswith("approve"):
            action = "approve"
        elif data.startswith("reject"):
            action = "reject"  
        elif data.startswith("modify"):
            action = "modify"
        else:
            logger.error(f"❌ Unknown callback data: {data}")
            await query.edit_message_text(f"⚠️ Unknown action: {data}")
            return

        # Extract protocol and patient ID
        parts = data.split("_")
        protocol_id = parts[1] if len(parts) > 1 else "PROTO_DEFAULT"
        patient_id = parts[2] if len(parts) > 2 else "UNKNOWN"
        
        logger.info(f"🔍 Processed: action={action}, protocol={protocol_id}, patient={patient_id}")
        
        if action == "approve":
            logger.info(f"✅ Doctor approved protocol {protocol_id} for patient {patient_id}")
            await query.edit_message_text(
                text=f"✅ <b>PROTOCOL APPROVED</b>\n\n"
                     f"Patient ID: {patient_id}\n"
                     f"Protocol: {protocol_id}\n\n"
                     f"✅ Sending AI recommendation to nurse...",
                parse_mode="HTML"
            )
            
            await self.send_ai_recommendation_to_nurse(patient_id, protocol_id)

        elif action == "reject":
            logger.info(f"❌ Doctor rejected protocol {protocol_id} for patient {patient_id}")
            await query.edit_message_text(
                text=f"❌ <b>PROTOCOL REJECTED</b>\n\n"
                     f"Patient ID: {patient_id}\n"
                     f"Protocol: {protocol_id}\n\n"
                     f"Please add a note with:\n"
                     f"<code>/note {patient_id} your_note_here</code>",
                parse_mode="HTML"
            )
            
            pending_protocols[patient_id] = {
                "action": "rejected",
                "protocol_id": protocol_id
            }
            
            await self.notify_nurse_to_wait(patient_id, protocol_id)

        elif action == "modify":
            logger.info(f"✏️ Doctor wants to modify protocol {protocol_id} for patient {patient_id}")
            await query.edit_message_text(
                text=f"✏️ <b>PROTOCOL MODIFICATION REQUESTED</b>\n\n"
                     f"Patient ID: {patient_id}\n"
                     f"Protocol: {protocol_id}\n\n"
                     f"Please add modification notes with:\n"
                     f"<code>/note {patient_id} your_modifications_here</code>",
                parse_mode="HTML"
            )
            
            pending_protocols[patient_id] = {
                "action": "modify", 
                "protocol_id": protocol_id
            }

    async def note_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /note command"""
        try:
            args = context.args
            if len(args) < 2:
                await update.message.reply_text(
                    "❌ Usage: /note <patient_id> <your_note>\n"
                    "Example: /note PAT001 Start vancomycin 1g q12h",
                    parse_mode="HTML"
                )
                return

            patient_id = args[0]
            note_text = " ".join(args[1:])
            
            logger.info(f"📝 Doctor note for {patient_id}: {note_text}")
            
            # Send note to nurse
            if NURSE_CHAT_ID:
                message = f"""📝 <b>DOCTOR'S INSTRUCTIONS</b>

<b>Patient ID:</b> {patient_id}
<b>Instructions:</b> {note_text}

<i>Please implement these modifications to the treatment protocol.</i>

🏥 Asclepius AI - ICU Sepsis Early Warning System"""

                await self.bot.send_message(
                    chat_id=NURSE_CHAT_ID,
                    text=message,
                    parse_mode="HTML"
                )
                
                # Clear pending protocol
                if patient_id in pending_protocols:
                    del pending_protocols[patient_id]

            reply = f"✅ <b>NOTE SENT</b>\n\nYour instructions for {patient_id} have been sent to the nurse.\n\n<i>Note:</i> {note_text}"
            await update.message.reply_text(reply, parse_mode="HTML")
            
        except Exception as e:
            logger.error(f"Error in note handler: {e}")
            await update.message.reply_text("❌ Error processing note. Please try again.")

    async def start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        message = f"""🏥 <b>Asclepius AI - ICU Sepsis Early Warning System</b>

🤖 <b>Telegram Bot Active</b>

<b>Available Commands:</b>
• <code>/note PAT001 message</code> - Doctor instructions
• <code>/warning</code> - Test warning alert

<b>Chat Information:</b>
• Chat ID: <code>{update.effective_chat.id}</code>
• User: {update.effective_user.first_name or 'Unknown'}

<b>System Status:</b> ✅ Connected and ready for medical alerts

🏥 Medical alert workflow operational!"""

        await update.message.reply_text(message, parse_mode="HTML")

    async def warning_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /warning command for testing"""
        message = f"""⚠️ <b>WARNING ALERT</b>

<b>Test Alert</b> - Command initiated
<b>Chat ID:</b> {update.effective_chat.id}
<b>User:</b> {update.effective_user.first_name or 'Unknown'}

This is a test warning alert to verify the bot is working properly.

🏥 Asclepius AI System"""

        await update.message.reply_text(message, parse_mode="HTML")

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle bot errors"""
        logger.error(f"Telegram bot error: {context.error}")
        
    # Helper methods
    async def send_ai_recommendation_to_nurse(self, patient_id: str, protocol_id: str):
        """Send AI protocol recommendation to nurse"""
        if not NURSE_CHAT_ID:
            logger.warning("No nurse chat ID configured")
            return
            
        try:
            message = f"""🤖 <b>AI PROTOCOL APPROVED</b>

<b>Patient ID:</b> {patient_id}
<b>Protocol:</b> {protocol_id}

<b>📋 Recommended Actions:</b>
• Start broad-spectrum antibiotics within 1 hour
• Obtain blood cultures before antibiotics
• Administer IV fluids 30ml/kg within 3 hours  
• Monitor vital signs every 15 minutes
• Consider vasopressor support if needed
• Lactate level recheck in 2-4 hours

<b>⚡ Time Critical:</b> Begin implementation immediately

🏥 Asclepius AI - ICU Sepsis Early Warning System"""

            await self.bot.send_message(
                chat_id=NURSE_CHAT_ID,
                text=message,
                parse_mode="HTML"
            )
            logger.info(f"✅ AI recommendation sent to nurse for {patient_id}")
            
        except Exception as e:
            logger.error(f"Failed to send AI recommendation: {e}")

    async def notify_nurse_to_wait(self, patient_id: str, protocol_id: str):
        """Notify nurse to wait for doctor's note"""
        if not NURSE_CHAT_ID:
            return
            
        try:
            message = f"""⏳ <b>WAITING FOR DOCTOR'S NOTE</b>

<b>Patient ID:</b> {patient_id}
<b>Protocol:</b> {protocol_id}

The doctor has rejected the standard protocol and is preparing alternative instructions.

<i>Please wait for the doctor's note before proceeding.</i>

🏥 Asclepius AI - ICU Sepsis Early Warning System"""

            await self.bot.send_message(
                chat_id=NURSE_CHAT_ID,
                text=message,
                parse_mode="HTML"
            )
            
        except Exception as e:
            logger.error(f"Failed to notify nurse: {e}")

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button clicks with flexible parsing"""
        query = update.callback_query
        data = query.data
        
        logger.info(f"📱 Button clicked: '{data}' from chat {update.effective_chat.id}")
        
        try:
            await query.answer()
        except Exception as e:
            logger.warning(f"Callback answer error: {e}")

        # Handle different callback data formats
        if data.startswith("approve"):
            action = "approve"
        elif data.startswith("reject"):
            action = "reject"  
        elif data.startswith("modify"):
            action = "modify"
        else:
            logger.error(f"❌ Unknown callback data: {data}")
            await query.edit_message_text(f"⚠️ Unknown action: {data}")
            return

        # Parse protocol and patient ID from callback data
        parts = data.split("_")
        protocol_id = parts[1] if len(parts) > 1 else "PROTO_DEFAULT"
        patient_id = parts[2] if len(parts) > 2 else "UNKNOWN"
        
        logger.info(f"🔍 Processed: action={action}, protocol={protocol_id}, patient={patient_id}")
        
        if action == "approve":
            logger.info(f"✅ Doctor approved protocol {protocol_id} for patient {patient_id}")
            await query.edit_message_text(
                text=f"✅ <b>PROTOCOL APPROVED</b>\n\n"
                     f"Patient ID: {patient_id}\n"
                     f"Protocol: {protocol_id}\n\n"
                     f"✅ Sending AI recommendation to nurse...",
                parse_mode="HTML"
            )
            
            # Send AI recommendation to nurse
            await self.send_ai_recommendation_to_nurse(patient_id, protocol_id)

        elif action == "reject":
            logger.info(f"❌ Doctor rejected protocol {protocol_id} for patient {patient_id}")
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
                "timestamp": context.application.bot_data
            }
            
            # Notify nurse to wait
            await self.notify_nurse_to_wait(patient_id, protocol_id)

        elif action == "modify":
            logger.info(f"✏️ Doctor wants to modify protocol {protocol_id} for patient {patient_id}")
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
                "timestamp": context.application.bot_data
            }

    async def note_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /note command"""
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
                await self.send_rejection_note_to_nurse(patient_id, protocol_id, note)
                reply = f"📝 <b>Rejection note sent to nurse</b>\n\n" \
                       f"Patient: {patient_id}\n" \
                       f"Note: {note}"
                       
            elif action == "modify":
                # Send modification note to nurse
                await self.send_modification_to_nurse(patient_id, protocol_id, note)
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
            await self.send_general_note_to_nurse(patient_id, note)

        await update.message.reply_text(reply, parse_mode="HTML")

    async def start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        message = f"""🏥 <b>Asclepius AI - ICU Sepsis Early Warning System</b>

🤖 <b>Telegram Bot Active</b>

<b>Available Commands:</b>
• <code>/note PAT001 message</code> - Doctor instructions
• <code>/warning</code> - Test warning alert

<b>Chat Information:</b>
• Chat ID: <code>{update.effective_chat.id}</code>
• User: {update.effective_user.first_name or 'Unknown'}

<b>System Status:</b> ✅ Connected and ready for medical alerts

🏥 Medical alert workflow operational!"""

        await update.message.reply_text(message, parse_mode="HTML")

    async def warning_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /warning command for testing"""
        message = f"""⚠️ <b>WARNING ALERT</b>

Patient monitoring shows elevated sepsis risk.
Please review vitals and increase monitoring frequency.

Sent by: Dr. {update.effective_user.first_name or 'Doctor'}
Time: {update.message.date}

🏥 Asclepius AI System"""

        await self.send_telegram_message(NURSE_CHAT_ID, message)
        await update.message.reply_text("⚠️ Warning alert sent to nurse", parse_mode="HTML")

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle bot errors"""
        logger.error(f"Telegram bot error: {context.error}")

    # Helper methods for sending messages
    async def send_ai_recommendation_to_nurse(self, patient_id: str, protocol_id: str):
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

        await self.send_telegram_message(NURSE_CHAT_ID, message)

    async def notify_nurse_to_wait(self, patient_id: str, protocol_id: str):
        """Notify nurse that protocol was rejected and to wait for doctor's note"""
        message = f"""❌ <b>PROTOCOL REJECTED</b>

<b>Patient ID:</b> {patient_id}
<b>Protocol:</b> {protocol_id}

⏳ <b>Please wait for doctor's alternative instructions</b>

Doctor is preparing alternative treatment plan.
You will receive updated instructions shortly.

🏥 Asclepius AI System"""

        await self.send_telegram_message(NURSE_CHAT_ID, message)

    async def send_rejection_note_to_nurse(self, patient_id: str, protocol_id: str, note: str):
        """Send doctor's rejection note with alternative instructions to nurse"""
        message = f"""📝 <b>DOCTOR'S ALTERNATIVE INSTRUCTIONS</b>

<b>Patient ID:</b> {patient_id}
<b>Rejected Protocol:</b> {protocol_id}

👨‍⚕️ <b>Doctor's Instructions:</b>
{note}

Please follow these alternative instructions instead of the AI protocol.

🏥 Asclepius AI System"""

        await self.send_telegram_message(NURSE_CHAT_ID, message)

    async def send_modification_to_nurse(self, patient_id: str, protocol_id: str, modifications: str):
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

        await self.send_telegram_message(NURSE_CHAT_ID, message)

    async def send_general_note_to_nurse(self, patient_id: str, note: str):
        """Send general doctor note to nurse"""
        message = f"""📋 <b>DOCTOR'S NOTE</b>

<b>Patient ID:</b> {patient_id}

👨‍⚕️ <b>Note:</b>
{note}

🏥 Asclepius AI System"""

        await self.send_telegram_message(NURSE_CHAT_ID, message)

    async def send_telegram_message(self, chat_id: str, message: str):
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
            logger.info(f"✅ Message sent to {chat_id}")
        except Exception as e:
            logger.error(f"❌ Failed to send message: {e}")

# Global bot runner instance
telegram_bot_runner = TelegramBotRunner()