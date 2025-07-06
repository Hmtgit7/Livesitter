import os
from dotenv import load_dotenv

load_dotenv()
print("Loaded MONGODB_URI:", os.environ.get('MONGODB_URI'))

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    MONGODB_URI = os.environ.get('MONGODB_URI') or 'mongodb://localhost:27017/livesitter'
    DATABASE_NAME = os.environ.get('DATABASE_NAME') or 'livesitter'
    
    # RTSP Stream settings
    FFMPEG_PATH = os.environ.get('FFMPEG_PATH') or 'ffmpeg'
    HLS_SEGMENT_DURATION = int(os.environ.get('HLS_SEGMENT_DURATION', '2'))
    HLS_PLAYLIST_LENGTH = int(os.environ.get('HLS_PLAYLIST_LENGTH', '10'))
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:8080,http://localhost:3000,http://localhost:5173').split(',')
    
    # Rate limiting
    RATELIMIT_DEFAULT = "100 per minute"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Stream settings
    STREAM_TIMEOUT = int(os.environ.get('STREAM_TIMEOUT', '30'))
    MAX_STREAMS = int(os.environ.get('MAX_STREAMS', '5'))

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    MONGODB_URI = 'mongodb://localhost:27017/livesitter_test'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 