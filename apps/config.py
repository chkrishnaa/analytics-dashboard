# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os

class Config(object):

    basedir = os.path.abspath(os.path.dirname(__file__))

    # Set up the App SECRET_KEY
    # SECRET_KEY = config('SECRET_KEY'  , default='S#perS3crEt_007')
    SECRET_KEY = os.getenv('SECRET_KEY', 'S#perS3crEt_007')

    # This will create a file in <app> FOLDER
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False 

    # Assets Management
    ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/assets')    
    
    SOCIAL_AUTH_GITHUB  = False

    GITHUB_ID      = os.getenv('GITHUB_ID')
    GITHUB_SECRET  = os.getenv('GITHUB_SECRET')

    # Enable/Disable Github Social Login    
    if GITHUB_ID and GITHUB_SECRET:
         SOCIAL_AUTH_GITHUB  = True

class ProductionConfig(Config):
    DEBUG = False

    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600

    # PostgreSQL database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', '')
    
    # MySQL database
    DB_ENGINE   = os.getenv('DB_ENGINE'   , 'mysql')
    DB_HOST     = os.getenv('DB_HOST'     , 'localhost')
    DB_PORT     = os.getenv('DB_PORT'     , 3306)
    DB_NAME     = os.getenv('DB_NAME'     , 'appseed_db')
    DB_USERNAME = os.getenv('DB_USERNAME' , 'appseed_db_usr')
    DB_PASS     = os.getenv('DB_PASS'     , 'pass')

    if DB_ENGINE == 'mysql':
        try:
            SQLALCHEMY_DATABASE_URI = '{}://{}:{}@{}:{}/{}'.format(
                DB_ENGINE,
                DB_USERNAME,
                DB_PASS,
                DB_HOST,
                DB_PORT,
                DB_NAME
            )
        except Exception as e:
            print('→ Error - DBMS Exception: ' + str(e) )
            SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(Config.basedir, 'db.sqlite3')

class DebugConfig(Config):
    DEBUG = True


# Load all possible configurations
config_dict = {
    'Production': ProductionConfig,
    'Debug'     : DebugConfig
}
