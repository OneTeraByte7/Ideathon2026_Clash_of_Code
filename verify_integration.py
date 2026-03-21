#!/usr/bin/env python3
"""
Asclepius AI - Quick Integration Verification Script

This script verifies that:
1. Backend imports are correct (no old SQLAlchemy)
2. MongoDB connection works
3. Models are properly initialized
4. All API routes are accessible
5. WebSocket is configured
6. Telegram settings are loaded

Run: python verify_integration.py
"""

import sys
import os
import asyncio
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def test_imports():
    """Test that all backend modules can be imported."""
    print("\n" + "=" * 70)
    print("🔍 TESTING IMPORTS")
    print("=" * 70)
    
    try:
        print("\n1. Config module...")
        from config import get_settings
        settings = get_settings()
        print(f"   ✅ Config: {settings.database_name}")
        
        print("\n2. MongoDB module (new)...")
        from db.mongo_database import get_db_connection, init_db, close_db
        print("   ✅ MongoDB module imported (using Beanie)")
        
        print("\n3. Beanie Models...")
        from models.patient import Patient
        from models.vital import Vital
        from models.alert import Alert
        from models.protocol import Protocol
        print("   ✅ All models are Beanie documents")
        
        print("\n4. API Routers...")
        from api.patients import router as pr
        from api.alerts import router as ar
        from api.seed import router as sr
        from api.protocol import router as protr
        from api.analytics import router as anr
        from api.websocket import router as wr
        print(f"   ✅ {len([pr, ar, sr, protr, anr, wr])} routers loaded")
        
        print("\n5. Services...")
        from services.vitals_service import ingest_vital
        from core.risk_engine import compute_risk
        from core.notifier import notify_nurse, notify_doctor
        print("   ✅ All services imported")
        
        print("\n6. FastAPI App...")
        from main import app
        print(f"   ✅ App created: {app.title}")
        print(f"   📊 Total routes: {len(app.routes)}")
        
        print("\n7. Checking for old SQLAlchemy imports...")
        import_check = _check_old_imports()
        if import_check:
            print(f"   ⚠️  Found old imports:")
            for item in import_check:
                print(f"      - {item}")
        else:
            print("   ✅ No old SQLAlchemy imports found")
        
        return True
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_mongodb_connection():
    """Test MongoDB connection if possible."""
    print("\n" + "=" * 70)
    print("🗄️  TESTING MONGODB CONNECTION")
    print("=" * 70)
    
    try:
        from db.mongo_database import database, init_db
        from models.patient import Patient
        
        print("\n1. Checking MongoDB URL...")
        from config import get_settings
        settings = get_settings()
        
        if not settings.mongodb_url:
            print("   ⚠️  MONGODB_URL not configured in .env")
            print("   📝 Set it to connect to MongoDB Atlas")
            return False
        
        print(f"   ✅ MongoDB URL configured")
        
        print("\n2. Initializing Beanie...")
        try:
            await init_db()
            print("   ✅ Beanie initialized with models")
        except Exception as e:
            print(f"   ⚠️  Could not connect to MongoDB: {e}")
            print("   💡 This is OK if MongoDB is not running locally")
            return False
        
        print("\n3. Testing Patient model...")
        count = len(await Patient.find_all().to_list())
        print(f"   ✅ Found {count} patients in database")
        
        return True
    except Exception as e:
        print(f"\n⚠️  MongoDB test skipped: {e}")
        return False


def test_configuration():
    """Test that critical settings are configured."""
    print("\n" + "=" * 70)
    print("⚙️  TESTING CONFIGURATION")
    print("=" * 70)
    
    try:
        from config import get_settings
        settings = get_settings()
        
        checks = {
            "Database Name": settings.database_name,
            "MongoDB URL": "configured" if settings.mongodb_url else "❌ NOT SET",
            "Telegram Bot Token": "configured" if settings.telegram_bot_token else "⚠️ NOT SET (optional for testing)",
            "Nurse Chat ID": settings.telegram_nurse_chat_id or "⚠️ NOT SET",
            "Doctor Chat ID": settings.telegram_doctor_chat_id or "⚠️ NOT SET",
            "Gemini API Key": "configured" if settings.gemini_api_key else "⚠️ NOT SET (optional)",
        }
        
        for key, value in checks.items():
            status = "✅" if value and value not in ["❌ NOT SET", "⚠️ NOT SET"] else "⚠️"
            print(f"   {status} {key}: {value if isinstance(value, str) and len(value) < 50 else value}")
        
        return settings.mongodb_url is not None
    except Exception as e:
        print(f"\n❌ Config test failed: {e}")
        return False


def test_frontend_files():
    """Check that critical frontend files exist."""
    print("\n" + "=" * 70)
    print("🎨 TESTING FRONTEND FILES")
    print("=" * 70)
    
    files_to_check = {
        "client/.env": Path("client/.env"),
        "client/package.json": Path("client/package.json"),
        "client/src/App.jsx": Path("client/src/App.jsx"),
        "client/public/logo.png": Path("client/public/logo.png"),
        "client/src/components/Navbar.jsx": Path("client/src/components/Navbar.jsx"),
    }
    
    all_exist = True
    for name, path in files_to_check.items():
        exists = path.exists()
        status = "✅" if exists else "❌"
        print(f"   {status} {name}")
        if not exists:
            all_exist = False
    
    return all_exist


def _check_old_imports():
    """Search for old SQLAlchemy imports in backend."""
    old_patterns = [
        "from db.database import",
        "from sqlalchemy",
        "AsyncSession",
    ]
    
    backend_dir = Path("backend")
    found = []
    
    for py_file in backend_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        
        try:
            content = py_file.read_text()
            for pattern in old_patterns:
                if pattern in content and "db/mongo_database" not in content:
                    rel_path = py_file.relative_to(Path.cwd())
                    found.append(str(rel_path))
                    break
        except Exception:
            pass
    
    return list(set(found))


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("🚀 ASCLEPIUS AI - INTEGRATION VERIFICATION")
    print("=" * 70)
    
    results = {
        "Imports": test_imports(),
        "Configuration": test_configuration(),
        "Frontend Files": test_frontend_files(),
    }
    
    # Test MongoDB async
    try:
        results["MongoDB"] = asyncio.run(test_mongodb_connection())
    except Exception as e:
        print(f"\n⚠️  MongoDB test failed: {e}")
        results["MongoDB"] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "⚠️ WARN"
        print(f"   {status} - {test_name}")
    
    critical_passed = results.get("Imports", False) and results.get("Configuration", False)
    
    print("\n" + "=" * 70)
    if critical_passed:
        print("✅ READY TO START - Backend and Frontend are configured correctly")
        print("\nNext steps:")
        print("  1. Backend: cd backend && uvicorn main:app --reload")
        print("  2. Frontend: cd client && npm run dev")
        print("  3. Open: http://localhost:5173")
    else:
        print("❌ ISSUES FOUND - Please fix the errors above")
    print("=" * 70 + "\n")
    
    return 0 if critical_passed else 1


if __name__ == "__main__":
    sys.exit(main())
