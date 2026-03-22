#!/usr/bin/env python3
"""
Quick test script to verify Asclepius AI API endpoints
"""
import requests
import json

BASE_URL = "https://ideathon2026-clash-of-code.onrender.com"

def test_api():
    print("🧪 Testing Asclepius AI API...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"✅ Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test patients endpoint
    try:
        response = requests.get(f"{BASE_URL}/patients/", timeout=10)
        print(f"✅ Patients endpoint: {response.status_code}")
        if response.status_code == 200:
            patients = response.json()
            print(f"   Found {len(patients)} patients")
            if patients:
                patient_id = patients[0].get('id')
                print(f"   First patient ID: {patient_id}")
                
                # Test critical alert trigger
                if patient_id:
                    try:
                        alert_response = requests.post(f"{BASE_URL}/patients/{patient_id}/trigger-critical", timeout=10)
                        print(f"✅ Critical alert test: {alert_response.status_code}")
                        if alert_response.status_code == 200:
                            result = alert_response.json()
                            print(f"   Alert message: {result.get('message')}")
                            print(f"   Telegram results: {result.get('telegram_notifications')}")
                    except Exception as e:
                        print(f"❌ Critical alert test failed: {e}")
    except Exception as e:
        print(f"❌ Patients endpoint failed: {e}")
    
    # Test Telegram configuration
    try:
        response = requests.get(f"{BASE_URL}/telegram/config", timeout=10)
        print(f"✅ Telegram config: {response.status_code}")
        if response.status_code == 200:
            config = response.json()
            print(f"   Bot configured: {config.get('is_configured')}")
            print(f"   Doctor chat: {config.get('config_values', {}).get('doctor_chat_id')}")
            print(f"   Nurse chat: {config.get('config_values', {}).get('nurse_chat_id')}")
    except Exception as e:
        print(f"❌ Telegram config failed: {e}")
    
    print("\n🎯 API Testing Complete!")

if __name__ == "__main__":
    test_api()