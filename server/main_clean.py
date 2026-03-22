"""
Asclepius AI — Medical ICU System with Telegram Integration
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

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

# Import database and services
from db.mongodb import init_db, close_db
from services.telegram_service import TelegramService
from config import get_settings

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting Asclepius AI system...")
    
    # Initialize database
    await init_db()
    logger.info("✅ Database connected")
    
    # Initialize Telegram service
    telegram_service = TelegramService()
    app.state.telegram = telegram_service
    
    if settings.telegram_bot_token:
        logger.info("✅ Telegram service initialized")
    else:
        logger.warning("⚠️ Telegram not configured - using demo mode")
    
    yield
    
    # Cleanup
    await close_db()
    logger.info("✅ MongoDB connection closed")

# Create FastAPI app
app = FastAPI(
    title="Asclepius AI",
    description="Medical ICU AI System with Telegram Integration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(patients_router, prefix="/patients", tags=["patients"])
app.include_router(alerts_router, prefix="/alerts", tags=["alerts"])
app.include_router(protocol_router, prefix="/protocols", tags=["protocols"])
app.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
app.include_router(ws_router, prefix="/ws", tags=["websocket"])
app.include_router(seed_router, prefix="/seed", tags=["seed"])

@app.get("/")
async def root():
    return {"message": "Asclepius AI System Running", "status": "active"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "asclepius-ai"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)