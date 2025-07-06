#!/usr/bin/env python3
"""
Test Flask app
"""

import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables
load_dotenv()

def test_flask_app():
    """Test Flask app creation and configuration"""
    try:
        # Create Flask app
        app = create_app('development')
        
        print("✅ Flask app created successfully")
        print(f"✅ CORS_ORIGINS: {app.config.get('CORS_ORIGINS')}")
        print(f"✅ MONGODB_URI: {app.config.get('MONGODB_URI')}")
        print(f"✅ DATABASE_NAME: {app.config.get('DATABASE_NAME')}")
        
        # Test with app context
        with app.app_context():
            from utils.database import get_collection
            collection = get_collection('overlays')
            print(f"✅ Database collection accessible: {collection.name}")
            
            # Test a simple query
            count = collection.count_documents({})
            print(f"✅ Collection query successful: {count} documents")
        
        return True
        
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_flask_app() 