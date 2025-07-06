#!/usr/bin/env python3
"""
Test script for HLS generation and backend functionality
"""

import requests
import json
import time
import os

# Configuration
BASE_URL = "https://livesitter-yeop.onrender.com"
# BASE_URL = "http://localhost:5000"  # For local testing

def test_backend_health():
    """Test backend health"""
    print("Testing backend health...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print("✅ Backend is healthy")
            return True
        else:
            print("❌ Backend health check failed")
            return False
    except Exception as e:
        print(f"❌ Backend health check error: {e}")
        return False

def test_stream_creation():
    """Test stream creation"""
    print("\nTesting stream creation...")
    try:
        stream_data = {
            "name": "Test Stream",
            "rtsp_url": "rtsp://rtsp.stream/pattern",
            "settings": {
                "quality": "medium",
                "fps": 30,
                "resolution": "720p"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/streams",
            json=stream_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Create stream: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            stream_id = data['data']['_id']
            print(f"✅ Stream created with ID: {stream_id}")
            return stream_id
        else:
            print(f"❌ Stream creation failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Stream creation error: {e}")
        return None

def test_stream_start(stream_id):
    """Test stream start"""
    print(f"\nTesting stream start for {stream_id}...")
    try:
        response = requests.post(f"{BASE_URL}/api/streams/{stream_id}/start")
        
        print(f"Start stream: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            hls_url = data['data']['hls_url']
            print(f"✅ Stream started with HLS URL: {hls_url}")
            return hls_url
        else:
            print(f"❌ Stream start failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Stream start error: {e}")
        return None

def test_hls_access(stream_id):
    """Test HLS file access"""
    print(f"\nTesting HLS access for {stream_id}...")
    try:
        hls_url = f"{BASE_URL}/api/streams/hls/{stream_id}/playlist.m3u8"
        response = requests.get(hls_url)
        
        print(f"HLS access: {response.status_code}")
        if response.status_code == 200:
            print("✅ HLS file accessible")
            print(f"Content: {response.text[:200]}...")
            return True
        else:
            print(f"❌ HLS file not accessible: {response.text}")
            return False
    except Exception as e:
        print(f"❌ HLS access error: {e}")
        return False

def test_hls_creation(stream_id):
    """Test HLS file creation using test endpoint"""
    print(f"\nTesting HLS creation for {stream_id}...")
    try:
        response = requests.get(f"{BASE_URL}/api/streams/test-hls/{stream_id}")
        
        print(f"Test HLS creation: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Test HLS files created: {data['message']}")
            return True
        else:
            print(f"❌ Test HLS creation failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Test HLS creation error: {e}")
        return False

def test_stream_status(stream_id):
    """Test stream status"""
    print(f"\nTesting stream status for {stream_id}...")
    try:
        response = requests.get(f"{BASE_URL}/api/streams/{stream_id}/status")
        
        print(f"Stream status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            status = data['data']
            print(f"✅ Stream status: {status}")
            return status
        else:
            print(f"❌ Stream status failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Stream status error: {e}")
        return None

def main():
    """Run all tests"""
    print("🚀 Starting backend tests...")
    
    # Test 1: Health check
    if not test_backend_health():
        return
    
    # Test 2: Create stream
    stream_id = test_stream_creation()
    if not stream_id:
        return
    
    # Test 3: Test HLS creation (before starting stream)
    test_hls_creation(stream_id)
    
    # Test 4: Start stream
    hls_url = test_stream_start(stream_id)
    if not hls_url:
        return
    
    # Test 5: Check stream status
    status = test_stream_status(stream_id)
    
    # Test 6: Try to access HLS file
    time.sleep(5)  # Wait for HLS files to be generated
    test_hls_access(stream_id)
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    main() 