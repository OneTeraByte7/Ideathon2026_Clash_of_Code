#!/usr/bin/env python3
"""Test script to identify import issues"""

import sys
import os

# Add server to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    print("Testing basic imports...")
    
    # Test config
    try:
        from config import get_settings
        print("✅ config import successful")
    except Exception as e:
        print(f"❌ config import failed: {e}")
    
    # Test database
    try:
        from db.mongodb import init_db, close_db
        print("✅ database import successful")
    except Exception as e:
        print(f"❌ database import failed: {e}")
    
    # Test services
    try:
        from services.telegram_service import TelegramService
        print("✅ telegram service import successful")
    except Exception as e:
        print(f"❌ telegram service import failed: {e}")
    
    # Test API routes
    try:
        from api.patients import router as patients_router
        print("✅ patients API import successful")
    except Exception as e:
        print(f"❌ patients API import failed: {e}")
    
    try:
        from api.alerts import router as alerts_router  
        print("✅ alerts API import successful")
    except Exception as e:
        print(f"❌ alerts API import failed: {e}")
    
    try:
        from api.seed import router as seed_router
        print("✅ seed API import successful")
    except Exception as e:
        print(f"❌ seed API import failed: {e}")
    
    try:
        from api.protocol import router as protocol_router
        print("✅ protocol API import successful")
    except Exception as e:
        print(f"❌ protocol API import failed: {e}")
    
    try:
        from api.websocket import router as ws_router
        print("✅ websocket API import successful")
    except Exception as e:
        print(f"❌ websocket API import failed: {e}")
    
    try:
        from api.analytics import router as analytics_router
        print("✅ analytics API import successful")
    except Exception as e:
        print(f"❌ analytics API import failed: {e}")
    
    print("\n🎉 All imports tested!")
    
except Exception as e:
    print(f"❌ Main test failed: {e}")
    import traceback
    traceback.print_exc()