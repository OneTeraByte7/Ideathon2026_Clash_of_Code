#!/usr/bin/env python3
"""
Start script for Asclepius AI server
"""
import sys
import os
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent
server_dir = project_root / "server"

# Add server directory to Python path
sys.path.insert(0, str(server_dir))

# Change to server directory for relative imports
os.chdir(server_dir)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Asclepius AI server...")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"🐍 Python path includes: {server_dir}")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)