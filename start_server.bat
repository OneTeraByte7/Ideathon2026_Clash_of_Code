@echo off
echo 🚀 Starting Asclepius AI Server...
cd /d "%~dp0\server"
echo 📁 Working directory: %CD%
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
pause