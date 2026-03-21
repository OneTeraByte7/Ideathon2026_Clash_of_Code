#!/usr/bin/env python3
"""Quick verification that all backend modules can be imported without errors."""
import sys
import asyncio

print("=" * 60)
print("🧪 BACKEND IMPORT TEST")
print("=" * 60)

try:
    print("\n1️⃣ Testing config...")
    from backend.config import get_settings
    settings = get_settings()
    print(f"   ✅ Config loaded: {settings.database_name}")
    
    print("\n2️⃣ Testing MongoDB connection...")
    from backend.db.mongo_database import get_db_connection, init_db
    db = get_db_connection()
    print(f"   ✅ Database connection ready")
    
    print("\n3️⃣ Testing models...")
    from backend.models.patient import Patient
    from backend.models.vital import Vital
    from backend.models.alert import Alert
    from backend.models.protocol import Protocol
    print(f"   ✅ All models imported successfully")
    
    print("\n4️⃣ Testing API routers...")
    from backend.api.patients import router as patients_router
    from backend.api.alerts import router as alerts_router
    from backend.api.seed import router as seed_router
    from backend.api.protocol import router as protocol_router
    from backend.api.analytics import router as analytics_router
    from backend.api.websocket import router as ws_router
    print(f"   ✅ All routers imported successfully")
    
    print("\n5️⃣ Testing services...")
    from backend.services.vitals_service import ingest_vital
    from backend.core.risk_engine import compute_risk
    from backend.core.notifier import notify_nurse, notify_doctor
    print(f"   ✅ All services imported successfully")
    
    print("\n6️⃣ Testing main app...")
    from backend.main import app
    print(f"   ✅ FastAPI app created successfully")
    print(f"      Title: {app.title}")
    print(f"      Routes: {len(app.routes)}")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - Backend ready to start!")
    print("=" * 60)
    sys.exit(0)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
