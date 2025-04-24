# -*- encoding: utf-8 -*-
"""
API Validation Module
Implements request validation similar to Joi in Express.js
"""

from flask import request, jsonify
from functools import wraps
from marshmallow import Schema, fields, ValidationError

# Base validator function
def validate_with_schema(schema):
    """
    Decorator to validate incoming request data with a marshmallow schema
    
    :param schema: Marshmallow schema class to validate against
    
    Usage:
    class UserSchema(Schema):
        name = fields.String(required=True, validate=lambda s: len(s) >= 3)
        email = fields.Email(required=True)
        password = fields.String(required=True, validate=lambda s: len(s) >= 6)
        
    @app.route('/api/users', methods=['POST'])
    @validate_with_schema(UserSchema())
    def create_user():
        # If this executes, validation passed
        return jsonify({"message": "User created"})
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Determine the request data based on content type
            if request.is_json:
                data = request.json
            elif request.content_type == 'application/x-www-form-urlencoded':
                data = request.form.to_dict()
            else:
                data = request.get_json(silent=True) or {}
            
            try:
                # Validate data against schema
                validated_data = schema.load(data)
                # Add validated data to request object for easy access
                request.validated_data = validated_data
            except ValidationError as err:
                # Return validation errors
                return jsonify({"errors": err.messages}), 400
            
            return f(*args, **kwargs)
        return wrapper
    return decorator

# Common validation schemas
class UserRegistrationSchema(Schema):
    """Schema for user registration"""
    username = fields.String(required=True, validate=lambda s: len(s) >= 3)
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=lambda s: len(s) >= 6)

class UserLoginSchema(Schema):
    """Schema for user login"""
    username = fields.String(required=True)
    password = fields.String(required=True)

class ProfileUpdateSchema(Schema):
    """Schema for profile update"""
    name = fields.String(validate=lambda s: len(s) >= 3)
    email = fields.Email()
    bio = fields.String(validate=lambda s: len(s) <= 500)

# Export common schemas
user_registration_schema = UserRegistrationSchema()
user_login_schema = UserLoginSchema()
profile_update_schema = ProfileUpdateSchema() 