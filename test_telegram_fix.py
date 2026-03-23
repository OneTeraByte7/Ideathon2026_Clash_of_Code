#!/usr/bin/env python3
"""
Test the fixed Telegram bot runner
"""
import asyncio
import sys
from pathlib import Path

# Add server to path
server_path = Path(__file__).parent / "server"
sys.path.insert(0, str(server_path))

async def test_telegram_fix():
    """Test the fixed telegram bot implementation"""
    print("🧪 TESTING FIXED TELEGRAM BOT")
    print("=" * 40)
    
    try:
        # Import the fixed bot runner
        from server.services.telegram_bot_runner import telegram_bot_runner
        print("✅ Successfully imported fixed telegram_bot_runner")
        
        # Test configuration check
        is_configured = telegram_bot_runner.is_configured()
        print(f"📱 Bot configured: {is_configured}")
        
        if is_configured:
            print("🤖 Bot configuration looks good!")
            print("🚀 Ready to start with the server")
        else:
            print("⚠️ Bot not configured - check .env file")
            
        print("\n💡 NEXT STEPS:")
        print("   1. Stop any running server (Ctrl+C)")
        print("   2. Start server: python start_system.py")
        print("   3. Look for '✅ Telegram bot started successfully'")
        print("   4. Test buttons should now work!")
        
    except Exception as e:
        print(f"❌ Error testing bot: {e}")
        print("💡 Make sure you're running from project root")

if __name__ == "__main__":
    try:
        asyncio.run(test_telegram_fix())
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted")
    except Exception as e:
        print(f"\n❌ Test error: {e}")