#!/usr/bin/env python3
"""
Production server startup script for Word Cloud Generator API.
Uses waitress WSGI server for production deployment.
"""

import os
import sys
from waitress import serve
from app import app

if __name__ == '__main__':
    # Set production environment variables
    os.environ['FLASK_ENV'] = 'production'
    os.environ['DEBUG'] = '0'
    
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 8000))
    
    print(f"Starting Word Cloud Generator API on port {port}...")
    print("Server will be available at: http://localhost:{port}")
    print("Press Ctrl+C to stop the server")
    
    try:
        # Start the waitress server
        serve(app, host='0.0.0.0', port=port, threads=4)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1) 