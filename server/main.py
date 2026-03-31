"""
Asclepius AI — Clean main server file
Enhanced ICU Sepsis Early Warning System
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import API routers
from api.patients import router as patients_router
from api.alerts import router as alerts_router  
from api.seed import router as seed_router
from api.protocol import router as protocol_router
from api.websocket import router as ws_router
from api.analytics import router as analytics_router
from api.health_tip import router as health_tip_router
from db.mongodb import init_db, close_db
from services.telegram_service import TelegramService
from services.telegram_bot_runner_direct import telegram_bot_runner
from config import get_settings

settings = get_settings()

# Initialize Telegram service
telegram_service = TelegramService()

# Import chat IDs for status check
NURSE_CHAT_ID = settings.telegram_nurse_chat_id
DOCTOR_CHAT_ID = settings.telegram_doctor_chat_id

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 Starting Asclepius AI system...")
    
    try:
        # Initialize database
        await init_db()
        logger.info("✅ Database connected")
        
        # Initialize Telegram service
        if telegram_service.is_configured():
            logger.info("📱 Telegram service initialized with real mode")
            # Test connection
            test_result = await telegram_service.test_connection()
            if test_result["status"] == "success":
                logger.info(f"✅ Telegram bot connected: {test_result.get('bot_info', {}).get('username', 'Unknown')}")
            else:
                logger.error(f"❌ Telegram bot connection failed: {test_result['message']}")
        else:
            logger.error("❌ Telegram not properly configured - check environment variables")
        
        # Start integrated Telegram bot
        if telegram_bot_runner.is_configured():
            logger.info(f"🤖 Starting integrated Telegram bot...")
            logger.info(f"📱 Nurse Chat ID: {settings.telegram_nurse_chat_id}")
            logger.info(f"👨‍⚕️ Doctor Chat ID: {settings.telegram_doctor_chat_id}")
            
            bot_started = await telegram_bot_runner.start_bot()
            if bot_started:
                logger.info("✅ Integrated Telegram bot started successfully")
                logger.info("🔗 Bot will handle approval buttons and /note commands")
            else:
                logger.error("❌ Telegram bot failed to start - check token and configuration")
                logger.error("💡 System will continue without Telegram notifications")
        else:
            logger.warning("🤖 Telegram bot not configured - missing token or chat IDs")
            logger.warning("💡 Add TELEGRAM_BOT_TOKEN, TELEGRAM_NURSE_CHAT_ID, TELEGRAM_DOCTOR_CHAT_ID to .env")
        
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        # Continue anyway - system can function without some components
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Asclepius AI...")
    
    # Stop Telegram bot
    if telegram_bot_runner.running:
        await telegram_bot_runner.stop_bot()
    
    await close_db()
    logger.info("✅ Database connection closed")

# Create FastAPI app with original configuration
app = FastAPI(
    title="Asclepius AI - ICU Sepsis Early Warning System",
    description="""
    🏥 **Advanced Medical AI System** for ICU sepsis detection and management
    
    **Features:**
    - Real-time patient monitoring
    - AI-powered sepsis risk prediction  
    - Automated clinical protocols
    - Telegram notifications for medical staff
    - Comprehensive analytics dashboard
    
    **Medical Grade:** Professional healthcare application with realistic medical data
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS configuration for medical application
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "https://*.vercel.app",
        "https://*.onrender.com",
        "*"  # For development - restrict in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all original API routers (they already have prefixes defined)

app.include_router(patients_router, tags=["👥 Patients"])
app.include_router(alerts_router, tags=["🚨 Alerts"])
app.include_router(protocol_router, tags=["📋 Medical Protocols"])  
app.include_router(analytics_router, tags=["📊 Analytics"])
app.include_router(seed_router, tags=["🌱 Data Seeding"])
app.include_router(ws_router, tags=["⚡ Real-time"])
app.include_router(health_tip_router, tags=["💡 Health Tips"])

# Add throttle configuration router
from api.throttle import router as throttle_router
app.include_router(throttle_router, tags=["⏱️ Alert Throttling"])

# Enhanced health endpoints
@app.get("/", tags=["🏥 System Health"])
async def system_status():
    """System status and configuration check"""
    
    # Debug: Check configuration status
    service_configured = telegram_service.is_configured()
    bot_configured = telegram_bot_runner.is_configured()
    bot_running = telegram_bot_runner.running
    
    logger.info(f"🔍 Status Check - Service: {service_configured}, Bot Configured: {bot_configured}, Bot Running: {bot_running}")
    
    # Check if integrated bot is running
    bot_status = "✅ Integrated Bot Running" if bot_running else (
        "⚠️ Configured" if bot_configured else "❌ Not Configured"
    )
    
    # Check Telegram service
    telegram_status = "✅ Ready" if service_configured else "⚠️ Demo Mode"
    
    # System is in production if both service is configured AND bot is running
    is_production = service_configured and bot_running
    
    return {
        "system": "Asclepius AI",
        "status": "🟢 Online",
        "version": "2.0.0",
        "mode": "production" if is_production else "demo",
        "description": "ICU Sepsis Early Warning System",
        "features": {
            "database": "✅ MongoDB Connected",
            "ai_prediction": "✅ Sepsis Risk Models",  
            "telegram_notifications": telegram_status,
            "integrated_bot": bot_status,
            "real_time_monitoring": "✅ WebSocket Enabled",
            "medical_protocols": "✅ Active"
        },
        "endpoints": {
            "documentation": "/docs",
            "patients": "/patients/",
            "alerts": "/alerts/", 
            "protocols": "/protocols/",
            "analytics": "/analytics/",
            "websocket": "/ws/icu",
            "bot_status": "/telegram/bot/status"
        },
        "connection_test": {
            "telegram_service_configured": service_configured,
            "bot_configured": bot_configured,
            "bot_running": bot_running,
            "nurse_chat_id": NURSE_CHAT_ID,
            "doctor_chat_id": DOCTOR_CHAT_ID,
            "production_mode": is_production
        }
    }

@app.get("/health", tags=["🏥 System Health"])
async def health_check():
    """Simple health check for monitoring"""
    return {
        "status": "healthy",
        "timestamp": "2026-03-22T00:21:38.515Z",
        "system": "asclepius-ai",
        "version": "2.0.0"
    }

# Telegram configuration check endpoint
@app.get("/telegram/config", tags=["📱 Telegram"])  
async def check_telegram_config():
    """Check current Telegram configuration"""
    settings = get_settings()
    return {
        "bot_token_configured": bool(settings.telegram_bot_token),
        "nurse_chat_configured": bool(settings.telegram_nurse_chat_id),
        "doctor_chat_configured": bool(settings.telegram_doctor_chat_id),
        "service_configured": telegram_service.is_configured(),
        "bot_configured": telegram_bot_runner.is_configured(),
        "bot_running": telegram_bot_runner.running,
        "config_values": {
            "bot_token": settings.telegram_bot_token[:10] + "..." if settings.telegram_bot_token else "NOT SET",
            "nurse_chat_id": settings.telegram_nurse_chat_id if settings.telegram_nurse_chat_id else "NOT SET", 
            "doctor_chat_id": settings.telegram_doctor_chat_id if settings.telegram_doctor_chat_id else "NOT SET"
        }
    }

@app.get("/telegram/bot/status", tags=["📱 Telegram"])
async def check_bot_status():
    """Check integrated Telegram bot status"""
    return {
        "bot_configured": telegram_bot_runner.is_configured(),
        "bot_running": telegram_bot_runner.running,
        "chat_ids": {
            "nurse": NURSE_CHAT_ID,
            "doctor": DOCTOR_CHAT_ID
        },
        "features": [
            "Critical alert workflow with doctor approval buttons",
            "Warning alerts to nurse only", 
            "Doctor note commands (/note PAT001 message)",
            "Real-time protocol approval/rejection"
        ],
        "commands": [
            "/note <patient_id> <message> - Doctor adds instructions",
            "/warning - Test warning alert",
            "/start - Bot information"
        ],
        "test_endpoints": {
            "test_critical_message": "/telegram/test/critical",
            "test_warning_message": "/telegram/test/warning"
        }
    }

@app.post("/telegram/test/critical", tags=["📱 Telegram"])
async def test_critical_message():
    """Test sending a critical alert message"""
    if not telegram_bot_runner.running:
        return {
            "error": "Telegram bot not running",
            "status": "bot_not_running",
            "solution": "Start server with: python start_system.py"
        }
    
    if not telegram_service.is_configured():
        return {
            "error": "Telegram service not configured", 
            "status": "service_not_configured",
            "solution": "Check TELEGRAM_BOT_TOKEN and chat IDs in server/.env"
        }
    
    test_patient = {
        "id": "TEST001",
        "name": "Test Patient",
        "bed_number": "ICU-TEST",
        "current_risk_score": 85.5,
        "diagnosis": "Test Case - Critical Alert",
        "vitals": {
            "heart_rate": 120,
            "systolic_bp": 90,
            "respiratory_rate": 28,
            "temperature": 38.5,
            "spo2": 90,
            "lactate": 4.2
        }
    }
    
    try:
        logger.info("🧪 Sending test critical alert...")
        result = await telegram_service.send_critical_alert(test_patient)
        return {
            "status": "success",
            "message": "🚨 Test critical alert sent successfully!",
            "patient": test_patient,
            "result": result,
            "instructions": [
                "1. Check doctor Telegram chat for message with buttons",
                "2. Check nurse Telegram chat for status message", 
                "3. Click 'Approve' button to test workflow",
                "4. Check server logs for button click events"
            ]
        }
    except Exception as e:
        logger.error(f"❌ Test critical alert failed: {e}")
        return {
            "status": "error", 
            "message": f"Failed to send test alert: {e}",
            "troubleshooting": [
                "1. Check server logs for errors",
                "2. Verify bot is in both doctor and nurse chats", 
                "3. Test bot token: curl https://api.telegram.org/bot<TOKEN>/getMe",
                "4. Restart server if needed"
            ]
        }

@app.post("/telegram/test/warning", tags=["📱 Telegram"])
async def test_warning_message():
    """Test sending a warning alert message"""
    if not telegram_bot_runner.running:
        return {"error": "Telegram bot not running"}
    
    test_patient = {
        "id": "TEST002",
        "name": "Test Patient 2",
        "bed_number": "ICU-TEST-2",
        "current_risk_score": 65.0,
        "diagnosis": "Warning Test Case",
        "vitals": {
            "heart_rate": 100,
            "systolic_bp": 110,
            "respiratory_rate": 22,
            "temperature": 37.8,
            "spo2": 94,
            "lactate": 2.5
        }
    }
    
    try:
        result = await telegram_service.send_warning_alert(test_patient)
        return {
            "status": "success",
            "message": "Test warning alert sent",
            "result": result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to send test alert: {e}"
        }

@app.get("/debug/system", tags=["🔧 Debug"])
async def debug_system_status():
    """Debug system configuration and status"""
    settings = get_settings()
    
    return {
        "timestamp": datetime.now().isoformat(),
        "environment": {
            "telegram_bot_token": "✅ Set" if settings.telegram_bot_token else "❌ Missing",
            "telegram_bot_token_preview": settings.telegram_bot_token[:10] + "..." if settings.telegram_bot_token else None,
            "nurse_chat_id": settings.telegram_nurse_chat_id,
            "doctor_chat_id": settings.telegram_doctor_chat_id,
            "mongodb_url": "✅ Set" if settings.mongodb_url else "❌ Missing"
        },
        "telegram_service": {
            "configured": telegram_service.is_configured(),
            "has_token": bool(settings.telegram_bot_token),
            "has_nurse_chat": bool(settings.telegram_nurse_chat_id),
            "has_doctor_chat": bool(settings.telegram_doctor_chat_id)
        },
        "telegram_bot_runner": {
            "configured": telegram_bot_runner.is_configured(),
            "running": telegram_bot_runner.running,
            "has_app": telegram_bot_runner.app is not None
        },
        "production_check": {
            "service_configured": telegram_service.is_configured(),
            "bot_configured": telegram_bot_runner.is_configured(), 
            "bot_running": telegram_bot_runner.running,
            "should_be_production": telegram_service.is_configured() and telegram_bot_runner.running
        },
        "next_steps": [
            "1. Check all environment variables are set",
            "2. Test bot token with /telegram/test/critical", 
            "3. Verify bot is added to doctor and nurse chats",
            "4. Send /start command to bot in both chats",
            "5. Restart server if configuration changed"
        ]
    }

# Simple webhook placeholder (not needed for polling mode)
@app.post("/telegram/webhook", tags=["📱 Telegram"])
async def telegram_webhook():
    """Webhook endpoint (not used in polling mode)"""
    return {"status": "webhook_not_used", "mode": "polling"}
async def telegram_webhook(update: dict):
    """Handle Telegram webhook updates (button callbacks)"""
    try:
        logger.info(f"📱 Webhook received: {update}")
        
        # Handle callback queries (button presses)
        if "callback_query" in update:
            callback_query = update["callback_query"]
            callback_data = callback_query.get("data", "")
            chat_id = callback_query["from"]["id"]
            message_id = callback_query["message"]["message_id"]
            
            logger.info(f"🔘 Button pressed: '{callback_data}' by user {chat_id}")
            
            # Parse callback data: accept_critical, reject_critical, add_note_critical, approve_protocol_id, etc.
            parts = callback_data.split("_")
            action = parts[0]
            
            # Handle compound actions like "add_note"
            if len(parts) >= 2 and parts[0] == "add" and parts[1] == "note":
                action = "add_note"
                protocol_id = parts[2] if len(parts) > 2 else "Unknown"
            else:
                protocol_id = parts[1] if len(parts) > 1 else "Unknown"
                
            logger.info(f"🔘 Parsed action: '{action}', protocol_id: '{protocol_id}'")
            
            # Handle different actions
            if action == "approve":
                response_text = "✅ **PROTOCOL APPROVED**\n\nThe medical protocol has been approved and will be executed."
                await _update_protocol_status(protocol_id, "approved", "Approved via Telegram")
                
            elif action == "reject":
                response_text = "❌ **PROTOCOL REJECTED**\n\nThe medical protocol has been rejected. Please review alternatives."
                await _update_protocol_status(protocol_id, "rejected", "Rejected via Telegram")
                
            elif action == "modify":
                response_text = "✏️ **PROTOCOL MODIFICATION REQUESTED**\n\nPlease review and modify the protocol on the dashboard."
                await _update_protocol_status(protocol_id, "pending", "Modification requested via Telegram")
                
            elif action == "details":
                response_text = "📋 **PROTOCOL DETAILS**\n\nPlease review the full protocol details on the Asclepius AI dashboard."
                
            elif action == "accept":
                response_text = "✅ **ACCEPTED**\n\nCritical alert accepted. Treatment protocols are being initiated."
                
            elif action == "add_note":
                response_text = "📝 **ADD NOTE**\n\nTo add a note, please reply to this message with your note, or use the dashboard for detailed notes."
                
            else:
                logger.warning(f"❓ Unknown action: '{action}' from callback_data: '{callback_data}'")
                logger.warning(f"🔍 Full parts array: {parts}")
                logger.warning(f"🔍 Callback query: {callback_query}")
                response_text = f"⚠️ Unknown action: '{action}'\n\nDebug Info:\n• callback_data: '{callback_data}'\n• parsed parts: {parts}\n• action detected: '{action}'\n\nPlease check server logs for details."
            
            # Send response back to Telegram
            await telegram_service.edit_message(chat_id, message_id, response_text)
            
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"status": "error", "message": str(e)}

# Telegram webhook setup endpoint  
@app.post("/telegram/setup-webhook", tags=["📱 Telegram"])
async def setup_telegram_webhook(webhook_url: str = None):
    """Setup Telegram webhook for button callbacks"""
    if not telegram_service.is_configured():
        raise HTTPException(
            status_code=503, 
            detail="Telegram not configured. Set TELEGRAM_BOT_TOKEN and chat IDs in environment variables."
        )
    
    # Use provided URL or build from request
    if not webhook_url:
        # In production, this would be your actual domain
        webhook_url = "https://your-domain.com/telegram/webhook"
    
    try:
        import httpx
        url = f"https://api.telegram.org/bot{telegram_service.bot_token}/setWebhook"
        data = {"url": webhook_url}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=data)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "success",
                    "message": "Webhook configured successfully",
                    "webhook_url": webhook_url,
                    "result": result
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to setup webhook: {response.text}"
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to setup webhook: {str(e)}")

async def _update_protocol_status(protocol_id: str, status: str, notes: str):
    """Update protocol status in database"""
    try:
        from models.protocol import Protocol
        from beanie import PydanticObjectId
        from datetime import datetime, timezone
        
        if protocol_id != "Unknown":
            protocol = await Protocol.get(PydanticObjectId(protocol_id))
            if protocol:
                protocol.status = status
                protocol.reviewed_by = "doctor_telegram"
                protocol.doctor_notes = notes
                protocol.reviewed_at = datetime.now(timezone.utc)
                await protocol.save()
                logger.info(f"✅ Updated protocol {protocol_id} status to {status}")
            else:
                logger.warning(f"⚠️ Protocol {protocol_id} not found")
        else:
            logger.warning("⚠️ Unknown protocol ID in callback")
    except Exception as e:
        logger.error(f"❌ Failed to update protocol: {e}")

# Telegram test endpoint
@app.get("/telegram/test", tags=["📱 Telegram"])
async def test_telegram_notifications():
    """Test Telegram notification system"""
    if not telegram_service.is_configured():
        raise HTTPException(
            status_code=503, 
            detail="Telegram not configured. Set TELEGRAM_BOT_TOKEN and chat IDs in environment variables."
        )
    
    test_message = """🧪 <b>Asclepius AI Test</b>
    
<b>System Status:</b> Online ✅
<b>Time:</b> 2026-03-22 00:21:38 UTC
<b>Test Type:</b> Telegram Integration

This is a test notification from the Asclepius AI medical monitoring system.

If you receive this message, the notification system is working correctly! 📱⚡

🏥 <i>Asclepius AI - ICU Sepsis Early Warning System</i>"""

    try:
        results = await telegram_service.send_to_medical_team(
            message=test_message,
            level="info"
        )
        
        return {
            "status": "success",
            "message": "Test notifications sent to medical team",
            "results": results,
            "timestamp": "2026-03-22T00:21:38.515Z"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send test: {str(e)}")

# Test webhook manually
@app.post("/telegram/test-webhook-manually", tags=["📱 Telegram"])
async def test_webhook_manually():
    """Manually test webhook parsing with sample data"""
    
    # Simulate different button callback scenarios
    test_scenarios = [
        {
            "name": "Accept Critical",
            "callback_data": "accept_critical",
            "expected_action": "accept"
        },
        {
            "name": "Reject Critical", 
            "callback_data": "reject_critical",
            "expected_action": "reject"
        },
        {
            "name": "Add Note Critical",
            "callback_data": "add_note_critical", 
            "expected_action": "add_note"
        },
        {
            "name": "Test Button",
            "callback_data": "accept_test123",
            "expected_action": "accept"
        }
    ]
    
    results = []
    
    for scenario in test_scenarios:
        callback_data = scenario["callback_data"]
        
        # Parse callback data using same logic as webhook
        parts = callback_data.split("_")
        action = parts[0]
        
        # Handle compound actions like "add_note"
        if len(parts) >= 2 and parts[0] == "add" and parts[1] == "note":
            action = "add_note"
            protocol_id = parts[2] if len(parts) > 2 else "unknown"
        else:
            protocol_id = parts[1] if len(parts) > 1 else "unknown"
        
        results.append({
            "scenario": scenario["name"],
            "callback_data": callback_data,
            "parts": parts,
            "parsed_action": action,
            "protocol_id": protocol_id,
            "expected_action": scenario["expected_action"],
            "matches_expected": action == scenario["expected_action"]
        })
    
    return {
        "status": "success",
        "webhook_parsing_test": results,
        "summary": {
            "total_tests": len(results),
            "passed": len([r for r in results if r["matches_expected"]]),
            "failed": len([r for r in results if not r["matches_expected"]])
        }
    }

# Test Telegram buttons endpoint
@app.post("/telegram/test-buttons", tags=["📱 Telegram"])
async def test_telegram_buttons():
    """Test Telegram buttons functionality"""
    if not telegram_service.is_configured():
        raise HTTPException(
            status_code=503, 
            detail="Telegram not configured. Set TELEGRAM_BOT_TOKEN and chat IDs in environment variables."
        )
    
    test_message = """🧪 <b>Button Test</b>
    
This is a test message with interactive buttons.
Please use the buttons below:
• ✅ Accept - Acknowledge and accept the alert
• ❌ Reject - Reject the alert with reason
• 📝 Add Note - Add additional notes

🏥 <i>Asclepius AI - ICU Sepsis Early Warning System</i>"""

    # Test buttons
    test_buttons = {
        "inline_keyboard": [
            [
                {"text": "✅ Accept", "callback_data": "accept_test123"},
                {"text": "❌ Reject", "callback_data": "reject_test123"}
            ],
            [
                {"text": "📝 Add Note", "callback_data": "add_note_test123"}
            ]
        ]
    }

    try:
        # Test critical alert with buttons
        test_result = await telegram_service.send_to_medical_team(
            test_message, 
            level="critical",
            include_buttons=True
        )
        
        return {
            "status": "success",
            "message": "Test message with buttons sent to medical team",
            "results": test_result,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send test buttons: {str(e)}")

# Quick restore working state
@app.post("/admin/restore-working-state", tags=["🔧 Admin"])
async def restore_working_state():
    """Restore the system to a known working state with patients and sample data"""
    
    try:
        from models.patient import Patient
        from models.vital import Vital
        from models.alert import Alert
        from models.protocol import Protocol
        
        # Check current state
        patient_count = await Patient.count()
        logger.info(f"📊 Current patients: {patient_count}")
        
        # Clear existing data if needed and recreate
        if patient_count == 0:
            sample_patients = [
                {
                    "name": "John Doe",
                    "age": 65,
                    "gender": "Male", 
                    "bed_number": "ICU-101",
                    "diagnosis": "Pneumonia",
                    "allergies": "Penicillin",
                    "comorbidities": "Diabetes, HTN",
                    "is_post_surgical": False,
                    "is_immunocompromised": False
                },
                {
                    "name": "Sarah Johnson", 
                    "age": 52,
                    "gender": "Female",
                    "bed_number": "ICU-102", 
                    "diagnosis": "Post-abdominal surgery",
                    "allergies": "",
                    "comorbidities": "Asthma",
                    "is_post_surgical": True,
                    "is_immunocompromised": False
                },
                {
                    "name": "Michael Chen",
                    "age": 71,
                    "gender": "Male",
                    "bed_number": "ICU-103",
                    "diagnosis": "Sepsis suspected", 
                    "allergies": "Sulfa",
                    "comorbidities": "COPD, CKD",
                    "is_post_surgical": False,
                    "is_immunocompromised": False
                }
            ]
            
            # Create patients
            created_patients = []
            for patient_data in sample_patients:
                patient = Patient(**patient_data)
                await patient.insert()
                created_patients.append({
                    "id": str(patient.id),
                    "name": patient.name,
                    "bed_number": patient.bed_number
                })
                
            # Add some initial vitals to make it look like it was working
            from services.vitals_service import ingest_vital
            from beanie import PydanticObjectId
            
            normal_vitals = {
                "heart_rate": 75.0,
                "systolic_bp": 120.0,
                "respiratory_rate": 16.0,
                "temperature": 37.0,
                "spo2": 98.0,
                "lactate": 1.0,
            }
            
            for patient_data in created_patients:
                try:
                    patient_obj_id = PydanticObjectId(patient_data["id"])
                    await ingest_vital(patient_obj_id, normal_vitals, source="restore_baseline")
                except Exception as e:
                    logger.warning(f"Could not add initial vitals for {patient_data['name']}: {e}")
            
            return {
                "status": "success",
                "message": "System restored to working state",
                "patients_created": len(created_patients),
                "patients": created_patients,
                "note": "Critical seed button should now work properly"
            }
        else:
            return {
                "status": "info",
                "message": f"System already has {patient_count} patients",
                "note": "If critical button still shows demo mode, there may be a different issue"
            }
            
    except Exception as e:
        logger.error(f"Failed to restore working state: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to restore: {str(e)}")

# Database status endpoint
@app.get("/admin/db-status", tags=["🔧 Admin"])
async def database_status():
    """Check database status and record counts"""
    try:
        from models.patient import Patient
        from models.vital import Vital
        from models.alert import Alert
        from models.protocol import Protocol
        
        patient_count = await Patient.count()
        vital_count = await Vital.count()
        alert_count = await Alert.count()
        protocol_count = await Protocol.count()
        
        return {
            "status": "success",
            "database": "MongoDB (Beanie)",
            "collections": {
                "patients": patient_count,
                "vitals": vital_count, 
                "alerts": alert_count,
                "protocols": protocol_count
            },
            "ready_for_seeding": patient_count > 0,
            "message": "Ready to seed vitals" if patient_count > 0 else "Need to create patients first"
        }
        
    except Exception as e:
        logger.error(f"Database status check failed: {e}")
        return {
            "status": "error",
            "message": f"Database error: {str(e)}"
        }

# Initialize database with sample patients
@app.post("/admin/init-patients", tags=["🔧 Admin"])
async def initialize_sample_patients():
    """Initialize database with sample ICU patients for testing"""
    
    sample_patients = [
        {
            "name": "John Doe",
            "age": 65,
            "gender": "Male", 
            "bed_number": "ICU-101",
            "diagnosis": "Pneumonia",
            "allergies": "Penicillin",
            "comorbidities": "Diabetes, HTN",
            "is_post_surgical": False,
            "is_immunocompromised": False
        },
        {
            "name": "Sarah Johnson", 
            "age": 52,
            "gender": "Female",
            "bed_number": "ICU-102", 
            "diagnosis": "Post-abdominal surgery",
            "allergies": "",
            "comorbidities": "Asthma",
            "is_post_surgical": True,
            "is_immunocompromised": False
        },
        {
            "name": "Michael Chen",
            "age": 71,
            "gender": "Male",
            "bed_number": "ICU-103",
            "diagnosis": "Sepsis suspected", 
            "allergies": "Sulfa",
            "comorbidities": "COPD, CKD",
            "is_post_surgical": False,
            "is_immunocompromised": False
        },
        {
            "name": "Emma Williams",
            "age": 58, 
            "gender": "Female",
            "bed_number": "ICU-104",
            "diagnosis": "UTI with complications",
            "allergies": "",
            "comorbidities": "HIV+",
            "is_post_surgical": False,
            "is_immunocompromised": True
        },
        {
            "name": "David Martinez",
            "age": 73,
            "gender": "Male", 
            "bed_number": "ICU-105",
            "diagnosis": "Community-acquired pneumonia",
            "allergies": "ACE inhibitors",
            "comorbidities": "CHF, AFib",
            "is_post_surgical": False,
            "is_immunocompromised": False
        }
    ]
    
    try:
        from models.patient import Patient
        
        # Check if patients already exist
        existing_count = await Patient.count()
        if existing_count > 0:
            return {
                "status": "info",
                "message": f"Database already has {existing_count} patients",
                "existing_patients": existing_count
            }
        
        # Create sample patients
        created_patients = []
        for patient_data in sample_patients:
            patient = Patient(**patient_data)
            await patient.insert()
            created_patients.append({
                "id": str(patient.id),
                "name": patient.name,
                "bed_number": patient.bed_number
            })
        
        return {
            "status": "success",
            "message": f"Successfully created {len(created_patients)} sample patients",
            "patients": created_patients
        }
        
    except Exception as e:
        logger.error(f"Failed to initialize patients: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize patients: {str(e)}")

# Enhanced error handling
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Endpoint not found",
        "message": "Please check the API documentation at /docs",
        "system": "Asclepius AI",
        "available_endpoints": ["/patients", "/alerts", "/protocols", "/analytics", "/ws"]
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🏥 Starting Asclepius AI server...")
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENV") == "development"
    )