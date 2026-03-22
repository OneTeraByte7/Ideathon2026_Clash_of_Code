#!/usr/bin/env python3
"""
Simplified server startup script
"""
import os
import sys
import subprocess
from pathlib import Path

# Get directories
project_root = Path(__file__).parent
server_dir = project_root / "server"

print("🚀 Starting Asclepius AI Server...")
print(f"📁 Project root: {project_root}")
print(f"📁 Server dir: {server_dir}")

# Change to server directory
os.chdir(server_dir)
print(f"📁 Working directory: {os.getcwd()}")

# Add server to Python path
sys.path.insert(0, str(server_dir))

# Start uvicorn server
try:
    cmd = [
        sys.executable, "-m", "uvicorn", "main:app", 
        "--reload", "--host", "127.0.0.1", "--port", "8000"
    ]
    print(f"🔧 Running: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=server_dir)
except KeyboardInterrupt:
    print("\n⏹️ Server stopped by user")
except Exception as e:
    print(f"❌ Server error: {e}")