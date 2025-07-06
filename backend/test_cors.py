#!/usr/bin/env python3
"""
Test CORS preflight handling
"""

import requests
import json

def test_cors_preflight():
    """Test CORS preflight handling"""
    try:
        # Test OPTIONS request (preflight)
        print("Testing OPTIONS request...")
        response = requests.options('http://localhost:5000/api/overlays', 
                                 headers={'Origin': 'http://localhost:8080'})
        print(f"OPTIONS Status: {response.status_code}")
        print("OPTIONS Headers:")
        for k, v in response.headers.items():
            if 'access-control' in k.lower():
                print(f"  {k}: {v}")
        
        # Test POST request
        print("\nTesting POST request...")
        response = requests.post('http://localhost:5000/api/overlays',
                               headers={'Origin': 'http://localhost:8080', 'Content-Type': 'application/json'},
                               json={'name': 'Test Overlay', 'type': 'text', 'content': 'Test'})
        print(f"POST Status: {response.status_code}")
        print("POST Headers:")
        for k, v in response.headers.items():
            if 'access-control' in k.lower():
                print(f"  {k}: {v}")
        print(f"POST Response: {response.text[:200]}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == '__main__':
    test_cors_preflight() 