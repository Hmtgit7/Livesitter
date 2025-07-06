#!/usr/bin/env python3
"""
Test script to check database connection and identify the issue
"""
import os
import sys
from pymongo import MongoClient
from pymongo.database import Database

def test_mongodb_connection():
    """Test MongoDB connection"""
    print("Testing MongoDB connection...")
    
    # Get MongoDB URI from environment or use default
    mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/livesitter')
    database_name = os.environ.get('DATABASE_NAME', 'livesitter')
    
    print(f"MongoDB URI: {mongodb_uri}")
    print(f"Database Name: {database_name}")
    
    try:
        # Test connection
        client = MongoClient(mongodb_uri)
        db = client[database_name]
        
        # Test ping
        client.admin.command('ping')
        print("✓ MongoDB connection successful")
        
        # Test collection access
        collection = db['streams']
        print("✓ Collection access successful")
        
        # Test insert (will be rolled back)
        test_doc = {'test': 'data', 'timestamp': '2025-07-06'}
        result = collection.insert_one(test_doc)
        print(f"✓ Insert test successful, inserted ID: {result.inserted_id}")
        
        # Clean up test data
        collection.delete_one({'_id': result.inserted_id})
        print("✓ Cleanup successful")
        
        client.close()
        print("✓ All tests passed!")
        
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
        return False
    
    return True

def test_database_manager():
    """Test the database manager"""
    print("\nTesting Database Manager...")
    
    try:
        from utils.database import init_database, get_collection
        
        # Mock config
        config = {
            'MONGODB_URI': os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/livesitter'),
            'DATABASE_NAME': os.environ.get('DATABASE_NAME', 'livesitter')
        }
        
        # Initialize database
        db_manager = init_database(config)
        print("✓ Database manager initialized")
        
        # Test collection access
        collection = get_collection('streams')
        print("✓ Collection access through manager successful")
        
        # Test insert
        test_doc = {'test': 'manager_test', 'timestamp': '2025-07-06'}
        result = collection.insert_one(test_doc)
        print(f"✓ Manager insert test successful, inserted ID: {result.inserted_id}")
        
        # Clean up
        collection.delete_one({'_id': result.inserted_id})
        print("✓ Manager cleanup successful")
        
        print("✓ Database manager tests passed!")
        
    except Exception as e:
        print(f"✗ Database manager test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=== Database Connection Test ===\n")
    
    # Test basic MongoDB connection
    basic_test = test_mongodb_connection()
    
    if basic_test:
        # Test database manager
        manager_test = test_database_manager()
        
        if manager_test:
            print("\n🎉 All database tests passed!")
        else:
            print("\n❌ Database manager test failed!")
    else:
        print("\n❌ Basic MongoDB connection failed!")
        print("Please check if MongoDB is running and accessible.") 