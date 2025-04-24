# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask import render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
from apps import db
from apps.authentication.models import Users
import os
from werkzeug.utils import secure_filename
import uuid


@blueprint.route('/index')
@login_required
def index():
    return render_template('home/index.html', segment='index')


@blueprint.route('/profile', methods=['GET'])
@login_required
def profile():
    return render_template('home/user.html', segment='user')


@blueprint.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    """Handle profile update form submission - using client-side storage"""
    try:
        # Return success without DB changes
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@blueprint.route('/upload-profile-image', methods=['POST'])
@login_required
def upload_profile_image():
    """Handle profile image upload"""
    if 'profile_image' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'}), 400
    
    file = request.files['profile_image']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'}), 400
    
    if file:
        # Secure filename and create a unique name to prevent overwriting
        filename = secure_filename(file.filename)
        file_extension = os.path.splitext(filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        
        # Create the uploads directory if it doesn't exist
        uploads_dir = os.path.join(current_app.root_path, 'static/assets/img/profile_uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(uploads_dir, unique_filename)
        file.save(file_path)
        
        # Return the path without database update
        relative_path = f"img/profile_uploads/{unique_filename}"
        
        return jsonify({
            'success': True, 
            'message': 'Profile image uploaded successfully',
            'image_path': relative_path
        })
    
    return jsonify({'success': False, 'message': 'Failed to upload file'}), 500


@blueprint.route('/<template>')
@login_required
def route_template(template):
    try:
        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):
    try:
        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
