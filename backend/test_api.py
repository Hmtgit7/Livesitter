#!/usr/bin/env python3
"""
Simple test script for the Livesitter API
Run this after starting the Flask server
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoints"""
    print("Testing health endpoints...")
    
    # Test overall health
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Health check: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {data.get('status')}")
        print(f"Database: {data.get('database')}")
        print(f"Active streams: {data.get('active_streams')}")
    
    # Test database health
    response = requests.get(f"{BASE_URL}/api/health/database")
    print(f"Database health: {response.status_code}")
    
    # Test streams health
    response = requests.get(f"{BASE_URL}/api/health/streams")
    print(f"Streams health: {response.status_code}")
    print()

def test_overlays():
    """Test overlay endpoints"""
    print("Testing overlay endpoints...")
    
    # Create overlay
    overlay_data = {
        "name": "Test Logo",
        "type": "logo",
        "content": "https://example.com/logo.png",
        "position": {"x": 10, "y": 10},
        "size": {"width": 100, "height": 50},
        "style": {
            "fontSize": 16,
            "color": "#ffffff",
            "fontFamily": "Arial",
            "opacity": 1.0,
            "backgroundColor": "transparent",
            "borderColor": "transparent",
            "borderWidth": 0
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/overlays",
        json=overlay_data,
        headers={"Content-Type": "application/json"}
    )
    print(f"Create overlay: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        overlay_id = data['data']['_id']
        print(f"Created overlay ID: {overlay_id}")
        
        # Get overlay
        response = requests.get(f"{BASE_URL}/api/overlays/{overlay_id}")
        print(f"Get overlay: {response.status_code}")
        
        # Update overlay
        update_data = overlay_data.copy()
        update_data["name"] = "Updated Logo"
        update_data["position"] = {"x": 20, "y": 20}
        
        response = requests.put(
            f"{BASE_URL}/api/overlays/{overlay_id}",
            json=update_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Update overlay: {response.status_code}")
        
        # Get all overlays
        response = requests.get(f"{BASE_URL}/api/overlays")
        print(f"Get all overlays: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total overlays: {data['pagination']['total']}")
        
        # Delete overlay
        response = requests.delete(f"{BASE_URL}/api/overlays/{overlay_id}")
        print(f"Delete overlay: {response.status_code}")
    
    print()

def test_streams():
    """Test stream endpoints"""
    print("Testing stream endpoints...")
    
    # Create stream
    stream_data = {
        "name": "Test Stream",
        "rtsp_url": "rtsp://rtsp.stream/pattern",
        "settings": {
            "quality": "medium",
            "fps": 30,
            "resolution": "720p",
            "bitrate": "1000k"
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
        print(f"Created stream ID: {stream_id}")
        
        # Get stream
        response = requests.get(f"{BASE_URL}/api/streams/{stream_id}")
        print(f"Get stream: {response.status_code}")
        
        # Get stream status
        response = requests.get(f"{BASE_URL}/api/streams/{stream_id}/status")
        print(f"Get stream status: {response.status_code}")
        
        # Start stream (this might fail if FFmpeg is not available)
        print("Attempting to start stream...")
        response = requests.post(f"{BASE_URL}/api/streams/{stream_id}/start")
        print(f"Start stream: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Stream started: {data['data']['hls_url']}")
            
            # Wait a bit for stream to start
            time.sleep(2)
            
            # Get stream status again
            response = requests.get(f"{BASE_URL}/api/streams/{stream_id}/status")
            print(f"Updated stream status: {response.status_code}")
            
            # Stop stream
            response = requests.post(f"{BASE_URL}/api/streams/{stream_id}/stop")
            print(f"Stop stream: {response.status_code}")
        
        # Get all streams
        response = requests.get(f"{BASE_URL}/api/streams")
        print(f"Get all streams: {response.status_code}")
        
        # Delete stream
        response = requests.delete(f"{BASE_URL}/api/streams/{stream_id}")
        print(f"Delete stream: {response.status_code}")
    
    print()

def test_api_docs():
    """Test API documentation endpoint"""
    print("Testing API documentation...")
    
    response = requests.get(f"{BASE_URL}/api/docs")
    print(f"API docs: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("Available endpoints:")
        for category, endpoints in data['endpoints'].items():
            print(f"  {category}:")
            for endpoint, description in endpoints.items():
                print(f"    {endpoint}: {description}")
    
    print()

def main():
    """Run all tests"""
    print("Livesitter API Test Script")
    print("=" * 40)
    print()
    
    try:
        # Test if server is running
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print(f"Server not responding: {response.status_code}")
            return
        
        print("Server is running!")
        print()
        
        # Run tests
        test_health()
        test_overlays()
        test_streams()
        test_api_docs()
        
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server.")
        print("Make sure the Flask server is running on http://localhost:5000")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 