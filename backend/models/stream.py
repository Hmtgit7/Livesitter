from datetime import datetime
from typing import Dict, Any, Optional
from bson import ObjectId
import re

class Stream:
    """Stream model for MongoDB"""
    
    def __init__(self, data: Dict[str, Any]):
        self._id = data.get('_id')
        self.user_id = data.get('user_id', 'default')
        self.name = data.get('name', '')
        self.rtsp_url = data.get('rtsp_url', '')
        self.hls_url = data.get('hls_url', '')
        self.status = data.get('status', 'stopped')  # stopped, running, error
        self.is_active = data.get('is_active', False)
        self.overlay_ids = data.get('overlay_ids', [])
        self.settings = data.get('settings', {
            'quality': 'medium',
            'fps': 30,
            'resolution': '720p',
            'bitrate': '1000k'
        })
        self.created_at = data.get('created_at', datetime.utcnow())
        self.updated_at = data.get('updated_at', datetime.utcnow())
        self.last_started = data.get('last_started')
        self.last_stopped = data.get('last_stopped')
    
    @staticmethod
    def validate(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate stream data"""
        errors = []
        
        # Required fields
        if not data.get('name'):
            errors.append("Name is required")
        
        if not data.get('rtsp_url'):
            errors.append("RTSP URL is required")
        
        # Validate RTSP URL format
        rtsp_url = data.get('rtsp_url', '')
        if rtsp_url and not rtsp_url.startswith('rtsp://'):
            errors.append("RTSP URL must start with 'rtsp://'")
        
        # Validate status
        if data.get('status') and data['status'] not in ['stopped', 'running', 'error']:
            errors.append("Status must be 'stopped', 'running', or 'error'")
        
        # Validate settings
        settings = data.get('settings', {})
        if not isinstance(settings, dict):
            errors.append("Settings must be an object")
        else:
            if 'quality' in settings and settings['quality'] not in ['low', 'medium', 'high']:
                errors.append("Quality must be 'low', 'medium', or 'high'")
            if 'fps' in settings and not isinstance(settings['fps'], int):
                errors.append("FPS must be an integer")
            if 'resolution' in settings and settings['resolution'] not in ['480p', '720p', '1080p']:
                errors.append("Resolution must be '480p', '720p', or '1080p'")
        
        return {'valid': len(errors) == 0, 'errors': errors}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stream to dictionary"""
        return {
            '_id': str(self._id) if self._id else None,
            'user_id': self.user_id,
            'name': self.name,
            'rtsp_url': self.rtsp_url,
            'hls_url': self.hls_url,
            'status': self.status,
            'is_active': self.is_active,
            'overlay_ids': self.overlay_ids,
            'settings': self.settings,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            'last_started': self.last_started.isoformat() if isinstance(self.last_started, datetime) else self.last_started,
            'last_stopped': self.last_stopped.isoformat() if isinstance(self.last_stopped, datetime) else self.last_stopped
        }
    
    def to_mongo_dict(self) -> Dict[str, Any]:
        """Convert stream to MongoDB document format"""
        doc = self.to_dict()
        # Remove _id if it's None to let MongoDB auto-generate it
        if doc['_id'] is None:
            doc.pop('_id', None)
        elif doc['_id']:
            doc['_id'] = ObjectId(doc['_id'])
        return doc
    
    @classmethod
    def from_mongo_doc(cls, doc: Dict[str, Any]) -> 'Stream':
        """Create stream from MongoDB document"""
        return cls(doc)
    
    def update(self, data: Dict[str, Any]) -> None:
        """Update stream with new data"""
        if 'name' in data:
            self.name = data['name']
        if 'rtsp_url' in data:
            self.rtsp_url = data['rtsp_url']
        if 'hls_url' in data:
            self.hls_url = data['hls_url']
        if 'status' in data:
            self.status = data['status']
        if 'is_active' in data:
            self.is_active = data['is_active']
        if 'overlay_ids' in data:
            self.overlay_ids = data['overlay_ids']
        if 'settings' in data:
            self.settings.update(data['settings'])
        
        self.updated_at = datetime.utcnow()
    
    def start(self) -> None:
        """Mark stream as started"""
        self.status = 'running'
        self.is_active = True
        self.last_started = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def stop(self) -> None:
        """Mark stream as stopped"""
        self.status = 'stopped'
        self.is_active = False
        self.last_stopped = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def set_error(self) -> None:
        """Mark stream as error"""
        self.status = 'error'
        self.is_active = False
        self.updated_at = datetime.utcnow() 