# -*- encoding: utf-8 -*-
"""
API Routes
Secure API endpoints with rate limiting, validation, and JWT authentication
"""

from flask import jsonify, request
from apps.api import blueprint
from apps.api_limiter import rate_limiter
from apps.api_validation import validate_with_schema, user_login_schema, user_registration_schema
from apps.api_security import jwt_required
from apps.authentication.models import Users
from apps.authentication.util import verify_pass
from apps import db

import jwt
import datetime
from flask import current_app

# Public API endpoint with rate limiting
@blueprint.route('/status', methods=['GET'])
@rate_limiter.limit
def api_status():
    """Public API endpoint with rate limiting"""
    return jsonify({
        "status": "online",
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

# API Login with validation and rate limiting
@blueprint.route('/auth/login', methods=['POST'])
@rate_limiter.limit
@validate_with_schema(user_login_schema)
def api_login():
    """
    API Login endpoint
    - Validates input with schema
    - Rate limited for security
    - Returns JWT token on success
    """
    # Get validated data
    data = request.validated_data
    username = data.get('username')
    password = data.get('password')
    
    # Locate user
    user = Users.query.filter_by(username=username).first()
    
    # Check password
    if user and verify_pass(password, user.password):
        # Generate token
        token = jwt.encode({
            'user_id': user.id,
            'username': user.username,
            'exp': datetime.datetime.now() + datetime.timedelta(hours=24)
        }, current_app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({
            'token': token,
            'expires_in': 86400  # 24 hours in seconds
        })
    
    return jsonify({'error': 'Invalid credentials'}), 401

# API Registration with validation
@blueprint.route('/auth/register', methods=['POST'])
@rate_limiter.limit
@validate_with_schema(user_registration_schema)
def api_register():
    """
    API Registration endpoint
    - Validates input with schema
    - Rate limited for security
    """
    # Get validated data
    data = request.validated_data
    username = data.get('username')
    email = data.get('email')
    
    # Check if username exists
    user = Users.query.filter_by(username=username).first()
    if user:
        return jsonify({'error': 'Username already registered'}), 400
    
    # Check if email exists
    user = Users.query.filter_by(email=email).first()
    if user:
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create new user
    new_user = Users(**data)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully'}), 201

# Protected API endpoint requiring JWT authentication
@blueprint.route('/profile', methods=['GET'])
@rate_limiter.limit
@jwt_required
def api_profile(current_user):
    """
    Protected API endpoint
    - Requires JWT authentication
    - Rate limited for security
    - Gets current user from JWT token
    """
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email
    })

# Protected API with both JWT and rate limiting
@blueprint.route('/dashboard/stats', methods=['GET'])
@rate_limiter.limit
@jwt_required
def api_dashboard_stats(current_user):
    """
    Protected dashboard stats API
    - Requires JWT authentication
    - Rate limited for security
    - Example of a data API endpoint
    """
    # This would typically fetch data from a database
    # For demo purposes, we're returning mock data
    return jsonify({
        'total_users': Users.query.count(),
        'active_sessions': 42,
        'daily_requests': 1024,
        'user_info': {
            'id': current_user.id,
            'username': current_user.username
        }
    }) 