# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module


db = SQLAlchemy()
login_manager = LoginManager()


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)


def register_blueprints(app):
    # Register core modules
    for module_name in ('authentication', 'home'):
        module = import_module('apps.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)
    
    # Register API blueprint
    from apps.api.routes import blueprint as api_blueprint
    app.register_blueprint(api_blueprint)


def configure_database(app):

    @app.before_first_request
    def initialize_database():
        db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()

from apps.authentication.oauth import github_blueprint

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    
    # Initialize extensions
    register_extensions(app)
    
    # OAuth registration
    app.register_blueprint(github_blueprint, url_prefix="/login")
    
    # Register blueprints
    register_blueprints(app)
    
    # Configure database
    configure_database(app)
    
    # Initialize API security features
    from apps.api_security import api_security
    api_security.init_app(app)
    
    return app
