from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from typing import Optional
import logging
from config.settings import Config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database manager for MongoDB operations"""
    
    def __init__(self, config):
        self.config = config
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self._connect()
    
    def _connect(self) -> None:
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(self.config['MONGODB_URI'])
            self.db = self.client[self.config['DATABASE_NAME']]
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def get_collection(self, collection_name: str) -> Collection:
        """Get a MongoDB collection"""
        if self.db is None:
            raise Exception("Database not connected")
        return self.db[collection_name]
    
    def close(self) -> None:
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    def health_check(self) -> bool:
        """Check database health"""
        try:
            self.client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

# Global database manager instance
db_manager: Optional[DatabaseManager] = None

def init_database(config) -> DatabaseManager:
    """Initialize database manager"""
    global db_manager
    db_manager = DatabaseManager(config)
    return db_manager

def get_db_manager() -> DatabaseManager:
    """Get database manager instance"""
    if db_manager is None:
        raise Exception("Database not initialized")
    return db_manager

def get_collection(collection_name: str) -> Collection:
    """Get a MongoDB collection"""
    return get_db_manager().get_collection(collection_name) 