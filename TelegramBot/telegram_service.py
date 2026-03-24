#!/usr/bin/env python3
"""
Asclepius AI - Production Telegram Service
Handles medical alert notifications without demo mode
"""
import httpx
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import sys

# Add server directory to path for imports
server_path = Path(__file__).parent.parent / "server"
sys.path.insert(0, str(server_path))

from config import get_settings

logger = logging.getLogger(__name__)

class TelegramService:
    """Production Telegram service for medical alert notifications"""
    
    def __init__(self):
        settings = get_settings()
        self.bot_token = settings.telegram_bot_token
        self.nurse_chat_id = settings.telegram_nurse_chat_id
        self.doctor_chat_id = settings.telegram_doctor_chat_id
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else ""
        
        # Validate configuration
        if not self.is_configured():
            logger.warning("⚠️ Telegram service not fully configured")
    
    def is_configured(self) -> bool:
        """Check if Telegram is properly configured"""
        return bool(self.bot_token and (self.nurse_chat_id or self.doctor_chat_id))
    
    async def send_critical_alert(self, patient: Dict[str, Any]) -> Dict[str, Any]:
        """Send critical sepsis alert with doctor approval workflow"""
        if not self.is_configured():
            logger.error("Telegram not configured - cannot send critical alert")
            return {"status": "error", "message": "Telegram not configured"}
        
        patient_id = patient.get('id', 'UNKNOWN')
        patient_name = patient.get('name', 'Unknown Patient')
        bed_number = patient.get('bed_number', 'N/A')
        risk_score = patient.get('current_risk_score', 0)
        diagnosis = patient.get('diagnosis', 'Not specified')
        
        # Generate unique protocol ID
        protocol_id = f"PROTO_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Get vitals data
        vitals = patient.get('vitals', {})
        hr = vitals.get('heart_rate', 'N/A')
        bp = vitals.get('systolic_bp', 'N/A')
        rr = vitals.get('respiratory_rate', 'N/A')
        temp = vitals.get('temperature', 'N/A')
        spo2 = vitals.get('spo2', 'N/A')
        lactate = vitals.get('lactate', 'N/A')
        
        # Send alert to nurse first (status update)
        nurse_message = f"""🔴 <b>CRITICAL SEPSIS ALERT</b>

<b>Patient:</b> {patient_name} (Bed {bed_number})
<b>Risk Score:</b> {risk_score:.1f}/100 - CRITICAL
<b>Diagnosis:</b> {diagnosis}

<b>Critical Vitals:</b>
• Heart Rate: {hr} bpm
• Blood Pressure: {bp} mmHg
• Respiratory Rate: {rr} br/min
• Temperature: {temp}°C
• SpO2: {spo2}%
• Lactate: {lactate} mmol/L

⏳ <b>STATUS:</b> AI protocol generated - Doctor reviewing
👨‍⚕️ <b>ACTION:</b> Standby for doctor's decision

<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</i>
🏥 Asclepius AI - ICU Sepsis Early Warning System"""

        # Send alert to doctor with approval buttons
        doctor_message = f"""🚨 <b>CRITICAL ALERT - IMMEDIATE DOCTOR ACTION REQUIRED</b>

<b>Patient:</b> {patient_name} (Bed {bed_number})
<b>Patient ID:</b> {patient_id}
<b>Risk Score:</b> {risk_score:.1f}/100 - CRITICAL
<b>Diagnosis:</b> {diagnosis}

<b>Critical Findings:</b>
• Heart Rate: {hr} bpm
• Blood Pressure: {bp} mmHg
• Temperature: {temp}°C
• SpO2: {spo2}%
• Lactate: {lactate} mmol/L

🤖 <b>AI SEPSIS PROTOCOL READY</b>
• Blood cultures (STAT before antibiotics)
• Broad-spectrum antibiotics within 1 hour
• IV crystalloid 30ml/kg within 3 hours
• Vasopressor support if MAP &lt; 65 mmHg
• Enhanced monitoring q15min

<b>⚡ CHOOSE ACTION:</b>

<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</i>
🏥 Asclepius AI - ICU Sepsis Early Warning System"""

        # Create approval buttons for doctor
        doctor_buttons = {
            "inline_keyboard": [
                [
                    {"text": "✅ Approve Protocol", "callback_data": f"approve_{protocol_id}_{patient_id}"},
                    {"text": "❌ Reject Protocol", "callback_data": f"reject_{protocol_id}_{patient_id}"}
                ],
                [
                    {"text": "✏️ Modify Protocol", "callback_data": f"modify_{protocol_id}_{patient_id}"}
                ]
            ]
        }

        results = {}
        
        # Send to nurse (no buttons)
        if self.nurse_chat_id:
            nurse_result = await self._send_message(self.nurse_chat_id, nurse_message)
            results["nurse"] = nurse_result
        
        # Send to doctor with buttons
        if self.doctor_chat_id:
            doctor_result = await self._send_message(self.doctor_chat_id, doctor_message, buttons=doctor_buttons)
            results["doctor"] = doctor_result
        
        logger.info(f"Critical alert sent for patient {patient_id} (Protocol: {protocol_id})")
        return results
    
    async def send_warning_alert(self, patient: Dict[str, Any]) -> Dict[str, Any]:
        """Send warning alert to nurse only (no doctor approval needed)"""
        if not self.is_configured():
            logger.error("Telegram not configured - cannot send warning alert")
            return {"status": "error", "message": "Telegram not configured"}
        
        patient_name = patient.get('name', 'Unknown Patient')
        bed_number = patient.get('bed_number', 'N/A')
        risk_score = patient.get('current_risk_score', 0)
        diagnosis = patient.get('diagnosis', 'Not specified')
        
        vitals = patient.get('vitals', {})
        hr = vitals.get('heart_rate', 'N/A')
        bp = vitals.get('systolic_bp', 'N/A')
        temp = vitals.get('temperature', 'N/A')
        spo2 = vitals.get('spo2', 'N/A')
        
        message = f"""⚠️ <b>WARNING ALERT - Elevated Sepsis Risk</b>

<b>Patient:</b> {patient_name} (Bed {bed_number})
<b>Risk Score:</b> {risk_score:.1f}/100 - ELEVATED
<b>Diagnosis:</b> {diagnosis}

<b>Key Vitals:</b>
• Heart Rate: {hr} bpm
• Blood Pressure: {bp} mmHg
• Temperature: {temp}°C
• SpO2: {spo2}%

⚠️ <b>ENHANCED MONITORING RECOMMENDED</b>
• Increase vital sign checks to every 2 hours
• Monitor for signs of clinical deterioration
• Consider more frequent laboratory assessments
• Escalate to doctor if condition worsens

<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</i>
🏥 Asclepius AI - ICU Sepsis Early Warning System"""

        result = {}
        if self.nurse_chat_id:
            nurse_result = await self._send_message(self.nurse_chat_id, message)
            result["nurse"] = nurse_result
            logger.info(f"Warning alert sent for patient {patient.get('id', 'unknown')}")
        else:
            result["nurse"] = {"status": "error", "message": "No nurse chat ID configured"}
        
        return result
    
    async def send_protocol_update(self, protocol_id: str, patient_id: str, status: str, notes: str = "") -> Dict[str, Any]:
        """Send protocol status update to medical team"""
        if not self.is_configured():
            return {"status": "error", "message": "Telegram not configured"}
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        if status == "approved":
            emoji = "✅"
            title = "PROTOCOL APPROVED"
            action_text = "Implementation authorized - Begin treatment immediately"
        elif status == "rejected":
            emoji = "❌"
            title = "PROTOCOL REJECTED"
            action_text = "Alternative treatment plan required"
        elif status == "modified":
            emoji = "✏️"
            title = "PROTOCOL MODIFIED"
            action_text = "Implement modified protocol as specified"
        else:
            emoji = "ℹ️"
            title = "PROTOCOL UPDATE"
            action_text = "Status updated"
        
        message = f"""{emoji} <b>{title}</b>

<b>Patient ID:</b> {patient_id}
<b>Protocol:</b> {protocol_id}
<b>Status:</b> {status.upper()}
<b>Time:</b> {timestamp}

<b>Doctor Notes:</b>
{notes if notes else "No additional notes provided"}

<b>Action Required:</b> {action_text}

🏥 Asclepius AI - ICU Sepsis Early Warning System"""

        results = {}
        
        # Send to both nurse and doctor for transparency
        if self.nurse_chat_id:
            nurse_result = await self._send_message(self.nurse_chat_id, message)
            results["nurse"] = nurse_result
        
        if self.doctor_chat_id:
            doctor_result = await self._send_message(self.doctor_chat_id, message)
            results["doctor"] = doctor_result
        
        return results
    
    async def _send_message(self, chat_id: str, message: str, buttons: Optional[Dict] = None) -> Dict[str, Any]:
        """Send message to Telegram chat"""
        if not self.bot_token or not chat_id:
            return {"status": "error", "message": "Missing bot token or chat ID"}
        
        url = f"{self.base_url}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        
        if buttons:
            data["reply_markup"] = buttons
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=data)
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Message sent to chat {chat_id}")
                    return {
                        "status": "success",
                        "message_id": result.get("result", {}).get("message_id")
                    }
                else:
                    error_text = response.text
                    logger.error(f"Telegram API error: {response.status_code} - {error_text}")
                    return {
                        "status": "error",
                        "code": response.status_code,
                        "message": error_text
                    }
        except Exception as e:
            logger.error(f"Telegram error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
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

# Global service instance for backwards compatibility
telegram_service = TelegramService()

# Legacy function aliases for backwards compatibility
async def send_warning_alert_to_nurse(patient_name: str, patient_id: str, bed_number: str, 
                                     risk_score: float, factors: list):
    """Legacy function - use TelegramService.send_warning_alert instead"""
    patient_data = {
        'name': patient_name,
        'id': patient_id,
        'bed_number': bed_number,
        'current_risk_score': risk_score,
        'diagnosis': 'Legacy alert'
    }
    return await telegram_service.send_warning_alert(patient_data)

async def send_critical_alert_to_nurse_and_doctor(patient_name: str, patient_id: str, 
                                                bed_number: str, risk_score: float, 
                                                factors: list, protocol_id: str):
    """Legacy function - use TelegramService.send_critical_alert instead"""
    patient_data = {
        'name': patient_name,
        'id': patient_id,
        'bed_number': bed_number,
        'current_risk_score': risk_score,
        'diagnosis': 'Legacy critical alert'
    }
    return await telegram_service.send_critical_alert(patient_data)

async def send_doctor_decision_to_nurse(patient_name: str, bed_number: str, decision: str, notes: str = ""):
    """Legacy function - use TelegramService.send_protocol_update instead"""
    protocol_id = f"LEGACY_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    patient_id = f"PAT_{bed_number}"
    return await telegram_service.send_protocol_update(protocol_id, patient_id, decision, notes)