"""
Telegram notification service for Asclepius AI
Handles medical alert notifications to healthcare staff
"""
import httpx
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from config import get_settings

logger = logging.getLogger(__name__)

class TelegramService:
    """Enhanced Telegram service for medical notifications"""
    
    def __init__(self):
        settings = get_settings()
        self.bot_token = settings.telegram_bot_token
        self.nurse_chat_id = settings.telegram_nurse_chat_id
        self.doctor_chat_id = settings.telegram_doctor_chat_id
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else ""
        
        # Debug logging to verify configuration
        logger.info(f"🤖 Telegram Bot Token: {'✅ SET' if self.bot_token else '❌ MISSING'}")
        logger.info(f"👩‍⚕️ Nurse Chat ID: {self.nurse_chat_id if self.nurse_chat_id else '❌ MISSING'}")
        logger.info(f"👨‍⚕️ Doctor Chat ID: {self.doctor_chat_id if self.doctor_chat_id else '❌ MISSING'}")
        
        # Medical staff configuration
        self.medical_staff = {
            "nurse": {
                "chat_id": self.nurse_chat_id,
                "role": "Head Nurse",
                "alerts": ["warning", "critical"]
            },
            "doctor": {
                "chat_id": self.doctor_chat_id, 
                "role": "Attending Physician",
                "alerts": ["critical"]
            }
        }
    
    def is_configured(self) -> bool:
        """Check if Telegram is properly configured"""
        configured = bool(self.bot_token and (self.nurse_chat_id or self.doctor_chat_id))
        if not configured:
            logger.warning("⚠️ Telegram not fully configured:")
            if not self.bot_token:
                logger.warning("  - Missing TELEGRAM_BOT_TOKEN")
            if not self.nurse_chat_id:
                logger.warning("  - Missing TELEGRAM_NURSE_CHAT_ID") 
            if not self.doctor_chat_id:
                logger.warning("  - Missing TELEGRAM_DOCTOR_CHAT_ID")
        return configured
    
    async def send_message(self, chat_id: str, message: str, parse_mode: str = "HTML", reply_markup: Dict = None) -> Dict[str, Any]:
        """Send a message to a specific chat"""
        if not self.bot_token:
            logger.warning("📤 No bot token configured - skipping Telegram message")
            return {"status": "error", "message": "No bot token configured"}
            
        if not chat_id:
            logger.warning("📤 No chat ID provided - skipping Telegram message")
            return {"status": "error", "message": "No chat ID provided"}
        
        url = f"{self.base_url}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True
        }
        
        if reply_markup:
            data["reply_markup"] = reply_markup
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=data)
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"✅ Message sent to chat {chat_id}")
                    return {"status": "success", "message_id": result.get("result", {}).get("message_id")}
                else:
                    error_text = response.text
                    logger.error(f"❌ Telegram API error: {response.status_code} - {error_text}")
                    return {
                        "status": "error", 
                        "code": response.status_code,
                        "message": error_text
                    }
                    
        except httpx.TimeoutException:
            logger.error("❌ Telegram request timeout")
            return {"status": "error", "message": "Request timeout"}
        except Exception as e:
            logger.error(f"❌ Telegram error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def send_to_medical_team(self, message: str, level: str = "info", patient_name: str = None) -> Dict[str, Any]:
        """Send message to appropriate medical staff based on alert level"""
        results = {}
        
        for staff_type, config in self.medical_staff.items():
            chat_id = config["chat_id"]
            
            # Send to appropriate staff based on alert level
            if level in config["alerts"] or level == "info":
                if chat_id:
                    # Add role-specific header
                    role_message = f"📱 <b>Alert for {config['role']}</b>\n\n{message}"
                    result = await self.send_message(chat_id, role_message)
                    results[staff_type] = result
                else:
                    results[staff_type] = {"status": "error", "message": f"No {staff_type} chat ID configured"}
        
        return results
    
    async def send_critical_alert(self, patient: Dict[str, Any]) -> Dict[str, Any]:
        """Send critical patient alert to medical team"""
        message = f"""🚨 <b>CRITICAL PATIENT ALERT</b>
        
<b>Patient:</b> {patient.get('name', 'Unknown')} ({patient.get('bed_number', 'N/A')})
<b>Risk Score:</b> {patient.get('current_risk_score', 0):.1f} (CRITICAL)
<b>Diagnosis:</b> {patient.get('diagnosis', 'Not specified')}

<b>Current Vitals:</b>
• Heart Rate: {patient.get('vitals', {}).get('heart_rate', 'N/A')} bpm
• Blood Pressure: {patient.get('vitals', {}).get('systolic_bp', 'N/A')} mmHg  
• Respiratory Rate: {patient.get('vitals', {}).get('respiratory_rate', 'N/A')} br/min
• Temperature: {patient.get('vitals', {}).get('temperature', 'N/A')}°C
• SpO2: {patient.get('vitals', {}).get('spo2', 'N/A')}%
• Lactate: {patient.get('vitals', {}).get('lactate', 'N/A')} mmol/L

<b>🚨 IMMEDIATE INTERVENTION REQUIRED</b>
Review protocol on dashboard immediately!

<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</i>
🏥 Asclepius AI - ICU Sepsis Early Warning System"""

        return await self.send_to_medical_team(message, level="critical", patient_name=patient.get('name'))
    
    async def send_warning_alert(self, patient: Dict[str, Any]) -> Dict[str, Any]:
        """Send warning patient alert to nurses"""
        message = f"""⚠️ <b>WARNING PATIENT ALERT</b>
        
<b>Patient:</b> {patient.get('name', 'Unknown')} ({patient.get('bed_number', 'N/A')})
<b>Risk Score:</b> {patient.get('current_risk_score', 0):.1f} (WARNING)
<b>Diagnosis:</b> {patient.get('diagnosis', 'Not specified')}

<b>Key Vitals:</b>
• Heart Rate: {patient.get('vitals', {}).get('heart_rate', 'N/A')} bpm
• Blood Pressure: {patient.get('vitals', {}).get('systolic_bp', 'N/A')} mmHg
• Temperature: {patient.get('vitals', {}).get('temperature', 'N/A')}°C
• SpO2: {patient.get('vitals', {}).get('spo2', 'N/A')}%

<b>⚠️ INCREASED MONITORING REQUIRED</b>
Please review patient status and vitals.

<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</i>
🏥 Asclepius AI - ICU Sepsis Early Warning System"""

        return await self.send_to_medical_team(message, level="warning", patient_name=patient.get('name'))
    
    async def send_protocol_alert(self, protocol: Dict[str, Any], patient: Dict[str, Any]) -> Dict[str, Any]:
        """Send protocol notification to medical team with action buttons for doctors"""
        message = f"""📋 <b>MEDICAL PROTOCOL GENERATED</b>
        
<b>Patient:</b> {patient.get('name', 'Unknown')} ({patient.get('bed_number', 'N/A')})
<b>Risk Score:</b> {protocol.get('risk_score', 0):.1f}
<b>Protocol Status:</b> {protocol.get('status', 'pending').upper()}

<b>Immediate Actions Required:</b>
{protocol.get('immediate_actions', 'Review dashboard for details')}

<b>📋 REVIEW PROTOCOL ON DASHBOARD</b>
Detailed antibiotic recommendations and rationale available.

<i>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</i>
🏥 Asclepius AI - ICU Sepsis Early Warning System"""

        # Create inline buttons for doctor responses (only for critical alerts)
        doctor_buttons = {
            "inline_keyboard": [
                [
                    {"text": "✅ Approve Protocol", "callback_data": f"approve_{protocol.get('id', 'unknown')}"},
                    {"text": "❌ Reject Protocol", "callback_data": f"reject_{protocol.get('id', 'unknown')}"}
                ],
                [
                    {"text": "✏️ Modify Protocol", "callback_data": f"modify_{protocol.get('id', 'unknown')}"},
                    {"text": "📋 View Details", "callback_data": f"details_{protocol.get('id', 'unknown')}"}
                ]
            ]
        }

        results = {}
        
        for staff_type, config in self.medical_staff.items():
            chat_id = config["chat_id"]
            
            if chat_id and "critical" in config["alerts"]:
                # Add role-specific header
                role_message = f"📱 <b>Alert for {config['role']}</b>\n\n{message}"
                
                # Send with buttons only to doctors
                reply_markup = doctor_buttons if staff_type == "doctor" else None
                result = await self.send_message(chat_id, role_message, reply_markup=reply_markup)
                results[staff_type] = result
            elif chat_id:
                # Send without buttons to nurses
                role_message = f"📱 <b>Alert for {config['role']}</b>\n\n{message}"
                result = await self.send_message(chat_id, role_message)
                results[staff_type] = result
            else:
                results[staff_type] = {"status": "error", "message": f"No {staff_type} chat ID configured"}
        
        return results
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test Telegram bot connection"""
        if not self.bot_token:
            return {"status": "error", "message": "No bot token configured"}
        
        try:
            url = f"{self.base_url}/getMe"
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    bot_info = response.json()
                    return {
                        "status": "success",
                        "bot_info": bot_info.get("result", {}),
                        "message": "Bot connection successful"
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"HTTP {response.status_code}: {response.text}"
                    }
        except Exception as e:
            return {"status": "error", "message": str(e)}

# Global telegram service instance
telegram_service = TelegramService()