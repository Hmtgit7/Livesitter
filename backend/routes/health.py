from flask import Blueprint, jsonify
import logging
from utils.database import get_db_manager
from utils.stream_manager import get_stream_manager

logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__, url_prefix='/api/health')

@health_bp.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db_manager = get_db_manager()
        db_healthy = db_manager.health_check()
        
        # Check stream manager
        stream_manager = get_stream_manager()
        active_streams = stream_manager.get_all_streams()
        
        status = {
            'status': 'healthy' if db_healthy else 'unhealthy',
            'database': 'connected' if db_healthy else 'disconnected',
            'active_streams': len(active_streams),
            'timestamp': '2024-01-01T00:00:00Z'  # You can add proper timestamp here
        }
        
        status_code = 200 if db_healthy else 503
        
        return jsonify(status), status_code
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503

@health_bp.route('/database', methods=['GET'])
def database_health():
    """Database health check"""
    try:
        db_manager = get_db_manager()
        is_healthy = db_manager.health_check()
        
        return jsonify({
            'status': 'healthy' if is_healthy else 'unhealthy',
            'database': 'connected' if is_healthy else 'disconnected'
        }), 200 if is_healthy else 503
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503

@health_bp.route('/streams', methods=['GET'])
def streams_health():
    """Streams health check"""
    try:
        stream_manager = get_stream_manager()
        active_streams = stream_manager.get_all_streams()
        
        return jsonify({
            'status': 'healthy',
            'active_streams': len(active_streams),
            'streams': active_streams
        }), 200
        
    except Exception as e:
        logger.error(f"Streams health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503 