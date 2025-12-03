#!/usr/bin/env python3
"""
Test script for Tamil Panchang API
"""

import requests
import json
from datetime import date

API_BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing /health endpoint...")
    response = requests.get(f"{API_BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_panchang():
    """Test panchang endpoint"""
    print("Testing /api/panchang endpoint...")
    
    payload = {
        "date": "2024-11-27",
        "latitude": 10.7905,  # Trichy
        "longitude": 78.7047,
        "timezone": 5.5
    }
    
    response = requests.post(
        f"{API_BASE_URL}/api/panchang",
        json=payload
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
    print()

def test_today():
    """Test today endpoint"""
    print("Testing /api/today endpoint...")
    
    payload = {
        "latitude": 13.0827,  # Chennai
        "longitude": 80.2707,
        "timezone": 5.5
    }
    
    response = requests.post(
        f"{API_BASE_URL}/api/today",
        json=payload
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
    print()

def main():
    print("=" * 50)
    print("Tamil Panchang API Tests")
    print("=" * 50)
    print()
    
    try:
        test_health()
        test_panchang()
        test_today()
        print("✅ All tests passed!")
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API")
        print("Make sure the API is running: docker-compose up -d")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
