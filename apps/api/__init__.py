# -*- encoding: utf-8 -*-
"""
API Blueprint Registration
"""
from flask import Blueprint

blueprint = Blueprint(
    'api_blueprint',
    __name__,
    url_prefix='/api'
) 