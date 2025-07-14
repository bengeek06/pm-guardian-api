"""
wsgi.py
-------

WSGI entry point for deploying the Flask application.

This script:
    - Detects the current environment from the FLASK_ENV environment variable.
    - Loads the appropriate .env file for the environment.
    - Selects the correct configuration class for the Flask app.
    - Creates the Flask application instance as 'app' for the WSGI server.
"""

import os
from dotenv import load_dotenv
from app import create_app

env = os.environ.get('FLASK_ENV', 'development')

if env == 'production':
    load_dotenv('.env.production')
    config_class = 'app.config.ProductionConfig'
elif env == 'staging':
    load_dotenv('.env.staging')
    config_class = 'app.config.StagingConfig'
elif env == 'testing':
    load_dotenv('.env.test')
    config_class = 'app.config.TestingConfig'
else:
    load_dotenv('.env.development')
    config_class = 'app.config.DevelopmentConfig'


app = create_app(config_class)
