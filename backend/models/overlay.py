from datetime import datetime
from typing import Dict, Any, Optional
from bson import ObjectId
import re

class Overlay:
    """Overlay model for MongoDB"""
    
    def __init__(self, data: Dict[str, Any]):
        self._id = data.get('_id')
        self.user_id = data.get('user_id', 'default')
        self.name = data.get('name', '')
        self.type = data.get('type', 'text')  # text, image, logo
        self.content = data.get('content', '')
        self.position = data.get('position', {'x': 0, 'y': 0})
        self.size = data.get('size', {'width': 100, 'height': 50})
        self.style = data.get('style', {
            'fontSize': 16,
            'color': '#ffffff',
            'fontFamily': 'Arial',
            'opacity': 1.0,
            'backgroundColor': 'transparent',
            'borderColor': 'transparent',
            'borderWidth': 0
        })
        self.created_at = data.get('created_at', datetime.utcnow())
        self.updated_at = data.get('updated_at', datetime.utcnow())
    
    @staticmethod
    def validate(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate overlay data"""
        errors = []
        
        # Required fields
        if not data.get('name'):
            errors.append("Name is required")
        
        if not data.get('type'):
            errors.append("Type is required")
        
        if data.get('type') not in ['text', 'image', 'logo']:
            errors.append("Type must be 'text', 'image', or 'logo'")
        
        # Validate position
        position = data.get('position', {})
        if not isinstance(position, dict):
            errors.append("Position must be an object")
        else:
            if not isinstance(position.get('x'), (int, float)):
                errors.append("Position x must be a number")
            if not isinstance(position.get('y'), (int, float)):
                errors.append("Position y must be a number")
        
        # Validate size
        size = data.get('size', {})
        if not isinstance(size, dict):
            errors.append("Size must be an object")
        else:
            if not isinstance(size.get('width'), (int, float)) or size.get('width', 0) <= 0:
                errors.append("Size width must be a positive number")
            if not isinstance(size.get('height'), (int, float)) or size.get('height', 0) <= 0:
                errors.append("Size height must be a positive number")
        
        # Validate style
        style = data.get('style', {})
        if not isinstance(style, dict):
            errors.append("Style must be an object")
        else:
            if 'fontSize' in style and not isinstance(style['fontSize'], (int, float)):
                errors.append("Font size must be a number")
            if 'opacity' in style and not (0 <= style['opacity'] <= 1):
                errors.append("Opacity must be between 0 and 1")
            if 'color' in style and not re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', style['color']):
                errors.append("Color must be a valid hex color")
        
        return {'valid': len(errors) == 0, 'errors': errors}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert overlay to dictionary"""
        return {
            '_id': str(self._id) if self._id else None,
            'user_id': self.user_id,
            'name': self.name,
            'type': self.type,
            'content': self.content,
            'position': self.position,
            'size': self.size,
            'style': self.style,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
    
    def to_mongo_dict(self) -> Dict[str, Any]:
        """Convert overlay to MongoDB document format"""
        doc = self.to_dict()
        # Remove _id if it's None to let MongoDB auto-generate it
        if doc['_id'] is None:
            doc.pop('_id', None)
        elif doc['_id']:
            doc['_id'] = ObjectId(doc['_id'])
        return doc
    
    @classmethod
    def from_mongo_doc(cls, doc: Dict[str, Any]) -> 'Overlay':
        """Create overlay from MongoDB document"""
        return cls(doc)
    
    def update(self, data: Dict[str, Any]) -> None:
        """Update overlay with new data"""
        if 'name' in data:
            self.name = data['name']
        if 'type' in data:
            self.type = data['type']
        if 'content' in data:
            self.content = data['content']
        if 'position' in data:
            self.position = data['position']
        if 'size' in data:
            self.size = data['size']
        if 'style' in data:
            self.style.update(data['style'])
        
        self.updated_at = datetime.utcnow() 