#!/usr/bin/env python3
"""
Test script for Tamil Panchang API
"""

import json

import requests

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
        "timezone": 5.5,
    }

    response = requests.post(f"{API_BASE_URL}/api/panchang", json=payload, timeout=10)

    print(f"Status: {response.status_code}")
    print("Response:")
    print(json.dumps(response.json(), indent=2))
    print()


def test_today():
    """Test today endpoint"""
    print("Testing /api/today endpoint...")

    payload = {
        "latitude": 13.0827,  # Chennai
        "longitude": 80.2707,
        "timezone": 5.5,
    }

    response = requests.post(f"{API_BASE_URL}/api/today", json=payload, timeout=10)

    print(f"Status: {response.status_code}")
    print("Response:")
    print(json.dumps(response.json(), indent=2))
    print()


def test_muhurta():
    """Test muhurta endpoint for each supported activity"""
    print("Testing /api/muhurta endpoint...")

    for activity in ("general", "griha_pravesam", "bhoomi_pooja"):
        payload = {
            "start_date": "2026-05-01",
            "end_date": "2026-05-15",
            "latitude": 10.7905,  # Trichy
            "longitude": 78.7047,
            "timezone": 5.5,
            "activity": activity,
        }

        response = requests.post(f"{API_BASE_URL}/api/muhurta", json=payload, timeout=10)
        assert response.status_code == 200, (
            f"activity={activity} returned {response.status_code}: {response.text}"
        )
        data = response.json()
        assert data["activity"] == activity
        assert data["total_days_scanned"] == 15
        assert data["qualifying_count"] == len(data["qualifying_dates"])

        print(f"  {activity}: {data['qualifying_count']} qualifying date(s) of 15 scanned")

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
        test_muhurta()
        print("✅ All tests passed!")
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API")
        print("Make sure the API is running: docker-compose up -d")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
