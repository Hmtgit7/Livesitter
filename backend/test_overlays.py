#!/usr/bin/env python3
"""
Test overlays route
"""

import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables
load_dotenv()

def test_overlays_route():
    """Test overlays route specifically"""
    try:
        # Create Flask app
        app = create_app('development')
        
        print("✅ Flask app created successfully")
        
        # Test with app context
        with app.app_context():
            from routes.overlays import get_overlays
            from flask import request
            
            # Mock request
            class MockRequest:
                def __init__(self):
                    self.args = {'page': '1', 'limit': '100'}
            
            # Test the route function directly
            request.args = {'page': '1', 'limit': '100'}
            
            try:
                response = get_overlays()
                print(f"✅ Overlays route response: {response}")
            except Exception as e:
                print(f"❌ Overlays route error: {e}")
                import traceback
                traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_overlays_route() 