import re
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

def validate_rtsp_url(url: str) -> Dict[str, Any]:
    """Validate RTSP URL format"""
    errors = []
    
    if not url:
        errors.append("RTSP URL is required")
        return {'valid': False, 'errors': errors}
    
    # Check if URL starts with rtsp://
    if not url.startswith('rtsp://'):
        errors.append("URL must start with 'rtsp://'")
    
    # Basic URL format validation
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            errors.append("Invalid URL format")
    except Exception:
        errors.append("Invalid URL format")
    
    return {'valid': len(errors) == 0, 'errors': errors}

def validate_overlay_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate overlay data"""
    errors = []
    
    # Required fields
    if not data.get('name'):
        errors.append("Name is required")
    
    if not data.get('type'):
        errors.append("Type is required")
    elif data['type'] not in ['text', 'image', 'logo']:
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

def validate_stream_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate stream data"""
    errors = []
    
    # Required fields
    if not data.get('name'):
        errors.append("Name is required")
    
    if not data.get('rtsp_url'):
        errors.append("RTSP URL is required")
    else:
        rtsp_validation = validate_rtsp_url(data['rtsp_url'])
        if not rtsp_validation['valid']:
            errors.extend(rtsp_validation['errors'])
    
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

def sanitize_string(value: str, max_length: int = 255) -> str:
    """Sanitize string input"""
    if not isinstance(value, str):
        return ""
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', value)
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized.strip()

def validate_pagination_params(page: int, limit: int, max_limit: int = 100) -> Dict[str, Any]:
    """Validate pagination parameters"""
    errors = []
    
    if not isinstance(page, int) or page < 1:
        errors.append("Page must be a positive integer")
    
    if not isinstance(limit, int) or limit < 1:
        errors.append("Limit must be a positive integer")
    elif limit > max_limit:
        errors.append(f"Limit cannot exceed {max_limit}")
    
    return {'valid': len(errors) == 0, 'errors': errors}

def validate_object_id(object_id: str) -> bool:
    """Validate MongoDB ObjectId format"""
    if not object_id:
        return False
    
    # MongoDB ObjectId is 24 characters long and contains only hex characters
    pattern = r'^[0-9a-fA-F]{24}$'
    return bool(re.match(pattern, object_id)) 