# -*- encoding: utf-8 -*-
"""
API Security Module
Implements various security measures for Flask APIs
"""

from flask import request, jsonify, make_response
from functools import wraps
from apps.api_limiter import rate_limiter

class APISecurity:
    """
    Class to implement security features for Flask APIs
    Similar to Express.js middleware for security
    """
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """
        Initialize the security features for the Flask app
        
        :param app: Flask application instance
        """
        # Apply security headers similar to Helmet in Express
        @app.after_request
        def apply_security_headers(response):
            # Content Security Policy
            response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:;"
            
            # Prevent MIME type sniffing
            response.headers['X-Content-Type-Options'] = 'nosniff'
            
            # Clickjacking protection
            response.headers['X-Frame-Options'] = 'SAMEORIGIN'
            
            # XSS Protection
            response.headers['X-XSS-Protection'] = '1; mode=block'
            
            # HTTP Strict Transport Security
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            
            # Referrer policy
            response.headers['Referrer-Policy'] = 'same-origin'
            
            return response
        
        # Apply CORS headers
        @app.after_request
        def apply_cors(response):
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
            response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
            
            # Handle preflight requests
            if request.method == 'OPTIONS':
                return make_response()
                
            return response
        
        # Make rate limiter available at the app level
        app.rate_limiter = rate_limiter
        
        # Register a blueprint for rate limiting endpoints if needed
        # This would be done at the app level when initializing

# Authentication decorator using JWT
def jwt_required(f):
    """
    Decorator to protect routes with JWT authentication
    
    Usage:
    @app.route('/protected')
    @jwt_required
    def protected():
        return jsonify({"message": "This is protected"})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                pass
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            # Import here to avoid circular imports
            from flask import current_app
            import jwt
            
            # Decode the token
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            
            # Get the user from the token data
            from apps.authentication.models import Users
            current_user = Users.query.filter_by(id=data['user_id']).first()
            
            if not current_user:
                return jsonify({'message': 'User not found'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        
        # Pass the current user to the route
        return f(current_user, *args, **kwargs)
    
    return decorated

# Create an instance for import
api_security = APISecurity() 