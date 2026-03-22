#!/usr/bin/env python3
"""
Test script to check server imports and basic functionality
"""
import sys
import os
from pathlib import Path

# Add server to path
server_dir = Path(__file__).parent / "server"
sys.path.insert(0, str(server_dir))
os.chdir(server_dir)

print("🔍 Testing imports...")

try:
    print("1. Testing config...")
    from config import get_settings
    settings = get_settings()
    print(f"   ✅ Config loaded")
    print(f"   📊 MongoDB: {'✅' if settings.mongodb_url else '❌'}")
    print(f"   🤖 Telegram: {'✅' if settings.telegram_bot_token else '❌'}")
    
    print("2. Testing database...")
    from db.mongodb import init_db
    print("   ✅ Database imports OK")
    
    print("3. Testing Telegram service...")
    from services.telegram_service import TelegramService
    telegram = TelegramService()
    print(f"   ✅ Telegram service loaded")
    print(f"   🔧 Configured: {telegram.is_configured()}")
    
    print("4. Testing API routers...")
    from api.patients import router as patients_router
    from api.alerts import router as alerts_router
    from api.protocol import router as protocol_router
    print("   ✅ API routers loaded")
    
    print("5. Testing main app...")
    from main import app
    print("   ✅ FastAPI app loaded successfully!")
    
    print("\n🎉 All imports successful! Server should work.")
    
except Exception as e:
    print(f"\n❌ Import error: {e}")
    import traceback
    traceback.print_exc()