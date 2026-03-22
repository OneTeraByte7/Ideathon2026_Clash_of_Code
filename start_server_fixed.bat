@echo off
cd /d E:\Ideathon2026\server
python -m uvicorn main_fixed:app --host 127.0.0.1 --port 8000 --reload