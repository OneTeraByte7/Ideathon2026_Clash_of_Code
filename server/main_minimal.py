"""
Asclepius AI — Minimal deployment version
FastAPI application for Render deployment without complex dependencies
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Simple routers that work without Beanie
from api.patients_simple import router as patients_router
from api.alerts_simple import router as alerts_router
from api.seed_simple import router as seed_router
from api.protocols_simple import router as protocol_router
from api.websocket_simple import router as ws_router
from api.analytics_simple import router as analytics_router

# Optional database connection
try:
    from db.simple_mongo import init_db, close_db
    USE_DB = True
except ImportError:
    USE_DB = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if USE_DB:
        try:
            await init_db()
        except Exception as e:
            print(f"Database connection failed, using mock data: {e}")
    yield
    # Shutdown
    if USE_DB:
        try:
            await close_db()
        except Exception:
            pass

app = FastAPI(
    title="Asclepius AI",
    description="ICU Sepsis Early Warning System — Minimal Deployment Version",
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
        "*"  # Allow all for now
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
        "version": "1.0.0 (minimal)",
        "database": "MongoDB Atlas (optional)",
        "docs": "/docs",
    }

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "mode": "minimal"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)