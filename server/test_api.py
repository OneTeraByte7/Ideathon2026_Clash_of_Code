#!/usr/bin/env python3
"""
Quick test script to verify API endpoints are working
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(endpoint, method="GET", data=None):
    """Test a single endpoint"""
    try:
        url = f"{BASE_URL}{endpoint}"
        print(f"Testing {method} {endpoint}...")
        
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print("  ✅ SUCCESS")
        else:
            print("  ❌ FAILED")
            print(f"  Error: {response.text[:200]}")
        print()
        
    except requests.exceptions.RequestException as e:
        print(f"  ❌ CONNECTION ERROR: {e}")
        print()

if __name__ == "__main__":
    print("🏥 Testing Asclepius AI API Endpoints...\n")
    
    # Test core endpoints
    test_endpoint("/")
    test_endpoint("/health")
    test_endpoint("/patients/")
    test_endpoint("/alerts/")
    test_endpoint("/protocols/pending")
    test_endpoint("/analytics/stats")
    
    # Test seed endpoints (POST)
    test_endpoint("/seed/normal", "POST")
    
    print("🎯 API Test Complete!")