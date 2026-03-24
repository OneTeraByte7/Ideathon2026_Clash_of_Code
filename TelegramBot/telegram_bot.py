#!/usr/bin/env python3
"""
Asclepius AI - Production Telegram Bot
Handles critical medical protocol approvals and notifications
"""
import logging
import asyncio
import httpx
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes
import sys

# Add server directory to path for imports
server_path = Path(__file__).parent.parent / "server"
sys.path.insert(0, str(server_path))

from config import get_settings

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load configuration
settings = get_settings()
BOT_TOKEN = settings.telegram_bot_token
NURSE_CHAT_ID = settings.telegram_nurse_chat_id
DOCTOR_CHAT_ID = settings.telegram_doctor_chat_id

# Storage for pending protocols and notes (in production use Redis/Database)
pending_protocols: Dict[str, Dict[str, Any]] = {}
protocol_notes: Dict[str, str] = {}

class AsclepiusTelegramBot:
    """Production Telegram Bot for Asclepius AI Medical System"""
    
    def __init__(self):
        self.bot_token = BOT_TOKEN
        self.nurse_chat_id = NURSE_CHAT_ID
        self.doctor_chat_id = DOCTOR_CHAT_ID
        self.app: Optional[Application] = None
        
    def is_configured(self) -> bool:
        """Check if bot is properly configured"""
        return bool(self.bot_token and (self.nurse_chat_id or self.doctor_chat_id))
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle doctor's protocol approval/rejection buttons"""
        query = update.callback_query
        data = query.data
        
        logger.info(f"Button clicked: {data} by user {query.from_user.id}")
        
        try:
            await query.answer()
        except Exception as e:
            logger.warning(f"Failed to acknowledge callback: {e}")
            return
        
        # Parse callback data: action_protocol_id_patient_id
        parts = data.split("_")
        if len(parts) < 3:
            await query.edit_message_text("⚠️ Invalid button data format")
            return
            
        action = parts[0]
        protocol_id = parts[1] 
        patient_id = parts[2]
        
        doctor_name = query.from_user.full_name or query.from_user.username or "Unknown Doctor"
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        if action == "approve":
            await self._handle_approve(query, protocol_id, patient_id, doctor_name, timestamp)
        elif action == "reject":
            await self._handle_reject(query, protocol_id, patient_id, doctor_name, timestamp)
        elif action == "modify":
            await self._handle_modify(query, protocol_id, patient_id, doctor_name, timestamp)
        else:
            await query.edit_message_text(f"⚠️ Unknown action: {action}")
    
    async def _handle_approve(self, query, protocol_id: str, patient_id: str, doctor_name: str, timestamp: str):
        """Handle protocol approval"""
        logger.info(f"Protocol {protocol_id} approved by {doctor_name} for patient {patient_id}")
        
        await query.edit_message_text(
            text=f"✅ <b>PROTOCOL APPROVED</b>\n\n"
                 f"<b>Patient ID:</b> {patient_id}\n"
                 f"<b>Protocol:</b> {protocol_id}\n"
                 f"<b>Approved by:</b> {doctor_name}\n"
                 f"<b>Time:</b> {timestamp}\n\n"
                 f"✅ <b>Sending treatment protocol to nursing staff...</b>",
            parse_mode="HTML"
        )
        
        # Send implementation instructions to nurse
        await self._send_approved_protocol_to_nurse(patient_id, protocol_id, doctor_name)
        
        # Update protocol status via API
        await self._update_protocol_status(protocol_id, "approved", f"Approved by {doctor_name}")
    
    async def _handle_reject(self, query, protocol_id: str, patient_id: str, doctor_name: str, timestamp: str):
        """Handle protocol rejection"""
        logger.info(f"Protocol {protocol_id} rejected by {doctor_name} for patient {patient_id}")
        
        await query.edit_message_text(
            text=f"❌ <b>PROTOCOL REJECTED</b>\n\n"
                 f"<b>Patient ID:</b> {patient_id}\n"
                 f"<b>Protocol:</b> {protocol_id}\n"
                 f"<b>Rejected by:</b> {doctor_name}\n"
                 f"<b>Time:</b> {timestamp}\n\n"
                 f"📝 <b>Please provide alternative instructions:</b>\n"
                 f"<code>/note {patient_id} your_alternative_instructions</code>",
            parse_mode="HTML"
        )
        
        # Store pending rejection for note handling
        pending_protocols[patient_id] = {
            "action": "rejected",
            "protocol_id": protocol_id,
            "doctor_name": doctor_name,
            "timestamp": timestamp
        }
        
        # Notify nurse to wait for alternative instructions
        await self._notify_nurse_protocol_rejected(patient_id, protocol_id, doctor_name)
        
        # Update protocol status via API
        await self._update_protocol_status(protocol_id, "rejected", f"Rejected by {doctor_name}")
    
    async def _handle_modify(self, query, protocol_id: str, patient_id: str, doctor_name: str, timestamp: str):
        """Handle protocol modification request"""
        logger.info(f"Protocol {protocol_id} modification requested by {doctor_name} for patient {patient_id}")
        
        await query.edit_message_text(
            text=f"✏️ <b>PROTOCOL MODIFICATION REQUESTED</b>\n\n"
                 f"<b>Patient ID:</b> {patient_id}\n"
                 f"<b>Protocol:</b> {protocol_id}\n"
                 f"<b>Requested by:</b> {doctor_name}\n"
                 f"<b>Time:</b> {timestamp}\n\n"
                 f"📝 <b>Please specify modifications:</b>\n"
                 f"<code>/note {patient_id} your_modifications</code>",
            parse_mode="HTML"
        )
        
        # Store pending modification for note handling
        pending_protocols[patient_id] = {
            "action": "modify",
            "protocol_id": protocol_id,
            "doctor_name": doctor_name,
            "timestamp": timestamp
        }
        
        # Update protocol status via API
        await self._update_protocol_status(protocol_id, "pending_modification", f"Modification requested by {doctor_name}")
    
    async def note_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /note command for doctor instructions"""
        if not context.args or len(context.args) < 2:
            await update.message.reply_text(
                "📝 <b>Usage:</b> /note &lt;patient_id&gt; &lt;your_instructions&gt;\n\n"
                "<b>Example:</b>\n"
                "<code>/note PAT001 Start vancomycin 1g q12h, increase monitoring frequency</code>",
                parse_mode="HTML"
            )
            return
        
        patient_id = context.args[0]
        note_text = " ".join(context.args[1:])
        doctor_name = update.effective_user.full_name or update.effective_user.username or "Unknown Doctor"
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        logger.info(f"Doctor note from {doctor_name} for patient {patient_id}: {note_text}")
        
        # Check if there's a pending protocol action for this patient
        if patient_id in pending_protocols:
            protocol_info = pending_protocols[patient_id]
            action = protocol_info["action"]
            protocol_id = protocol_info["protocol_id"]
            
            if action == "rejected":
                await self._send_alternative_instructions_to_nurse(patient_id, protocol_id, note_text, doctor_name)
                reply_text = f"✅ <b>Alternative instructions sent to nurse</b>\n\n" \
                           f"<b>Patient:</b> {patient_id}\n" \
                           f"<b>Instructions:</b> {note_text}"
                           
            elif action == "modify":
                await self._send_modified_protocol_to_nurse(patient_id, protocol_id, note_text, doctor_name)
                reply_text = f"✅ <b>Modified protocol sent to nurse</b>\n\n" \
                           f"<b>Patient:</b> {patient_id}\n" \
                           f"<b>Modifications:</b> {note_text}"
            
            # Clean up pending protocol
            del pending_protocols[patient_id]
            
            # Update protocol with notes via API
            await self._update_protocol_status(protocol_id, "completed", note_text)
        else:
            # General doctor note
            await self._send_general_note_to_nurse(patient_id, note_text, doctor_name)
            reply_text = f"✅ <b>Note sent to nursing staff</b>\n\n" \
                       f"<b>Patient:</b> {patient_id}\n" \
                       f"<b>Note:</b> {note_text}"
        
        await update.message.reply_text(reply_text, parse_mode="HTML")
    
    async def start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command"""
        chat_id = str(update.effective_chat.id)
        user_name = update.effective_user.full_name or update.effective_user.username or "Unknown"
        
        # Determine user role based on chat ID
        role = "👨‍⚕️ Doctor" if chat_id == self.doctor_chat_id else "👩‍⚕️ Nurse" if chat_id == self.nurse_chat_id else "❓ Unknown Role"
        
        message = f"""🏥 <b>Asclepius AI - ICU Sepsis Early Warning System</b>

🤖 <b>Medical Alert Bot Active</b>

<b>Your Role:</b> {role}
<b>Chat ID:</b> <code>{chat_id}</code>
<b>User:</b> {user_name}

<b>Available Commands:</b>
• <code>/note PAT001 instructions</code> - Send medical instructions
• <code>/status</code> - Check system status
• <code>/help</code> - Show this help message

<b>Automated Functions:</b>
• Receive critical sepsis alerts with approval buttons (Doctors)
• Receive warning alerts and protocol instructions (Nurses)
• Real-time medical protocol workflow management

<b>System Status:</b> ✅ Online and ready for medical alerts

🏥 <i>Professional medical alert system - Production mode</i>"""

        await update.message.reply_text(message, parse_mode="HTML")
    
    async def status_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /status command"""
        pending_count = len(pending_protocols)
        
        status_message = f"""📊 <b>System Status Report</b>

<b>Bot Status:</b> ✅ Online
<b>Pending Protocols:</b> {pending_count}
<b>System Mode:</b> Production
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

<b>Configuration:</b>
• Nurse Chat: {'✅ Configured' if self.nurse_chat_id else '❌ Not Set'}
• Doctor Chat: {'✅ Configured' if self.doctor_chat_id else '❌ Not Set'}

<b>Recent Activity:</b>"""
        
        if pending_count > 0:
            status_message += "\n\n<b>Pending Protocols:</b>"
            for patient_id, info in list(pending_protocols.items())[:5]:  # Show max 5
                status_message += f"\n• {patient_id}: {info.get('action', 'unknown')} - {info.get('protocol_id', 'N/A')}"
        else:
            status_message += "\n• No pending protocols"
        
        status_message += "\n\n🏥 Asclepius AI System"
        
        await update.message.reply_text(status_message, parse_mode="HTML")
    
    async def help_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command"""
        await self.start_handler(update, context)
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors"""
        logger.error(f"Telegram bot error: {context.error}")
    
    async def _send_approved_protocol_to_nurse(self, patient_id: str, protocol_id: str, doctor_name: str):
        """Send approved protocol implementation to nurse"""
        if not self.nurse_chat_id:
            logger.warning("No nurse chat ID configured")
            return
        
        message = f"""✅ <b>PROTOCOL APPROVED - IMPLEMENT IMMEDIATELY</b>

<b>Patient ID:</b> {patient_id}
<b>Protocol:</b> {protocol_id}
<b>Approved by:</b> {doctor_name}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

🚨 <b>IMMEDIATE ACTIONS REQUIRED:</b>
• Obtain blood cultures before antibiotics (STAT)
• Start broad-spectrum antibiotics within 1 hour
• Administer IV crystalloid 30ml/kg within 3 hours
• Monitor vital signs every 15 minutes
• Consider vasopressor support if MAP &lt; 65 mmHg
• Recheck lactate in 2-4 hours
• Reassess patient status every 30 minutes

<b>⚡ TIME CRITICAL - BEGIN IMPLEMENTATION NOW</b>

🏥 Asclepius AI - ICU Sepsis Early Warning System"""

        await self._send_message_to_chat(self.nurse_chat_id, message)
    
    async def _notify_nurse_protocol_rejected(self, patient_id: str, protocol_id: str, doctor_name: str):
        """Notify nurse that protocol was rejected"""
        if not self.nurse_chat_id:
            return
        
        message = f"""❌ <b>PROTOCOL REJECTED - AWAITING INSTRUCTIONS</b>

<b>Patient ID:</b> {patient_id}
<b>Protocol:</b> {protocol_id}
<b>Rejected by:</b> {doctor_name}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

⏳ <b>PLEASE STANDBY</b>
Doctor is preparing alternative treatment instructions.
Do not implement the original AI protocol.

You will receive updated instructions shortly.

🏥 Asclepius AI - ICU Sepsis Early Warning System"""

        await self._send_message_to_chat(self.nurse_chat_id, message)
    
    async def _send_alternative_instructions_to_nurse(self, patient_id: str, protocol_id: str, instructions: str, doctor_name: str):
        """Send doctor's alternative instructions to nurse"""
        if not self.nurse_chat_id:
            return
        
        message = f"""📝 <b>ALTERNATIVE TREATMENT INSTRUCTIONS</b>

<b>Patient ID:</b> {patient_id}
<b>Rejected Protocol:</b> {protocol_id}
<b>Doctor:</b> {doctor_name}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

👨‍⚕️ <b>DOCTOR'S INSTRUCTIONS:</b>
{instructions}

<b>⚡ IMPLEMENT THESE INSTRUCTIONS INSTEAD OF AI PROTOCOL</b>

🏥 Asclepius AI - ICU Sepsis Early Warning System"""

        await self._send_message_to_chat(self.nurse_chat_id, message)
    
    async def _send_modified_protocol_to_nurse(self, patient_id: str, protocol_id: str, modifications: str, doctor_name: str):
        """Send doctor's protocol modifications to nurse"""
        if not self.nurse_chat_id:
            return
        
        message = f"""✏️ <b>MODIFIED PROTOCOL - IMPLEMENT AS SPECIFIED</b>

<b>Patient ID:</b> {patient_id}
<b>Protocol:</b> {protocol_id}
<b>Modified by:</b> {doctor_name}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

🤖 <b>Base AI Protocol:</b>
• Blood cultures + broad-spectrum antibiotics
• Fluid resuscitation 30ml/kg
• Vasopressor support if indicated
• Enhanced monitoring

👨‍⚕️ <b>DOCTOR'S MODIFICATIONS:</b>
{modifications}

<b>⚡ IMPLEMENT MODIFIED PROTOCOL IMMEDIATELY</b>

🏥 Asclepius AI - ICU Sepsis Early Warning System"""

        await self._send_message_to_chat(self.nurse_chat_id, message)
    
    async def _send_general_note_to_nurse(self, patient_id: str, note: str, doctor_name: str):
        """Send general doctor note to nurse"""
        if not self.nurse_chat_id:
            return
        
        message = f"""📋 <b>DOCTOR'S NOTE</b>

<b>Patient ID:</b> {patient_id}
<b>Doctor:</b> {doctor_name}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

👨‍⚕️ <b>INSTRUCTIONS:</b>
{note}

🏥 Asclepius AI - ICU Sepsis Early Warning System"""

        await self._send_message_to_chat(self.nurse_chat_id, message)
    
    async def _send_message_to_chat(self, chat_id: str, message: str):
        """Send message to specified Telegram chat"""
        if not self.bot_token or not chat_id:
            logger.warning("Telegram not configured - cannot send message")
            return
        
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=data)
                if response.status_code == 200:
                    logger.info(f"Message sent to chat {chat_id}")
                else:
                    logger.error(f"Failed to send message: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
    
    async def _update_protocol_status(self, protocol_id: str, status: str, notes: str):
        """Update protocol status via API call"""
        try:
            # In production, this would call your actual API endpoint
            # For now, we'll just log the action
            logger.info(f"Protocol {protocol_id} updated: status={status}, notes={notes}")
            
            # Uncomment and modify for actual API integration:
            # async with httpx.AsyncClient() as client:
            #     response = await client.patch(
            #         f"http://localhost:8000/protocols/{protocol_id}",
            #         json={"status": status, "doctor_notes": notes}
            #     )
            #     if response.status_code == 200:
            #         logger.info(f"Protocol {protocol_id} updated successfully")
        except Exception as e:
            logger.error(f"Failed to update protocol {protocol_id}: {e}")
    
    def run(self):
        """Start the Telegram bot"""
        if not self.is_configured():
            logger.error("❌ Telegram bot not configured!")
            logger.error("Please set TELEGRAM_BOT_TOKEN, TELEGRAM_NURSE_CHAT_ID, and TELEGRAM_DOCTOR_CHAT_ID in .env file")
            return
        
        logger.info("🚀 Starting Asclepius AI Telegram Bot...")
        
        # Create application
        self.app = ApplicationBuilder().token(self.bot_token).build()
        
        # Add handlers
        self.app.add_handler(CallbackQueryHandler(self.button_handler))
        self.app.add_handler(CommandHandler("note", self.note_handler))
        self.app.add_handler(CommandHandler("start", self.start_handler))
        self.app.add_handler(CommandHandler("status", self.status_handler))
        self.app.add_handler(CommandHandler("help", self.help_handler))
        
        # Add error handler
        self.app.add_error_handler(self.error_handler)
        
        logger.info("✅ Telegram bot configured successfully")
        logger.info(f"📱 Nurse Chat ID: {self.nurse_chat_id}")
        logger.info(f"👨‍⚕️ Doctor Chat ID: {self.doctor_chat_id}")
        
        # Start the bot
        logger.info("🔄 Starting bot polling...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    """Main entry point"""
    bot = AsclepiusTelegramBot()
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot crashed: {e}")
        raise

if __name__ == "__main__":
    main()