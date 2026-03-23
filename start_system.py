#!/usr/bin/env python3
"""
🚀 Asclepius AI - Single Command Startup
Starts the complete medical alert system in one command
"""

import os
import sys
import subprocess
import time
import asyncio
from pathlib import Path

def print_banner():
    """Print startup banner"""
    print("""
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│        🏥 ASCLEPIUS AI - ICU SEPSIS EARLY WARNING SYSTEM       │
│                                                                 │
│        🚀 Single Command Startup - Everything Integrated        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
""")

def check_requirements():
    """Check if Python dependencies are installed"""
    print("🔧 Checking requirements...")
    
    try:
        import fastapi
        import uvicorn
        import motor
        import telegram
        print("✅ All Python dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("📦 Installing requirements...")
        
        # Install server requirements
        server_path = Path(__file__).parent / "server"
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", 
            str(server_path / "requirements.txt")
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Requirements installed successfully")
            return True
        else:
            print(f"❌ Failed to install requirements: {result.stderr}")
            return False

def start_integrated_server():
    """Start the integrated FastAPI server with Telegram bot"""
    print("🚀 Starting integrated server with Telegram bot...")
    
    server_path = Path(__file__).parent / "server"
    os.chdir(server_path)
    
    # Import and run server
    try:
        sys.path.insert(0, str(server_path))
        import uvicorn
        from main import app
        
        print("🌐 Server starting on http://localhost:8000")
        print("📱 Telegram bot will start automatically")
        print("🔗 API Documentation: http://localhost:8000/docs")
        print("💊 System Status: http://localhost:8000")
        print("🧪 Test Endpoints:")
        print("   • Critical Alert Test: http://localhost:8000/telegram/test/critical")
        print("   • Warning Alert Test: http://localhost:8000/telegram/test/warning")
        print("\n" + "="*60)
        print("🏥 ASCLEPIUS AI SYSTEM OPERATIONAL")
        print("="*60)
        print("\n📋 Next Steps:")
        print("   1. Open http://localhost:8000 to verify system status")
        print("   2. Test Telegram: POST to /telegram/test/critical")
        print("   3. Start frontend: cd client && npm run dev")
        print("   4. Open http://localhost:5173 for dashboard")
        print("   5. Test alert buttons in patient cards")
        print("\n⏹️ Press Ctrl+C to stop all services")
        print("-"*60)
        
        # Start the server with integrated bot
        uvicorn.run(
            app,
            host="0.0.0.0", 
            port=8000, 
            reload=False,  # Disable reload to keep Telegram bot stable
            log_level="info",
            access_log=False  # Reduce noise
        )
        
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down Asclepius AI system...")
        print("✅ All services stopped")
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        print("💡 Try running: pip install -r server/requirements.txt")

def main():
    """Main startup function"""
    print_banner()
    
    # Check if we're in the right directory
    if not Path("server").exists():
        print("❌ Please run this script from the project root directory")
        print("   Expected structure: project_root/server/")
        sys.exit(1)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Start integrated server
    start_integrated_server()

if __name__ == "__main__":
    main()