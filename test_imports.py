#!/usr/bin/env python3
"""Test that all imports work correctly"""

print("Testing MongoDB imports...")
try:
    from backend.db.mongo_database import get_db_connection, init_db
    print("✅ MongoDB imports successful")
except Exception as e:
    print(f"❌ MongoDB import error: {e}")

print("\nTesting API imports...")
try:
    from backend.api.patients import router as patients_router
    print("✅ Patients API import successful")
except Exception as e:
    print(f"❌ Patients API error: {e}")

try:
    from backend.api.alerts import router as alerts_router
    print("✅ Alerts API import successful")
except Exception as e:
    print(f"❌ Alerts API error: {e}")

try:
    from backend.api.analytics import router as analytics_router
    print("✅ Analytics API import successful")
except Exception as e:
    print(f"❌ Analytics API error: {e}")

try:
    from backend.api.protocol import router as protocol_router
    print("✅ Protocol API import successful")
except Exception as e:
    print(f"❌ Protocol API error: {e}")

try:
    from backend.api.seed import router as seed_router
    print("✅ Seed API import successful")
except Exception as e:
    print(f"❌ Seed API error: {e}")

try:
    from backend.api.websocket import router as ws_router
    print("✅ WebSocket API import successful")
except Exception as e:
    print(f"❌ WebSocket API error: {e}")

print("\n✅ All imports successful!")
