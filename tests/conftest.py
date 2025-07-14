"""
# conftest.py
# -----------
"""
import os
from pytest import fixture
from dotenv import load_dotenv

os.environ['FLASK_ENV'] = 'testing'
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env.test'))
from app import create_app
from app.models import db

@fixture
def app():
    """
    Fixture to create and configure a Flask application for testing.
    This fixture sets up the application context, initializes the database,
    and ensures that the database is created before tests run and dropped after tests complete.
    """
    app = create_app('app.config.TestingConfig')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@fixture
def client(app):
    return app.test_client()

@fixture
def session(app):
    with app.app_context():
        yield db.session
