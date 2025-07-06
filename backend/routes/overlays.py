from flask import Blueprint, request, jsonify
from bson import ObjectId
from typing import Dict, Any, List
import logging
from models.overlay import Overlay
from utils.database import get_collection
from utils.validators import validate_overlay_data, validate_object_id, validate_pagination_params

logger = logging.getLogger(__name__)

overlays_bp = Blueprint('overlays', __name__, url_prefix='/api/overlays')

@overlays_bp.route('/', methods=['OPTIONS'])
def handle_overlays_options():
    """Handle OPTIONS requests for overlays endpoint"""
    response = jsonify({'success': True})
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept, Origin, X-Requested-With'
    response.headers['Access-Control-Max-Age'] = '3600'
    return response

@overlays_bp.route('/', methods=['GET'])
def get_overlays():
    """Get all overlays with pagination"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        user_id = request.args.get('user_id', 'default')
        
        # Validate pagination parameters
        pagination_validation = validate_pagination_params(page, limit)
        if not pagination_validation['valid']:
            return jsonify({
                'success': False,
                'error': 'Invalid pagination parameters',
                'details': pagination_validation['errors']
            }), 400
        
        # Get overlays from database
        collection = get_collection('overlays')
        cursor = collection.find({'user_id': user_id}).sort('created_at', -1)
        
        overlays = []
        for doc in cursor:
            overlay = Overlay.from_mongo_doc(doc)
            overlays.append(overlay.to_dict())
        
        total_count = len(overlays)
        
        return jsonify({
            'success': True,
            'data': overlays,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_count,
                'pages': (total_count + limit - 1) // limit
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting overlays: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@overlays_bp.route('/<overlay_id>', methods=['GET'])
def get_overlay(overlay_id: str):
    """Get a specific overlay by ID"""
    try:
        # Validate ObjectId
        if not validate_object_id(overlay_id):
            return jsonify({
                'success': False,
                'error': 'Invalid overlay ID format'
            }), 400
        
        # Get overlay from database
        collection = get_collection('overlays')
        doc = collection.find_one({'_id': ObjectId(overlay_id)})
        
        if not doc:
            return jsonify({
                'success': False,
                'error': 'Overlay not found'
            }), 404
        
        overlay = Overlay.from_mongo_doc(doc)
        
        return jsonify({
            'success': True,
            'data': overlay.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting overlay {overlay_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@overlays_bp.route('/', methods=['POST'])
def create_overlay():
    """Create a new overlay"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        # Validate overlay data
        validation = validate_overlay_data(data)
        if not validation['valid']:
            return jsonify({
                'success': False,
                'error': 'Invalid overlay data',
                'details': validation['errors']
            }), 400
        
        # Add user_id if not provided
        if 'user_id' not in data:
            data['user_id'] = 'default'
        
        # Create overlay object
        overlay = Overlay(data)
        
        # Save to database
        collection = get_collection('overlays')
        result = collection.insert_one(overlay.to_mongo_dict())
        
        # Get the created overlay
        overlay._id = result.inserted_id
        created_overlay = overlay.to_dict()
        
        logger.info(f"Created overlay: {created_overlay['_id']}")
        
        return jsonify({
            'success': True,
            'data': created_overlay,
            'message': 'Overlay created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating overlay: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@overlays_bp.route('/<overlay_id>', methods=['PUT'])
def update_overlay(overlay_id: str):
    """Update an existing overlay"""
    try:
        # Validate ObjectId
        if not validate_object_id(overlay_id):
            return jsonify({
                'success': False,
                'error': 'Invalid overlay ID format'
            }), 400
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        # Validate overlay data
        validation = validate_overlay_data(data)
        if not validation['valid']:
            return jsonify({
                'success': False,
                'error': 'Invalid overlay data',
                'details': validation['errors']
            }), 400
        
        # Get existing overlay
        collection = get_collection('overlays')
        doc = collection.find_one({'_id': ObjectId(overlay_id)})
        
        if not doc:
            return jsonify({
                'success': False,
                'error': 'Overlay not found'
            }), 404
        
        overlay = Overlay.from_mongo_doc(doc)
        
        # Update overlay
        overlay.update(data)
        
        # Save to database
        collection.update_one(
            {'_id': ObjectId(overlay_id)},
            {'$set': overlay.to_mongo_dict()}
        )
        
        logger.info(f"Updated overlay: {overlay_id}")
        
        return jsonify({
            'success': True,
            'data': overlay.to_dict(),
            'message': 'Overlay updated successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating overlay {overlay_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@overlays_bp.route('/<overlay_id>', methods=['DELETE'])
def delete_overlay(overlay_id: str):
    """Delete an overlay"""
    try:
        # Validate ObjectId
        if not validate_object_id(overlay_id):
            return jsonify({
                'success': False,
                'error': 'Invalid overlay ID format'
            }), 400
        
        # Delete from database
        collection = get_collection('overlays')
        result = collection.delete_one({'_id': ObjectId(overlay_id)})
        
        if result.deleted_count == 0:
            return jsonify({
                'success': False,
                'error': 'Overlay not found'
            }), 404
        
        logger.info(f"Deleted overlay: {overlay_id}")
        
        return jsonify({
            'success': True,
            'message': 'Overlay deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting overlay {overlay_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@overlays_bp.route('/batch', methods=['POST'])
def create_multiple_overlays():
    """Create multiple overlays at once"""
    try:
        data = request.get_json()
        
        if not data or not isinstance(data.get('overlays'), list):
            return jsonify({
                'success': False,
                'error': 'Request body must contain overlays array'
            }), 400
        
        overlays_data = data['overlays']
        user_id = data.get('user_id', 'default')
        
        created_overlays = []
        errors = []
        
        for i, overlay_data in enumerate(overlays_data):
            # Validate overlay data
            validation = validate_overlay_data(overlay_data)
            if not validation['valid']:
                errors.append({
                    'index': i,
                    'errors': validation['errors']
                })
                continue
            
            # Add user_id if not provided
            if 'user_id' not in overlay_data:
                overlay_data['user_id'] = user_id
            
            # Create overlay object
            overlay = Overlay(overlay_data)
            created_overlays.append(overlay)
        
        if errors:
            return jsonify({
                'success': False,
                'error': 'Some overlays have validation errors',
                'details': errors
            }), 400
        
        # Save to database
        collection = get_collection('overlays')
        overlay_docs = [overlay.to_mongo_dict() for overlay in created_overlays]
        result = collection.insert_many(overlay_docs)
        
        # Update overlays with their IDs
        for i, overlay in enumerate(created_overlays):
            overlay._id = result.inserted_ids[i]
        
        created_data = [overlay.to_dict() for overlay in created_overlays]
        
        logger.info(f"Created {len(created_overlays)} overlays")
        
        return jsonify({
            'success': True,
            'data': created_data,
            'message': f'Created {len(created_overlays)} overlays successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating multiple overlays: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@overlays_bp.route('/test', methods=['GET'])
def test_overlays():
    """Test endpoint for overlays"""
    try:
        return jsonify({
            'success': True,
            'message': 'Overlays blueprint is working'
        }), 200
    except Exception as e:
        logger.error(f"Error in test endpoint: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500 