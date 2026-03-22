@echo off
echo 🎨 Starting Asclepius AI Client...
cd /d "%~dp0\client"
echo 📁 Working directory: %CD%
npm run dev
pause