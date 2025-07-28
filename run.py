"""
run.py
------

Entry point for running the Flask application.

This script:
    - Detects the current environment from the FLASK_ENV environment variable.
    - Loads the appropriate .env file for the environment.
    - Selects the correct configuration class for the Flask app.
    - Creates the Flask application instance.
    - Runs the application if executed as the main module.
"""

import os
from dotenv import load_dotenv
from app import create_app
from app.logger import logger

# Detect the current environment
env = os.environ.get('FLASK_ENV')
if not env:
    logger.warning("FLASK_ENV is not set, defaulting to 'development'")
    env = 'development'
else:
    logger.info(f"Running in {env} environment")


# Load the appropriate .env file
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=app.config['DEBUG'])
