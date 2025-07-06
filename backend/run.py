#!/usr/bin/env python3
"""
Run script for Livesitter Backend
"""

import os
import sys
from app import create_app

def main():
    """Main entry point"""
    
    # Set default environment
    if not os.environ.get('FLASK_ENV'):
        os.environ['FLASK_ENV'] = 'development'
    
    # Create app
    app = create_app()
    
    # Get configuration
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"Starting Livesitter Backend...")
    print(f"Environment: {os.environ.get('FLASK_ENV')}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    print(f"API URL: http://{host}:{port}")
    print(f"Health Check: http://{host}:{port}/api/health")
    print(f"API Docs: http://{host}:{port}/api/docs")
    print()
    
    # Run app
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    main() 