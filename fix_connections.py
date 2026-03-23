#!/usr/bin/env python3
"""
🔧 Fix Connection Issues - Asclepius AI
Diagnoses and fixes common connection problems
"""

import asyncio
import httpx
import sys
from pathlib import Path

# Add server to path
server_path = Path(__file__).parent / "server"
sys.path.insert(0, str(server_path))

async def fix_connections():
    """Fix common connection issues"""
    print("🔧 ASCLEPIUS AI CONNECTION FIXER")
    print("=" * 40)
    
    fixes_applied = []
    
    # Fix 1: Test Telegram Bot Token
    print("\n1️⃣ Testing Telegram Bot Token...")
    try:
        from server.config import get_settings
        settings = get_settings()
        
        if not settings.telegram_bot_token:
            print("❌ No Telegram bot token found")
            print("💡 Add TELEGRAM_BOT_TOKEN to server/.env")
        else:
            # Test bot token
            url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/getMe"
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    bot_info = response.json().get("result", {})
                    print(f"✅ Bot token valid: @{bot_info.get('username')}")
                    fixes_applied.append("Telegram bot token verified")
                else:
                    print(f"❌ Invalid bot token: {response.status_code}")
                    print("💡 Check TELEGRAM_BOT_TOKEN in server/.env")
    except Exception as e:
        print(f"❌ Error testing bot: {e}")
    
    # Fix 2: Test Chat IDs
    print("\n2️⃣ Testing Chat IDs...")
    try:
        nurse_id = settings.telegram_nurse_chat_id
        doctor_id = settings.telegram_doctor_chat_id
        
        if nurse_id:
            print(f"✅ Nurse Chat ID configured: {nurse_id}")
        else:
            print("⚠️ Nurse Chat ID not configured")
            print("💡 Add TELEGRAM_NURSE_CHAT_ID to server/.env")
            
        if doctor_id:
            print(f"✅ Doctor Chat ID configured: {doctor_id}")
        else:
            print("⚠️ Doctor Chat ID not configured") 
            print("💡 Add TELEGRAM_DOCTOR_CHAT_ID to server/.env")
            
        if nurse_id and doctor_id:
            fixes_applied.append("Chat IDs configured")
            
    except Exception as e:
        print(f"❌ Error checking chat IDs: {e}")
    
    # Fix 3: Test Database Connection
    print("\n3️⃣ Testing Database Connection...")
    try:
        from server.db.mongodb import init_db
        await init_db()
        print("✅ Database connection successful")
        fixes_applied.append("Database connection working")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("💡 Check MONGODB_URL in server/.env")
    
    # Fix 4: Check if server is running
    print("\n4️⃣ Testing Server Status...")
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get("http://localhost:8000/")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Server running: {data.get('status')}")
                
                # Check bot status
                bot_response = await client.get("http://localhost:8000/telegram/bot/status")
                if bot_response.status_code == 200:
                    bot_data = bot_response.json()
                    if bot_data.get("bot_running"):
                        print("✅ Integrated Telegram bot running")
                        fixes_applied.append("Integrated bot operational")
                    else:
                        print("⚠️ Telegram bot configured but not running")
                        print("💡 Restart server: python start_system.py")
            else:
                print(f"❌ Server returned: {response.status_code}")
    except Exception as e:
        print("⚠️ Server not running")
        print("💡 Start server: python start_system.py")
    
    # Summary
    print("\n" + "=" * 40)
    print("🎯 CONNECTION FIX SUMMARY")
    print("=" * 40)
    
    if fixes_applied:
        for fix in fixes_applied:
            print(f"✅ {fix}")
    else:
        print("❌ No connections working properly")
    
    print(f"\n📊 Status: {len(fixes_applied)}/4 connections working")
    
    # Recommendations
    print("\n💡 RECOMMENDED ACTIONS:")
    
    if len(fixes_applied) < 2:
        print("   🔧 CRITICAL SETUP ISSUES:")
        print("   1. Verify server/.env file has all required settings")
        print("   2. Check Telegram bot token with @BotFather")
        print("   3. Get chat IDs using @userinfobot")
        print("   4. Test MongoDB Atlas connection")
        
    elif len(fixes_applied) < 4:
        print("   ⚠️ MINOR ISSUES:")
        print("   1. Start the server: python start_system.py")
        print("   2. Test Telegram alerts via API endpoints")
        
    else:
        print("   🎉 ALL SYSTEMS OPERATIONAL!")
        print("   1. Start frontend: cd client && npm run dev") 
        print("   2. Open http://localhost:5173")
        print("   3. Test alert buttons in patient cards")
    
    print("\n🧪 TESTING COMMANDS:")
    print("   • Test system: python test_connections.py")
    print("   • Test critical alert: curl -X POST http://localhost:8000/telegram/test/critical")
    print("   • Test warning alert: curl -X POST http://localhost:8000/telegram/test/warning")


if __name__ == "__main__":
    try:
        asyncio.run(fix_connections())
    except KeyboardInterrupt:
        print("\n\n⏹️ Fix interrupted by user")
    except Exception as e:
        print(f"\n❌ Fix script error: {e}")
        print("Make sure you're running from the project root directory")