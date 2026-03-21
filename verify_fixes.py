#!/usr/bin/env python3
"""
Verification script to check all fixes are in place
"""
import os
import re

def check_file_content(filepath, should_contain=None, should_not_contain=None):
    """Check file content for specific patterns"""
    if not os.path.exists(filepath):
        return False, f"File not found: {filepath}"
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    if should_contain:
        for pattern in should_contain:
            if pattern not in content:
                return False, f"Missing: {pattern}"
    
    if should_not_contain:
        for pattern in should_not_contain:
            if pattern in content:
                return False, f"Should not contain: {pattern}"
    
    return True, "OK"

print("=" * 70)
print("🔍 VERIFYING MONGODB MIGRATION & CLIENT-SERVER FIXES")
print("=" * 70)

checks = [
    # Backend API imports
    {
        "name": "backend/api/patients.py - No SQLAlchemy",
        "file": "backend/api/patients.py",
        "should_not_contain": ["from sqlalchemy", "AsyncSession", "Depends, HTTPException"],
        "should_contain": ["from fastapi import APIRouter, HTTPException"]
    },
    {
        "name": "backend/api/alerts.py - No SQLAlchemy",
        "file": "backend/api/alerts.py",
        "should_not_contain": ["from sqlalchemy", "AsyncSession"],
        "should_contain": ["from fastapi import APIRouter, HTTPException"]
    },
    {
        "name": "client/src/hooks/useICUStream.js - Closure fixed",
        "file": "client/src/hooks/useICUStream.js",
        "should_contain": ["connectRef.current = connect;", "useEffect"],
        "should_not_contain": ["connectRef.current?.()"]
    },
    {
        "name": "client/src/App.jsx - Motion import fixed",
        "file": "client/src/App.jsx",
        "should_contain": ["import { AnimatePresence, motion }", "motion.div"],
        "should_not_contain": ["motion as Motion", "Motion.div"]
    },
    {
        "name": "backend/.env - Nurse chat ID updated",
        "file": "backend/.env",
        "should_contain": ["TELEGRAM_NURSE_CHAT_ID=-5144644074"],
        "should_not_contain": ["TELEGRAM_NURSE_CHAT_ID=-5269000368"]
    },
    {
        "name": "backend/db/mongo_database.py - Exports correct",
        "file": "backend/db/mongo_database.py",
        "should_contain": ["def get_db_connection()", "async def init_db()"],
    },
]

all_pass = True
for check in checks:
    result, msg = check_file_content(
        check["file"],
        should_contain=check.get("should_contain"),
        should_not_contain=check.get("should_not_contain")
    )
    
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"\n{status} - {check['name']}")
    if not result:
        print(f"   Error: {msg}")
        all_pass = False

print("\n" + "=" * 70)
if all_pass:
    print("✅ ALL CHECKS PASSED - System is ready!")
    print("\nNext steps:")
    print("1. Start backend:  cd backend && uvicorn main:app --reload")
    print("2. Seed patients:  python backend/seed_patients.py")
    print("3. Trigger alert:  curl -X POST http://localhost:8000/seed/critical")
    print("4. Start frontend: cd client && npm run dev")
    print("\n5. Monitor Telegram chats:")
    print("   - Doctor (-5294441613): Should receive critical alerts")
    print("   - Nurse (-5144644074): Should receive all alerts")
else:
    print("❌ SOME CHECKS FAILED - Please review errors above")

print("=" * 70)
