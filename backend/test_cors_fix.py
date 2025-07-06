#!/usr/bin/env python3
"""
Test script to verify CORS configuration is working correctly
"""
import requests
import json

def test_cors_preflight():
    """Test CORS preflight requests"""
    base_url = "http://localhost:5000"
    
    # Test OPTIONS request to streams endpoint
    print("Testing OPTIONS request to /api/streams...")
    try:
        response = requests.options(
            f"{base_url}/api/streams",
            headers={
                'Origin': 'http://localhost:8080',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print("✓ OPTIONS request successful")
    except Exception as e:
        print(f"✗ OPTIONS request failed: {e}")
    
    # Test OPTIONS request to overlays endpoint
    print("\nTesting OPTIONS request to /api/overlays...")
    try:
        response = requests.options(
            f"{base_url}/api/overlays",
            headers={
                'Origin': 'http://localhost:8080',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print("✓ OPTIONS request successful")
    except Exception as e:
        print(f"✗ OPTIONS request failed: {e}")
    
    # Test actual POST request to streams
    print("\nTesting POST request to /api/streams...")
    try:
        response = requests.post(
            f"{base_url}/api/streams",
            headers={
                'Origin': 'http://localhost:8080',
                'Content-Type': 'application/json'
            },
            json={
                'name': 'Test Stream',
                'rtsp_url': 'rtsp://test.com/stream',
                'user_id': 'test'
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        print("✓ POST request successful")
    except Exception as e:
        print(f"✗ POST request failed: {e}")

if __name__ == "__main__":
    test_cors_preflight() 