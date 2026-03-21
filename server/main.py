"""
Asclepius AI — ICU Sepsis Early Warning System
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import get_settings
from db.simple_mongo import init_db, close_db

# Routers
from api.patients import router as patients_router
from api.alerts import router as alerts_router
from api.seed import router as seed_router
from api.protocol import router as protocol_router
from api.websocket import router as ws_router
from api.analytics import router as analytics_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: connect to MongoDB
    await init_db()
    yield
    # Shutdown: close MongoDB connection
    await close_db()


app = FastAPI(
    title="Asclepius AI",
    description="ICU Sepsis Early Warning System — Multi-Agent AI with MongoDB Atlas",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev
        "http://localhost:5173",  # Vite dev  
        "https://*.vercel.app",   # Vercel deployments
        "https://vercel.app",     # Vercel domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(patients_router)
app.include_router(alerts_router)
app.include_router(seed_router)
app.include_router(protocol_router)
app.include_router(ws_router)
app.include_router(analytics_router)


@app.get("/", tags=["Health"])
async def root():
    return {
        "system": "Asclepius AI",
        "status": "online",
        "version": "1.0.0",
        "database": "MongoDB Atlas",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "database": "MongoDB Atlas"}