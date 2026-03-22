#!/usr/bin/env python3
"""
Simple startup script for Asclepius AI
"""
import os
import sys
import asyncio
import uvicorn
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

if __name__ == "__main__":
    print("🏥 Starting Asclepius AI Server...")
    print(f"📁 Working directory: {current_dir}")
    print(f"🐍 Python path includes: {current_dir}")
    
    # Change to server directory
    os.chdir(current_dir)
    
    try:
        # Import and start the app
        from main import app
        
        print("✅ Main app imported successfully")
        print("🚀 Starting server on http://0.0.0.0:8000")
        print("📖 API docs: http://0.0.0.0:8000/docs")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=int(os.getenv("PORT", 8000)),
            reload=False,  # Disable reload for stability
            access_log=True
        )
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("🔍 Running diagnostics...")
        
        # Try to identify the issue
        try:
            exec(open("test_imports.py").read())
        except Exception as test_e:
            print(f"❌ Diagnostics failed: {test_e}")
    except Exception as e:
        print(f"❌ Startup error: {e}")
        import traceback
        traceback.print_exc()