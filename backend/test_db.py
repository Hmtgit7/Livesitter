#!/usr/bin/env python3
"""
Test database connection
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

def test_db_connection():
    """Test MongoDB connection"""
    try:
        # Get MongoDB URI from environment
        mongodb_uri = os.getenv('MONGODB_URI')
        database_name = os.getenv('DATABASE_NAME')
        
        print(f"MongoDB URI: {mongodb_uri}")
        print(f"Database Name: {database_name}")
        
        if not mongodb_uri:
            print("ERROR: MONGODB_URI not found in environment")
            return False
        
        # Connect to MongoDB
        client = MongoClient(mongodb_uri)
        
        # Test connection
        client.admin.command('ping')
        print("✅ MongoDB connection successful")
        
        # Test database access
        db = client[database_name]
        collection = db['overlays']
        print(f"✅ Database '{database_name}' accessible")
        print(f"✅ Collection 'overlays' accessible")
        
        # Test a simple query
        count = collection.count_documents({})
        print(f"✅ Collection has {count} documents")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == '__main__':
    test_db_connection() 