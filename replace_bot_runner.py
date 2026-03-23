#!/usr/bin/env python3
"""
Replace telegram bot runner with fixed version
"""
import os
import shutil
from pathlib import Path

server_dir = Path(__file__).parent / "server" / "services"
old_file = server_dir / "telegram_bot_runner.py"
new_file = server_dir / "telegram_bot_runner_fixed.py"

try:
    if old_file.exists():
        os.remove(old_file)
        print(f"✅ Removed old file: {old_file}")
    
    if new_file.exists():
        os.rename(new_file, old_file)
        print(f"✅ Renamed {new_file} to {old_file}")
        
    print("🔧 Telegram bot runner has been replaced with fixed version")
    
except Exception as e:
    print(f"❌ Error replacing file: {e}")