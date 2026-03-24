#!/usr/bin/env python3
"""
Quick test script for Telegram bot compatibility - Fixed paths
"""
import asyncio
import logging
import sys
import os
from pathlib import Path

# Add current directory and server directory to path  
current_dir = Path(__file__).parent
server_dir = current_dir / "server"
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(server_dir))

logging.basicConfig(level=logging.INFO)

async def test_telegram_bot():
    """Test the Telegram bot compatibility"""
    try:
        print("🧪 Testing Telegram bot compatibility...")
        print(f"Current directory: {os.getcwd()}")
        print(f"Server directory: {server_dir}")
        print(f"Server directory exists: {server_dir.exists()}")
        
        # Test imports
        print("Testing imports...")
        
        try:
            # First test config import
            sys.path.insert(0, str(server_dir))
            import config
            print("✅ Config import successful")
            
            # Test settings
            settings = config.get_settings()
            print(f"✅ Settings loaded")
            print(f"Bot token configured: {'Yes' if settings.telegram_bot_token else 'No'}")
            print(f"Nurse chat ID: {settings.telegram_nurse_chat_id}")
            print(f"Doctor chat ID: {settings.telegram_doctor_chat_id}")
            
        except Exception as e:
            print(f"❌ Config import failed: {e}")
            return
        
        try:
            # Test telegram bot runner import
            from services.telegram_bot_runner import telegram_bot_runner
            print("✅ Telegram bot runner import successful")
            
            # Check configuration
            is_configured = telegram_bot_runner.is_configured()
            print(f"✅ Bot configured: {is_configured}")
            
            if is_configured:
                print("🚀 Starting bot test...")
                success = await telegram_bot_runner.start_bot()
                
                if success:
                    print("✅ Bot started successfully!")
                    print("⏱️  Running for 5 seconds...")
                    await asyncio.sleep(5)
                    
                    print("🛑 Stopping bot...")
                    await telegram_bot_runner.stop_bot()
                    print("✅ Bot stopped successfully!")
                else:
                    print("❌ Bot failed to start")
            else:
                print("⚠️  Bot not configured")
                print("📝 To configure, set these in server/.env:")
                print("   TELEGRAM_BOT_TOKEN=your_bot_token")
                print("   TELEGRAM_NURSE_CHAT_ID=-your_nurse_chat_id") 
                print("   TELEGRAM_DOCTOR_CHAT_ID=-your_doctor_chat_id")
                
        except ImportError as e:
            print(f"❌ Telegram bot import failed: {e}")
            print("Make sure the server/services directory exists")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_telegram_bot())