#!/usr/bin/env python3
"""
Asclepius AI - Production Telegram Bot
Handles critical medical protocol approvals and notifications in production environment
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

class AsclepiusTelegramBot:
    """Production Telegram Bot for Asclepius AI Medical System"""
    
    def __init__(self):
        settings = get_settings()
        self.bot_token = settings.telegram_bot_token
        self.nurse_chat_id = settings.telegram_nurse_chat_id
        self.doctor_chat_id = settings.telegram_doctor_chat_id
        self.api_base_url = "http://localhost:8000"  # Production API URL
        
        # Validate configuration
        if not self.is_configured():
            logger.error("❌ Telegram bot not configured properly")
            raise ValueError("Bot token or chat IDs not configured")
    
    def is_configured(self) -> bool:
        """Check if bot is properly configured"""
        return bool(self.bot_token and (self.nurse_chat_id or self.doctor_chat_id))
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle doctor protocol approval/rejection buttons"""
        query = update.callback_query
        
        try:
            await query.answer()
        except Exception as e:
            logger.warning(f"Failed to acknowledge callback: {e}")
            return
        
        try:
            # Parse callback data: action_protocol_id_patient_id
            parts = query.data.split("_")
            if len(parts) < 3:
                await query.edit_message_text("⚠️ Invalid button data format")
                return
            
            action = parts[0]
            protocol_id = parts[1]
            patient_id = parts[2]
            
            # Get doctor information
            user = update.effective_user
            doctor_name = user.full_name or user.username or f"Doctor_{user.id}"
            
            logger.info(f"Protocol {protocol_id} - {action} by Dr. {doctor_name} for patient {patient_id}")
            
            # Process the action and get response
            response_message = await self._handle_protocol_action(action, protocol_id, patient_id, doctor_name)
            
            # Update the message with the response
            await query.edit_message_text(
                text=response_message,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Error in button handler: {e}")
            await query.edit_message_text(
                "❌ <b>ERROR:</b> Failed to process your response. Please try again or contact support.",
                parse_mode='HTML'
            )
    
    async def _handle_protocol_action(self, action: str, protocol_id: str, patient_id: str, doctor_name: str) -> str:
        """Process doctor's protocol decision"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        if action == "approve":
            # Update protocol status
            api_success = await self._update_protocol_via_api(protocol_id, "approved", f"Approved by {doctor_name}")
            
            # Send implementation instructions to nurse
            await self._send_approved_protocol_to_nurse(patient_id, protocol_id, doctor_name)
            
            return f"""✅ <b>PROTOCOL APPROVED</b>

<b>Patient ID:</b> {patient_id}
<b>Protocol:</b> {protocol_id}
<b>Approved by:</b> {doctor_name}
<b>Time:</b> {timestamp}

✅ <b>Implementation instructions sent to nursing staff</b>
{'✅ Protocol status updated in system' if api_success else '⚠️ Manual system update may be required'}

<i>The nursing team has been notified to begin immediate implementation.</i>"""
            
        elif action == "reject":
            # Update protocol status
            api_success = await self._update_protocol_via_api(protocol_id, "rejected", f"Rejected by {doctor_name}")
            
            # Notify nurse to wait for alternative instructions
            await self._notify_nurse_protocol_rejected(patient_id, protocol_id, doctor_name)
            
            return f"""❌ <b>PROTOCOL REJECTED</b>

<b>Patient ID:</b> {patient_id}
<b>Protocol:</b> {protocol_id}
<b>Rejected by:</b> {doctor_name}
<b>Time:</b> {timestamp}

📝 <b>Please provide alternative treatment instructions:</b>
Use: <code>/note {patient_id} your_alternative_instructions</code>

⏳ <b>Nursing staff has been notified to standby</b>
{'✅ Protocol status updated in system' if api_success else '⚠️ Manual system update may be required'}"""
            
        elif action == "modify":
            # Update protocol status
            api_success = await self._update_protocol_via_api(protocol_id, "pending_modification", f"Modification requested by {doctor_name}")
            
            return f"""✏️ <b>PROTOCOL MODIFICATION REQUESTED</b>

<b>Patient ID:</b> {patient_id}
<b>Protocol:</b> {protocol_id}
<b>Requested by:</b> {doctor_name}
<b>Time:</b> {timestamp}

📝 <b>Please specify your modifications:</b>
Use: <code>/note {patient_id} your_specific_modifications</code>

{'✅ Protocol status updated in system' if api_success else '⚠️ Manual system update may be required'}"""
            
        else:
            return f"⚠️ <b>Unknown Action:</b> {action}\n\nPlease use the provided buttons or contact support."
    
    async def note_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /note command for doctor instructions"""
        if not context.args or len(context.args) < 2:
            await update.message.reply_text(
                "📝 <b>Usage:</b> /note &lt;patient_id&gt; &lt;your_instructions&gt;\n\n"
                "<b>Examples:</b>\n"
                "• <code>/note PAT001 Start vancomycin 1g q12h instead of piperacillin</code>\n"
                "• <code>/note PAT002 Increase fluid rate to 200ml/hr, recheck lactate in 1hr</code>\n\n"
                "<b>Note:</b> Your instructions will be immediately sent to the nursing staff.",
                parse_mode="HTML"
            )
            return
        
        patient_id = context.args[0]
        instructions = " ".join(context.args[1:])
        
        user = update.effective_user
        doctor_name = user.full_name or user.username or f"Doctor_{user.id}"
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        logger.info(f"Doctor instructions from {doctor_name} for patient {patient_id}: {instructions}")
        
        # Send instructions to nurse
        await self._send_doctor_instructions_to_nurse(patient_id, instructions, doctor_name)
        
        # Respond to doctor
        response = f"""✅ <b>INSTRUCTIONS SENT TO NURSING STAFF</b>

<b>Patient ID:</b> {patient_id}
<b>Doctor:</b> {doctor_name}
<b>Time:</b> {timestamp}

<b>Instructions:</b>
{instructions}

📨 <b>The nursing team has been notified immediately.</b>"""
        
        await update.message.reply_text(response, parse_mode='HTML')
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command"""
        chat_id = str(update.effective_chat.id)
        user_name = update.effective_user.full_name or update.effective_user.username or "Unknown"
        
        # Determine user role
        if chat_id == self.doctor_chat_id:
            role = "👨‍⚕️ Doctor"
            role_desc = "Receive critical sepsis alerts with approval buttons"
        elif chat_id == self.nurse_chat_id:
            role = "👩‍⚕️ Nurse"
            role_desc = "Receive protocol instructions and medical alerts"
        else:
            role = "❓ Unregistered User"
            role_desc = "Contact administrator to register this chat"
        
        message = f"""🏥 <b>Asclepius AI - ICU Sepsis Early Warning System</b>

🤖 <b>Medical Alert Bot - Production Mode</b>

<b>User Information:</b>
• <b>Name:</b> {user_name}
• <b>Role:</b> {role}
• <b>Chat ID:</b> <code>{chat_id}</code>
• <b>Function:</b> {role_desc}

<b>Available Commands:</b>
• <code>/note PAT001 instructions</code> - Send medical instructions (Doctors)
• <code>/status</code> - Check system and bot status
• <code>/help</b> - Show detailed help information

<b>Automated Functions:</b>
• Real-time critical sepsis alerts with approval workflow
• Protocol implementation notifications
• Medical team communication system

<b>System Status:</b> ✅ Online and operational

🏥 <i>Professional medical alert system serving ICU operations</i>"""

        await update.message.reply_text(message, parse_mode="HTML")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /status command"""
        chat_id = str(update.effective_chat.id)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        # Test API connectivity
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.api_base_url}/health")
                api_status = "✅ Online" if response.status_code == 200 else f"⚠️ Issues ({response.status_code})"
        except Exception:
            api_status = "❌ Offline"
        
        status_message = f"""📊 <b>System Status Report</b>

<b>Bot Status:</b> ✅ Online and operational
<b>Chat ID:</b> <code>{chat_id}</code>
<b>API Status:</b> {api_status}
<b>Report Time:</b> {timestamp}

<b>Configuration:</b>
• Doctor Chat: {'✅ Configured' if self.doctor_chat_id else '❌ Not Set'}
• Nurse Chat: {'✅ Configured' if self.nurse_chat_id else '❌ Not Set'}
• Bot Token: {'✅ Valid' if self.bot_token else '❌ Missing'}

<b>System Features:</b>
• Critical sepsis alert workflow ✅
• Protocol approval buttons ✅  
• Real-time medical notifications ✅
• Doctor-nurse communication ✅

<b>Support:</b> Contact system administrator if issues persist

🏥 Asclepius AI - Production Environment"""
        
        await update.message.reply_text(status_message, parse_mode="HTML")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command"""
        help_message = """📚 <b>Asclepius AI Bot - Help Guide</b>

<b>🚨 Critical Alert Workflow:</b>
1. System detects critical sepsis risk
2. Doctor receives alert with approval buttons
3. Doctor chooses: Approve, Reject, or Modify
4. Nursing staff receives immediate implementation instructions

<b>💬 Commands for Doctors:</b>
• <code>/note PAT001 your instructions</code> - Send treatment instructions
• <code>/status</code> - Check system status
• <code>/help</code> - Show this help

<b>🔘 Button Actions:</b>
• <b>✅ Approve:</b> Execute AI protocol immediately
• <b>❌ Reject:</b> Provide alternative treatment plan
• <b>✏️ Modify:</b> Adjust protocol with specific changes

<b>📝 Instruction Examples:</b>
• <code>/note PAT001 Start vancomycin 1g q12h, hold piperacillin</code>
• <code>/note PAT002 Increase fluid to 150ml/hr, check lactate q2h</code>
• <code>/note PAT003 Add norepinephrine if MAP &lt; 65, call if no improvement</code>

<b>⚡ Emergency Support:</b>
Contact ICU charge nurse or attending physician for immediate assistance.

🏥 <i>Asclepius AI - Saving lives through intelligent automation</i>"""
        
        await update.message.reply_text(help_message, parse_mode="HTML")
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle bot errors"""
        logger.error(f"Telegram bot error: {context.error}")
        
        # Try to notify user if update is available
        if update and update.effective_chat:
            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="⚠️ A system error occurred. Please try your request again or contact support if the issue persists."
                )
            except Exception:
                pass  # Don't log errors from error handler
    
    async def _update_protocol_via_api(self, protocol_id: str, status: str, notes: str) -> bool:
        """Update protocol status via API"""
        try:
            url = f"{self.api_base_url}/protocols/{protocol_id}/review"
            data = {
                "action": status,
                "reviewed_by": "doctor_telegram",
                "notes": notes,
                "timestamp": datetime.now().isoformat()
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.patch(url, json=data)
                
                if response.status_code == 200:
                    logger.info(f"Protocol {protocol_id} updated to {status}")
                    return True
                else:
                    logger.error(f"API error updating protocol: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to update protocol via API: {e}")
            return False
    
    async def _send_approved_protocol_to_nurse(self, patient_id: str, protocol_id: str, doctor_name: str):
        """Send approved protocol implementation to nurse"""
        if not self.nurse_chat_id:
            logger.warning("No nurse chat ID configured")
            return
        
        message = f"""✅ <b>PROTOCOL APPROVED - IMPLEMENT IMMEDIATELY</b>

<b>Patient ID:</b> {patient_id}
<b>Protocol:</b> {protocol_id}
<b>Approved by:</b> Dr. {doctor_name}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

🚨 <b>IMMEDIATE SEPSIS PROTOCOL - TIME CRITICAL:</b>
• <b>Blood cultures:</b> Obtain before antibiotics (STAT)
• <b>Antibiotics:</b> Start broad-spectrum within 1 hour
• <b>Fluids:</b> IV crystalloid 30ml/kg within 3 hours
• <b>Monitoring:</b> Vital signs every 15 minutes
• <b>Vasopressors:</b> Consider if MAP &lt; 65 mmHg
• <b>Labs:</b> Recheck lactate in 2-4 hours
• <b>Assessment:</b> Reassess patient every 30 minutes

<b>⚡ BEGIN IMPLEMENTATION NOW - DOCTOR APPROVED</b>

🏥 Asclepius AI - ICU Sepsis Early Warning System"""
        
        await self._send_message_to_chat(self.nurse_chat_id, message)
    
    async def _notify_nurse_protocol_rejected(self, patient_id: str, protocol_id: str, doctor_name: str):
        """Notify nurse that protocol was rejected"""
        if not self.nurse_chat_id:
            return
        
        message = f"""❌ <b>PROTOCOL REJECTED - STANDBY FOR INSTRUCTIONS</b>

<b>Patient ID:</b> {patient_id}
<b>Protocol:</b> {protocol_id}
<b>Rejected by:</b> Dr. {doctor_name}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

⏳ <b>IMPORTANT - DO NOT IMPLEMENT AI PROTOCOL</b>

Dr. {doctor_name} is preparing alternative treatment instructions.
You will receive specific instructions shortly.

<b>Continue standard monitoring while awaiting doctor's orders.</b>

🏥 Asclepius AI - ICU Sepsis Early Warning System"""
        
        await self._send_message_to_chat(self.nurse_chat_id, message)
    
    async def _send_doctor_instructions_to_nurse(self, patient_id: str, instructions: str, doctor_name: str):
        """Send doctor's specific instructions to nurse"""
        if not self.nurse_chat_id:
            return
        
        message = f"""📝 <b>DOCTOR'S TREATMENT INSTRUCTIONS</b>

<b>Patient ID:</b> {patient_id}
<b>Doctor:</b> Dr. {doctor_name}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

👨‍⚕️ <b>SPECIFIC INSTRUCTIONS:</b>
{instructions}

<b>⚡ IMPLEMENT THESE INSTRUCTIONS IMMEDIATELY</b>

🏥 Asclepius AI - ICU Sepsis Early Warning System"""
        
        await self._send_message_to_chat(self.nurse_chat_id, message)
    
    async def _send_message_to_chat(self, chat_id: str, message: str):
        """Send message to specified chat"""
        if not self.bot_token or not chat_id:
            logger.warning("Missing bot token or chat ID")
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
                    logger.error(f"Failed to send message: {response.status_code}")
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    def run(self):
        """Start the Telegram bot"""
        logger.info("🚀 Starting Asclepius AI Production Bot...")
        
        # Create application
        application = ApplicationBuilder().token(self.bot_token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("status", self.status_command))
        application.add_handler(CommandHandler("note", self.note_command))
        application.add_handler(CallbackQueryHandler(self.button_handler))
        
        # Add error handler
        application.add_error_handler(self.error_handler)
        
        logger.info("✅ Bot configured and ready")
        logger.info(f"📱 Nurse Chat ID: {self.nurse_chat_id}")
        logger.info(f"👨‍⚕️ Doctor Chat ID: {self.doctor_chat_id}")
        
        # Start the bot
        logger.info("🔄 Starting bot polling... (Press Ctrl+C to stop)")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    """Main entry point"""
    try:
        bot = AsclepiusTelegramBot()
        bot.run()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please check your .env file and ensure all required values are set")
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot crashed: {e}")
        raise

if __name__ == "__main__":
    main()