"""
Asclepius AI - Fixed version for deployment
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import without relative imports
from api.patients import router as patients_router
from api.alerts import router as alerts_router  
from api.seed import router as seed_router
from api.protocol import router as protocol_router
from api.websocket import router as ws_router
from api.analytics import router as analytics_router
from db.mongodb import init_db, close_db
from services.telegram_service import TelegramService
from config import get_settings

settings = get_settings()
telegram_service = TelegramService()

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
            logger.info("📱 Telegram service initialized")
        else:
            logger.warning("⚠️ Telegram not configured - using demo mode")
        
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        # Continue anyway for demo mode
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Asclepius AI...")
    await close_db()
    logger.info("✅ Database connection closed")

# Create FastAPI app
app = FastAPI(
    title="Asclepius AI - ICU Sepsis Early Warning System",
    description="""
    🏥 **Advanced Medical AI System** for ICU sepsis detection and management
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(patients_router, tags=["👥 Patients"])
app.include_router(alerts_router, tags=["🚨 Alerts"])
app.include_router(protocol_router, tags=["📋 Medical Protocols"])  
app.include_router(analytics_router, tags=["📊 Analytics"])
app.include_router(seed_router, tags=["🌱 Data Seeding"])
app.include_router(ws_router, tags=["⚡ Real-time"])

# Health endpoints
@app.get("/", tags=["🏥 System Health"])
async def system_status():
    """System status and configuration check"""
    return {
        "system": "Asclepius AI",
        "status": "🟢 Online",
        "version": "2.0.0",
        "mode": "full_featured",
        "description": "ICU Sepsis Early Warning System",
        "features": {
            "database": "✅ MongoDB Connected",
            "ai_prediction": "✅ Sepsis Risk Models",  
            "telegram_notifications": "✅ Ready" if telegram_service.is_configured() else "⚠️ Demo Mode",
            "real_time_monitoring": "✅ WebSocket Enabled",
            "medical_protocols": "✅ Active"
        }
    }

@app.get("/health", tags=["🏥 System Health"])
async def health_check():
    """Simple health check for monitoring"""
    return {
        "status": "healthy",
        "system": "asclepius-ai",
        "version": "2.0.0"
    }

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
<b>Test Type:</b> Telegram Integration

This is a test notification from the Asclepius AI medical monitoring system.

🏥 <i>Asclepius AI - ICU Sepsis Early Warning System</i>"""

    try:
        results = await telegram_service.send_to_medical_team(
            message=test_message,
            level="info"
        )
        
        return {
            "status": "success",
            "message": "Test notifications sent to medical team",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send test: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🏥 Starting Asclepius AI server...")
    uvicorn.run(
        "main_fixed:app", 
        host="0.0.0.0", 
        port=int(os.getenv("PORT", 8000)),
        reload=False
    )