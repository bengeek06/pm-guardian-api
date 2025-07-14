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

# Détection de l'environnement
env = os.environ.get('FLASK_ENV', 'development')

# Chargement du bon fichier .env
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
