#!/usr/bin/env python3
"""
Simple server startup script for testing
"""
import os
import sys
import subprocess

def main():
    print("🏥 Starting Asclepius AI Server...")
    
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("❌ Please run this from the server directory")
        sys.exit(1)
    
    # Try to start with uvicorn
    try:
        subprocess.run([
            "python", "-m", "uvicorn", 
            "main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()