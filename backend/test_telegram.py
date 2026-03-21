#!/usr/bin/env python3
"""
Test Telegram Bot - Get chat info and test messages
Run this to debug the Telegram nurse chat issue
"""
import asyncio
import httpx
from config import get_settings

settings = get_settings()

async def get_bot_info():
    """Get bot information"""
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/getMe"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            result = response.json()
            if result.get('ok'):
                bot_info = result['result']
                print("✅ Bot Info:")
                print(f"   Name: {bot_info.get('first_name')}")
                print(f"   Username: @{bot_info.get('username')}")
                print(f"   ID: {bot_info.get('id')}")
                return True
            else:
                print(f"❌ Failed to get bot info: {result}")
                return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def get_updates():
    """Get recent updates to see available chats"""
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/getUpdates"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            result = response.json()
            if result.get('ok'):
                updates = result['result']
                print(f"\n📢 Recent Updates ({len(updates)} messages):")
                
                chats = {}
                for update in updates[-10:]:  # Last 10 updates
                    if 'message' in update:
                        chat = update['message']['chat']
                        chat_id = chat['id']
                        chat_type = chat['type']
                        chat_title = chat.get('title', chat.get('first_name', 'Unknown'))
                        chats[chat_id] = {'type': chat_type, 'title': chat_title}
                
                if chats:
                    print("\n📝 Available Chats:")
                    for chat_id, info in chats.items():
                        print(f"   ID: {chat_id} | Type: {info['type']} | Name: {info['title']}")
                else:
                    print("   No recent chat activity found")
                    print("   💡 Send a message to the bot in any chat to see it here")
                
                return True
            else:
                print(f"❌ Failed to get updates: {result}")
                return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_chat(chat_id: str, chat_name: str = "test"):
    """Test sending message to a specific chat"""
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": f"🔧 **Asclepius Test Message**\n\nThis is a test from the Asclepius AI system.\nTime: {asyncio.get_event_loop().time():.0f}\n\nIf you received this, the bot is working correctly! ✅",
        "parse_mode": "Markdown"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)
            result = response.json()
            if result.get('ok'):
                print(f"✅ Test message sent to {chat_name} ({chat_id})")
                return True
            else:
                error = result.get('description', 'Unknown error')
                print(f"❌ Failed to send to {chat_name} ({chat_id}): {error}")
                return False
    except Exception as e:
        print(f"❌ Error sending to {chat_name}: {e}")
        return False

async def main():
    print("🤖 Telegram Bot Test - Asclepius AI")
    print("=" * 50)
    
    if not settings.telegram_bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not configured in .env")
        return
    
    print(f"Bot Token: {settings.telegram_bot_token[:20]}...")
    print(f"Nurse Chat ID: {settings.telegram_nurse_chat_id}")
    print(f"Doctor Chat ID: {settings.telegram_doctor_chat_id}")
    
    # Test bot connectivity
    print("\n1️⃣ Testing bot connectivity...")
    if not await get_bot_info():
        print("❌ Bot token is invalid or network issue")
        return
    
    # Get available chats
    print("\n2️⃣ Getting chat list...")
    await get_updates()
    
    # Test configured chats
    print("\n3️⃣ Testing configured chats...")
    
    if settings.telegram_nurse_chat_id:
        await test_chat(settings.telegram_nurse_chat_id, "Nurse Chat")
    else:
        print("⚠️ Nurse chat ID not configured")
    
    if settings.telegram_doctor_chat_id:
        await test_chat(settings.telegram_doctor_chat_id, "Doctor Chat")
    else:
        print("⚠️ Doctor chat ID not configured")
    
    print("\n" + "=" * 50)
    print("💡 Instructions:")
    print("1. If chats show as 'not found', create new Telegram groups")
    print("2. Add the bot to both groups as admin")
    print("3. Send a message in each group, then run this script again")
    print("4. Update .env with the correct chat IDs from the list above")

if __name__ == "__main__":
    asyncio.run(main())