"""
Asclepius AI - Direct API Telegram Bot Runner
Uses direct HTTP API calls to avoid python-telegram-bot compatibility issues
"""
import asyncio
import logging
import os
import json
from typing import Dict, Any, Optional
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)

# Import config the same way as telegram_service does
try:
    from config import get_settings
    settings = get_settings()
    BOT_TOKEN = settings.telegram_bot_token
    NURSE_CHAT_ID = settings.telegram_nurse_chat_id
    DOCTOR_CHAT_ID = settings.telegram_doctor_chat_id
except Exception as e:
    logger.warning(f"Could not load config: {e}, falling back to environment variables")
    BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    NURSE_CHAT_ID = os.getenv('TELEGRAM_NURSE_CHAT_ID')
    DOCTOR_CHAT_ID = os.getenv('TELEGRAM_DOCTOR_CHAT_ID')

# Global storage for pending protocols
pending_protocols: Dict[str, Dict[str, Any]] = {}

class DirectTelegramBotRunner:
    """Direct API Telegram bot runner - avoids library compatibility issues"""
    
    def __init__(self):
        self.running = False
        self._polling_task = None
        self.base_url = f"https://api.telegram.org/bot{BOT_TOKEN}" if BOT_TOKEN else ""
        
        # Debug logging
        logger.info(f"🔧 DirectTelegramBotRunner initialized with:")
        logger.info(f"   BOT_TOKEN: {'✅ Set' if BOT_TOKEN else '❌ Missing'}")
        logger.info(f"   NURSE_CHAT_ID: {'✅ ' + str(NURSE_CHAT_ID) if NURSE_CHAT_ID else '❌ Missing'}")
        logger.info(f"   DOCTOR_CHAT_ID: {'✅ ' + str(DOCTOR_CHAT_ID) if DOCTOR_CHAT_ID else '❌ Missing'}")
        
    def is_configured(self):
        """Check if bot is properly configured"""
        configured = bool(BOT_TOKEN and (NURSE_CHAT_ID or DOCTOR_CHAT_ID))
        if not configured:
            logger.warning("❌ Telegram bot not configured:")
            logger.warning(f"   BOT_TOKEN: {'✅ Set' if BOT_TOKEN else '❌ Missing'}")
            logger.warning(f"   NURSE_CHAT_ID: {'✅ Set' if NURSE_CHAT_ID else '❌ Missing'}")
            logger.warning(f"   DOCTOR_CHAT_ID: {'✅ Set' if DOCTOR_CHAT_ID else '❌ Missing'}")
        else:
            logger.info("✅ Telegram bot is properly configured")
        return configured
    
    async def start_bot(self):
        """Start the Telegram bot using direct API"""
        if not self.is_configured():
            logger.warning("🤖 Telegram bot not configured - check .env file")
            return False
            
        try:
            logger.info("🤖 Starting Direct API Telegram bot...")
            
            # Test bot token
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/getMe")
                if response.status_code != 200:
                    logger.error(f"❌ Invalid bot token: {response.text}")
                    return False
                
                bot_info = response.json().get("result", {})
                logger.info(f"✅ Bot token valid: @{bot_info.get('username', 'Unknown')}")
            
            # Start polling
            self.running = True
            self._polling_task = asyncio.create_task(self._direct_polling())
            
            logger.info("✅ Direct API Telegram bot started successfully")
            logger.info(f"📱 Nurse Chat ID: {NURSE_CHAT_ID}")
            logger.info(f"👨‍⚕️ Doctor Chat ID: {DOCTOR_CHAT_ID}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start Telegram bot: {e}")
            self.running = False
            return False
    
    async def _direct_polling(self):
        """Direct API polling without using python-telegram-bot Application"""
        logger.info("🔄 Starting direct API polling...")
        offset = 0
        consecutive_errors = 0
        
        while self.running:
            try:
                params = {
                    "offset": offset,
                    "timeout": 10,
                    "allowed_updates": ["message", "callback_query"]
                }
                
                async with httpx.AsyncClient(timeout=15.0) as client:
                    response = await client.get(f"{self.base_url}/getUpdates", params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("ok"):
                            updates = data.get("result", [])
                            
                            for update_data in updates:
                                try:
                                    await self._process_update(update_data)
                                    offset = update_data.get("update_id", 0) + 1
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
    
    async def _process_update(self, update_data: dict):
        """Process incoming update"""
        update_id = update_data.get("update_id")
        
        # Handle callback queries (button clicks)
        if "callback_query" in update_data:
            await self._handle_callback_query(update_data["callback_query"])
            
        # Handle messages (commands)
        elif "message" in update_data:
            await self._handle_message(update_data["message"])
    
    async def _handle_callback_query(self, query_data: dict):
        """Handle button clicks"""
        query_id = query_data.get("id")
        callback_data = query_data.get("data", "")
        message = query_data.get("message", {})
        user = query_data.get("from", {})
        
        logger.info(f"📱 Button clicked: '{callback_data}'")
        
        # Answer the callback query
        await self._answer_callback_query(query_id)
        
        # Parse callback data
        parts = callback_data.split("_")
        if len(parts) < 3:
            await self._edit_message(message, "⚠️ Invalid button format")
            return

        action, protocol_id, patient_id = parts[0], parts[1], parts[2]
        doctor_name = user.get("first_name", "") + " " + user.get("last_name", "")
        doctor_name = doctor_name.strip() or user.get("username", f"Doctor_{user.get('id', '')}")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        if action == "approve":
            new_text = f"""✅ <b>PROTOCOL APPROVED</b>

<b>Patient:</b> {patient_id}
<b>Protocol:</b> {protocol_id}
<b>Approved by:</b> Dr. {doctor_name}
<b>Time:</b> {timestamp}

✅ <b>Implementation instructions sent to nurse</b>"""
            
            await self._edit_message(message, new_text)
            await self._send_approved_protocol(patient_id, protocol_id, doctor_name)
            
        elif action == "reject":
            new_text = f"""❌ <b>PROTOCOL REJECTED</b>

<b>Patient:</b> {patient_id}
<b>Protocol:</b> {protocol_id}
<b>Rejected by:</b> Dr. {doctor_name}
<b>Time:</b> {timestamp}

📝 <b>Please provide alternative instructions:</b>
<code>/note {patient_id} your_instructions</code>"""
            
            await self._edit_message(message, new_text)
            pending_protocols[patient_id] = {
                "action": "rejected", "protocol_id": protocol_id,
                "doctor_name": doctor_name, "timestamp": timestamp
            }
            await self._notify_nurse_rejected(patient_id, protocol_id, doctor_name)
            
        elif action == "modify":
            new_text = f"""✏️ <b>PROTOCOL MODIFICATION REQUESTED</b>

<b>Patient:</b> {patient_id}
<b>Protocol:</b> {protocol_id}
<b>Requested by:</b> Dr. {doctor_name}
<b>Time:</b> {timestamp}

📝 <b>Please specify modifications:</b>
<code>/note {patient_id} your_modifications</code>"""
            
            await self._edit_message(message, new_text)
            pending_protocols[patient_id] = {
                "action": "modify", "protocol_id": protocol_id,
                "doctor_name": doctor_name, "timestamp": timestamp
            }
    
    async def _handle_message(self, message_data: dict):
        """Handle text messages and commands"""
        text = message_data.get("text", "")
        chat_id = message_data.get("chat", {}).get("id")
        user = message_data.get("from", {})
        
        if text.startswith("/"):
            await self._handle_command(text, chat_id, user)
    
    async def _handle_command(self, text: str, chat_id: int, user: dict):
        """Handle commands"""
        parts = text.split()
        command = parts[0].lower()
        
        if command == "/start":
            await self._handle_start_command(chat_id, user)
        elif command == "/status":
            await self._handle_status_command(chat_id)
        elif command == "/note":
            await self._handle_note_command(parts[1:], chat_id, user)
    
    async def _handle_start_command(self, chat_id: int, user: dict):
        """Handle /start command"""
        user_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
        user_name = user_name or user.get('username', 'Unknown')
        
        role = "👨‍⚕️ Doctor" if str(chat_id) == DOCTOR_CHAT_ID else "👩‍⚕️ Nurse" if str(chat_id) == NURSE_CHAT_ID else "❓ Unknown"
        
        message = f"""🏥 <b>Asclepius AI - ICU Sepsis Early Warning System</b>

🤖 <b>Production Medical Alert Bot</b>

<b>User:</b> {user_name}
<b>Role:</b> {role}
<b>Chat ID:</b> <code>{chat_id}</code>

<b>Commands:</b>
• <code>/note PAT001 instructions</code> - Send medical instructions
• <code>/status</code> - Check system status

<b>System Status:</b> ✅ Production mode active"""

        await self._send_message(chat_id, message)
    
    async def _handle_status_command(self, chat_id: int):
        """Handle /status command"""
        pending_count = len(pending_protocols)
        
        status = f"""📊 <b>Bot Status Report</b>

<b>Status:</b> ✅ Online (Direct API Mode)
<b>Pending Protocols:</b> {pending_count}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

<b>Configuration:</b>
• Nurse Chat: {'✅' if NURSE_CHAT_ID else '❌'}
• Doctor Chat: {'✅' if DOCTOR_CHAT_ID else '❌'}

<b>Mode:</b> Direct HTTP API (No library compatibility issues)"""
        
        await self._send_message(chat_id, status)
    
    async def _handle_note_command(self, args: list, chat_id: int, user: dict):
        """Handle /note command"""
        if len(args) < 2:
            await self._send_message(chat_id, "Usage: /note <patient_id> <instructions>")
            return

        patient_id = args[0]
        instructions = " ".join(args[1:])
        doctor_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
        doctor_name = doctor_name or user.get('username', f"Doctor_{user.get('id', '')}")
        
        if patient_id in pending_protocols:
            info = pending_protocols[patient_id]
            if info["action"] == "rejected":
                await self._send_alternative_instructions(patient_id, info["protocol_id"], instructions, doctor_name)
            elif info["action"] == "modify":
                await self._send_modified_protocol(patient_id, info["protocol_id"], instructions, doctor_name)
            del pending_protocols[patient_id]
        else:
            await self._send_general_instructions(patient_id, instructions, doctor_name)

        await self._send_message(chat_id, f"✅ Instructions sent to nursing staff\nPatient: {patient_id}")
    
    async def stop_bot(self):
        """Stop the bot"""
        if self.running:
            logger.info("🛑 Stopping Direct API Telegram bot...")
            self.running = False
            
            if self._polling_task:
                self._polling_task.cancel()
                try:
                    await self._polling_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("✅ Direct API Telegram bot stopped")
    
    # Helper methods for API calls
    async def _send_message(self, chat_id: int, text: str):
        """Send message via direct API"""
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(f"{self.base_url}/sendMessage", json=data)
                if response.status_code == 200:
                    logger.info(f"✅ Message sent to {chat_id}")
                else:
                    logger.error(f"❌ Failed to send message: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Send message error: {e}")
    
    async def _edit_message(self, message: dict, new_text: str):
        """Edit message via direct API"""
        data = {
            "chat_id": message.get("chat", {}).get("id"),
            "message_id": message.get("message_id"),
            "text": new_text,
            "parse_mode": "HTML"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(f"{self.base_url}/editMessageText", json=data)
                if response.status_code != 200:
                    logger.error(f"❌ Failed to edit message: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Edit message error: {e}")
    
    async def _answer_callback_query(self, query_id: str):
        """Answer callback query"""
        data = {"callback_query_id": query_id}
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(f"{self.base_url}/answerCallbackQuery", json=data)
        except Exception as e:
            logger.warning(f"Callback answer error: {e}")
    
    # Nurse notification methods
    async def _send_approved_protocol(self, patient_id: str, protocol_id: str, doctor_name: str):
        """Send approved protocol to nurse"""
        if not NURSE_CHAT_ID:
            return
            
        message = f"""✅ <b>PROTOCOL APPROVED - IMPLEMENT NOW</b>

<b>Patient:</b> {patient_id}
<b>Protocol:</b> {protocol_id}
<b>Approved by:</b> Dr. {doctor_name}

🚨 <b>SEPSIS PROTOCOL:</b>
• Blood cultures (STAT)
• Broad-spectrum antibiotics within 1 hour
• IV fluids 30ml/kg within 3 hours
• Monitor vitals q15min
• Vasopressors if MAP &lt; 65 mmHg

⚡ <b>BEGIN IMPLEMENTATION IMMEDIATELY</b>"""

        await self._send_message(int(NURSE_CHAT_ID), message)

    async def _notify_nurse_rejected(self, patient_id: str, protocol_id: str, doctor_name: str):
        """Notify nurse of rejection"""
        if not NURSE_CHAT_ID:
            return
            
        message = f"""❌ <b>PROTOCOL REJECTED - STANDBY</b>

<b>Patient:</b> {patient_id}
<b>Protocol:</b> {protocol_id}
<b>Rejected by:</b> Dr. {doctor_name}

⏳ <b>DO NOT IMPLEMENT AI PROTOCOL</b>
Wait for alternative instructions."""

        await self._send_message(int(NURSE_CHAT_ID), message)

    async def _send_alternative_instructions(self, patient_id: str, protocol_id: str, instructions: str, doctor_name: str):
        """Send alternative instructions"""
        if not NURSE_CHAT_ID:
            return
            
        message = f"""📝 <b>ALTERNATIVE TREATMENT ORDERS</b>

<b>Patient:</b> {patient_id}
<b>Doctor:</b> Dr. {doctor_name}

👨‍⚕️ <b>ORDERS:</b>
{instructions}

⚡ <b>IMPLEMENT THESE ORDERS IMMEDIATELY</b>"""

        await self._send_message(int(NURSE_CHAT_ID), message)

    async def _send_modified_protocol(self, patient_id: str, protocol_id: str, modifications: str, doctor_name: str):
        """Send modified protocol"""
        if not NURSE_CHAT_ID:
            return
            
        message = f"""✏️ <b>MODIFIED PROTOCOL</b>

<b>Patient:</b> {patient_id}
<b>Modified by:</b> Dr. {doctor_name}

<b>Modifications:</b>
{modifications}

⚡ <b>IMPLEMENT MODIFIED PROTOCOL</b>"""

        await self._send_message(int(NURSE_CHAT_ID), message)

    async def _send_general_instructions(self, patient_id: str, instructions: str, doctor_name: str):
        """Send general instructions"""
        if not NURSE_CHAT_ID:
            return
            
        message = f"""📋 <b>DOCTOR'S INSTRUCTIONS</b>

<b>Patient:</b> {patient_id}
<b>Doctor:</b> Dr. {doctor_name}

<b>Instructions:</b>
{instructions}"""

        await self._send_message(int(NURSE_CHAT_ID), message)

    async def send_critical_alert(self, patient: dict, protocol_id: str = None):
        """Send critical alert to doctor with buttons"""
        if not DOCTOR_CHAT_ID:
            logger.warning("No doctor chat ID configured for critical alert")
            return
            
        # Generate protocol ID if not provided
        if not protocol_id:
            protocol_id = f"SEPSIS_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
        patient_id = patient.get('patient_id', patient.get('name', '').replace(' ', '_'))
        
        # Create critical alert message
        message = f"""🔴 <b>CRITICAL ALERT - Doctor Action Required</b>

👤 <b>Patient:</b> {patient.get('name', 'Unknown')}
🛏️ <b>Bed:</b> {patient.get('bed_number', 'N/A')}
🚨 <b>Risk Score:</b> {patient.get('current_risk_score', 0):.1f}/100
📊 <b>Risk Factors:</b> {patient.get('risk_factors', 'Multiple critical indicators')}

📋 <b>AI-Generated Protocol available</b>
Click button below to review full protocol

⚠️ <b>You can:</b>
✅ <b>APPROVE</b> - Execute AI protocol as-is
❌ <b>REJECT</b> - Request alternative approach
✏️ <b>MODIFY</b> - Adjust protocol and send to nurse

<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
🏥 <i>Asclepius AI - ICU Sepsis Early Warning System</i>"""

        # Create buttons
        buttons = {
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
        
        # Send message with buttons
        await self._send_message_with_buttons(int(DOCTOR_CHAT_ID), message, buttons)
    
    async def _send_message_with_buttons(self, chat_id: int, text: str, buttons: dict):
        """Send message with inline keyboard buttons"""
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
            "reply_markup": buttons
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(f"{self.base_url}/sendMessage", json=data)
                if response.status_code == 200:
                    result = response.json().get("result", {})
                    logger.info(f"✅ Message with buttons sent to {chat_id}")
                    return result.get("message_id")
                else:
                    logger.error(f"❌ Failed to send message with buttons: {response.status_code}")
                    logger.error(f"Response: {response.text}")
        except Exception as e:
            logger.error(f"❌ Send message with buttons error: {e}")

# Global instance
telegram_bot_runner = DirectTelegramBotRunner()