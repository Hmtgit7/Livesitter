from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
import os
from datetime import datetime

# Import configuration
from config.settings import config

# Import utilities
from utils.database import init_database
from utils.stream_manager import init_stream_manager

# Import routes
from routes.overlays import overlays_bp
from routes.streams import streams_bp
from routes.health import health_bp

def create_app(config_name='default'):
    """Create and configure Flask application"""
    
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Disable automatic trailing slash redirects to prevent CORS issues
    app.url_map.strict_slashes = False
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize CORS with comprehensive configuration
    CORS(app, 
         origins=app.config['CORS_ORIGINS'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
         allow_headers=['Content-Type', 'Authorization', 'Accept', 'Origin', 'X-Requested-With'],
         expose_headers=['Content-Type', 'Authorization'],
         supports_credentials=False,  # Changed to False to avoid credential issues
         max_age=3600)
    
    # Initialize rate limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=[app.config['RATELIMIT_DEFAULT']],
        storage_uri=app.config['RATELIMIT_STORAGE_URL']
    )
    
    # Initialize database and stream manager
    with app.app_context():
        try:
            # Get the actual config class instance
            config_instance = config[config_name]()
            init_database(app.config)
            init_stream_manager(config_instance)
            app.logger.info("Successfully initialized database and stream manager")
        except Exception as e:
            app.logger.error(f"Failed to initialize services: {e}")
            raise
    
    # Register blueprints
    app.register_blueprint(overlays_bp)
    app.register_blueprint(streams_bp)
    app.register_blueprint(health_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Endpoint not found'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 'Method not allowed'
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    
    # Request logging middleware
    @app.before_request
    def log_request():
        app.logger.info(f"{request.method} {request.path} - {request.remote_addr}")
    
    # Global OPTIONS handler for CORS preflight requests
    @app.route('/api/<path:path>', methods=['OPTIONS'])
    def handle_options(path):
        """Handle OPTIONS requests for all API endpoints"""
        response = jsonify({'success': True})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept, Origin, X-Requested-With'
        response.headers['Access-Control-Max-Age'] = '3600'
        return response
    
    # Response logging middleware
    @app.after_request
    def log_response(response):
        app.logger.info(f"Response: {response.status_code}")
        
        # Add cache-busting headers for CORS
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
    

    
    # Root endpoint
    @app.route('/')
    def root():
        return jsonify({
            'success': True,
            'message': 'Livesitter API',
            'version': '1.0.0',
            'timestamp': datetime.utcnow().isoformat(),
            'endpoints': {
                'overlays': '/api/overlays',
                'streams': '/api/streams',
                'health': '/api/health'
            }
        })
    
    # API documentation endpoint
    @app.route('/api/docs')
    def api_docs():
        return jsonify({
            'success': True,
            'message': 'API Documentation',
            'endpoints': {
                'overlays': {
                    'GET /api/overlays': 'Get all overlays with pagination',
                    'GET /api/overlays/<id>': 'Get specific overlay',
                    'POST /api/overlays': 'Create new overlay',
                    'PUT /api/overlays/<id>': 'Update overlay',
                    'DELETE /api/overlays/<id>': 'Delete overlay',
                    'POST /api/overlays/batch': 'Create multiple overlays'
                },
                'streams': {
                    'GET /api/streams': 'Get all streams',
                    'GET /api/streams/<id>': 'Get specific stream',
                    'POST /api/streams': 'Create new stream',
                    'PUT /api/streams/<id>': 'Update stream',
                    'DELETE /api/streams/<id>': 'Delete stream',
                    'POST /api/streams/<id>/start': 'Start stream',
                    'POST /api/streams/<id>/stop': 'Stop stream',
                    'GET /api/streams/<id>/status': 'Get stream status',
                    'GET /api/streams/active': 'Get active streams'
                },
                'health': {
                    'GET /api/health': 'Overall health check',
                    'GET /api/health/database': 'Database health check',
                    'GET /api/health/streams': 'Streams health check'
                }
            }
        })
    
    return app

def main():
    """Main application entry point"""
    # Get configuration from environment
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Create app
    app = create_app(config_name)
    
    # Run app
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    app.logger.info(f"Starting Livesitter API on {host}:{port}")
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    main() 