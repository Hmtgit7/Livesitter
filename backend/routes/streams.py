from flask import Blueprint, request, jsonify, send_from_directory
from bson import ObjectId
from typing import Dict, Any, List
import logging
import os
from models.stream import Stream
from utils.database import get_collection
from utils.stream_manager import get_stream_manager
from utils.validators import validate_stream_data, validate_object_id, validate_rtsp_url

logger = logging.getLogger(__name__)

streams_bp = Blueprint('streams', __name__, url_prefix='/api/streams')

@streams_bp.route('/', methods=['OPTIONS'])
def handle_streams_options():
    """Handle OPTIONS requests for streams endpoint"""
    response = jsonify({'success': True})
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept, Origin, X-Requested-With'
    response.headers['Access-Control-Max-Age'] = '3600'
    return response

@streams_bp.route('/', methods=['GET'])
def get_streams():
    """Get all streams"""
    try:
        user_id = request.args.get('user_id', 'default')
        
        # Get streams from database
        collection = get_collection('streams')
        cursor = collection.find({'user_id': user_id}).sort('created_at', -1)
        
        streams = []
        for doc in cursor:
            stream = Stream.from_mongo_doc(doc)
            streams.append(stream.to_dict())
        
        return jsonify({
            'success': True,
            'data': streams
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting streams: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@streams_bp.route('/<stream_id>', methods=['GET'])
def get_stream(stream_id: str):
    """Get a specific stream by ID"""
    try:
        # Validate ObjectId
        if not validate_object_id(stream_id):
            return jsonify({
                'success': False,
                'error': 'Invalid stream ID format'
            }), 400
        
        # Get stream from database
        collection = get_collection('streams')
        doc = collection.find_one({'_id': ObjectId(stream_id)})
        
        if not doc:
            return jsonify({
                'success': False,
                'error': 'Stream not found'
            }), 404
        
        stream = Stream.from_mongo_doc(doc)
        
        # Get current stream status from stream manager
        stream_manager = get_stream_manager()
        status_info = stream_manager.get_stream_status(stream_id)
        
        stream_data = stream.to_dict()
        stream_data['current_status'] = status_info
        
        return jsonify({
            'success': True,
            'data': stream_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting stream {stream_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@streams_bp.route('/', methods=['POST'])
def create_stream():
    """Create a new stream"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        # Validate stream data
        validation = validate_stream_data(data)
        if not validation['valid']:
            return jsonify({
                'success': False,
                'error': 'Invalid stream data',
                'details': validation['errors']
            }), 400
        
        # Add user_id if not provided
        if 'user_id' not in data:
            data['user_id'] = 'default'
        
        # Create stream object
        stream = Stream(data)
        
        # Save to database
        collection = get_collection('streams')
        result = collection.insert_one(stream.to_mongo_dict())
        
        # Get the created stream
        stream._id = result.inserted_id
        created_stream = stream.to_dict()
        
        logger.info(f"Created stream: {created_stream['_id']}")
        
        return jsonify({
            'success': True,
            'data': created_stream,
            'message': 'Stream created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating stream: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@streams_bp.route('/<stream_id>', methods=['PUT'])
def update_stream(stream_id: str):
    """Update an existing stream"""
    try:
        # Validate ObjectId
        if not validate_object_id(stream_id):
            return jsonify({
                'success': False,
                'error': 'Invalid stream ID format'
            }), 400
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        # Validate stream data
        validation = validate_stream_data(data)
        if not validation['valid']:
            return jsonify({
                'success': False,
                'error': 'Invalid stream data',
                'details': validation['errors']
            }), 400
        
        # Get existing stream
        collection = get_collection('streams')
        doc = collection.find_one({'_id': ObjectId(stream_id)})
        
        if not doc:
            return jsonify({
                'success': False,
                'error': 'Stream not found'
            }), 404
        
        stream = Stream.from_mongo_doc(doc)
        
        # Update stream
        stream.update(data)
        
        # Save to database
        collection.update_one(
            {'_id': ObjectId(stream_id)},
            {'$set': stream.to_mongo_dict()}
        )
        
        logger.info(f"Updated stream: {stream_id}")
        
        return jsonify({
            'success': True,
            'data': stream.to_dict(),
            'message': 'Stream updated successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating stream {stream_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@streams_bp.route('/<stream_id>', methods=['DELETE'])
def delete_stream(stream_id: str):
    """Delete a stream"""
    try:
        # Validate ObjectId
        if not validate_object_id(stream_id):
            return jsonify({
                'success': False,
                'error': 'Invalid stream ID format'
            }), 400
        
        # Stop stream if running
        stream_manager = get_stream_manager()
        stream_manager.stop_stream(stream_id)
        
        # Delete from database
        collection = get_collection('streams')
        result = collection.delete_one({'_id': ObjectId(stream_id)})
        
        if result.deleted_count == 0:
            return jsonify({
                'success': False,
                'error': 'Stream not found'
            }), 404
        
        logger.info(f"Deleted stream: {stream_id}")
        
        return jsonify({
            'success': True,
            'message': 'Stream deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting stream {stream_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@streams_bp.route('/<stream_id>/start', methods=['POST'])
def start_stream(stream_id: str):
    """Start a stream"""
    try:
        # Validate ObjectId
        if not validate_object_id(stream_id):
            return jsonify({
                'success': False,
                'error': 'Invalid stream ID format'
            }), 400
        
        # Get stream from database
        collection = get_collection('streams')
        doc = collection.find_one({'_id': ObjectId(stream_id)})
        
        if not doc:
            return jsonify({
                'success': False,
                'error': 'Stream not found'
            }), 404
        
        stream = Stream.from_mongo_doc(doc)
        
        # Start stream using stream manager
        stream_manager = get_stream_manager()
        result = stream_manager.start_stream(
            stream_id=str(stream._id),
            rtsp_url=stream.rtsp_url,
            settings=stream.settings
        )
        
        if not result['success']:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
        
        # Update stream status in database
        stream.start()
        collection.update_one(
            {'_id': ObjectId(stream_id)},
            {'$set': stream.to_mongo_dict()}
        )
        
        logger.info(f"Started stream: {stream_id}")
        
        return jsonify({
            'success': True,
            'data': {
                'stream_id': stream_id,
                'hls_url': result['hls_url'],
                'status': result['status']
            },
            'message': 'Stream started successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error starting stream {stream_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@streams_bp.route('/<stream_id>/stop', methods=['POST'])
def stop_stream(stream_id: str):
    """Stop a stream"""
    try:
        # Validate ObjectId
        if not validate_object_id(stream_id):
            return jsonify({
                'success': False,
                'error': 'Invalid stream ID format'
            }), 400
        
        # Get stream from database
        collection = get_collection('streams')
        doc = collection.find_one({'_id': ObjectId(stream_id)})
        
        if not doc:
            return jsonify({
                'success': False,
                'error': 'Stream not found'
            }), 404
        
        stream = Stream.from_mongo_doc(doc)
        
        # Stop stream using stream manager
        stream_manager = get_stream_manager()
        result = stream_manager.stop_stream(stream_id=str(stream._id))
        
        if not result['success']:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
        
        # Update stream status in database
        stream.stop()
        collection.update_one(
            {'_id': ObjectId(stream_id)},
            {'$set': stream.to_mongo_dict()}
        )
        
        logger.info(f"Stopped stream: {stream_id}")
        
        return jsonify({
            'success': True,
            'message': 'Stream stopped successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error stopping stream {stream_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@streams_bp.route('/<stream_id>/status', methods=['GET'])
def get_stream_status(stream_id: str):
    """Get stream status"""
    try:
        # Validate ObjectId
        if not validate_object_id(stream_id):
            return jsonify({
                'success': False,
                'error': 'Invalid stream ID format'
            }), 400
        
        # Get stream status from stream manager
        stream_manager = get_stream_manager()
        status_info = stream_manager.get_stream_status(stream_id)
        
        return jsonify({
            'success': True,
            'data': status_info
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting stream status {stream_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@streams_bp.route('/active', methods=['GET'])
def get_active_streams():
    """Get all active streams"""
    try:
        stream_manager = get_stream_manager()
        active_streams = stream_manager.get_all_streams()
        
        return jsonify({
            'success': True,
            'data': active_streams
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting active streams: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@streams_bp.route('/hls/<path:filename>')
def serve_hls_file(filename):
    """Serve HLS files (playlist.m3u8 and .ts segments)"""
    try:
        streams_dir = os.path.join(os.getcwd(), 'streams')
        logger.info(f"Serving HLS file: {filename} from directory: {streams_dir}")
        
        # Check if file exists
        file_path = os.path.join(streams_dir, filename)
        if not os.path.exists(file_path):
            logger.warning(f"HLS file not found: {file_path}")
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404
        
        return send_from_directory(streams_dir, filename)
    except Exception as e:
        logger.error(f"Error serving HLS file {filename}: {e}")
        return jsonify({
            'success': False,
            'error': 'File not found'
        }), 404

@streams_bp.route('/test-hls/<stream_id>')
def test_hls_creation(stream_id: str):
    """Test endpoint to create a simple HLS file for testing"""
    try:
        streams_dir = os.path.join(os.getcwd(), 'streams')
        stream_dir = os.path.join(streams_dir, stream_id)
        os.makedirs(stream_dir, exist_ok=True)
        
        # Create a simple test playlist
        playlist_content = """#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:2
#EXT-X-MEDIA-SEQUENCE:0
#EXTINF:2.0,
segment_000.ts
#EXT-X-ENDLIST"""
        
        playlist_path = os.path.join(stream_dir, 'playlist.m3u8')
        with open(playlist_path, 'w') as f:
            f.write(playlist_content)
        
        # Create a simple test segment (empty file for testing)
        segment_path = os.path.join(stream_dir, 'segment_000.ts')
        with open(segment_path, 'w') as f:
            f.write('')
        
        logger.info(f"Created test HLS files for stream {stream_id}")
        return jsonify({
            'success': True,
            'message': f'Test HLS files created for stream {stream_id}',
            'playlist_url': f'/api/streams/hls/{stream_id}/playlist.m3u8'
        })
        
    except Exception as e:
        logger.error(f"Error creating test HLS files: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 