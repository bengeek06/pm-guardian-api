"""
Module: app.models.__init__

Initializes the SQLAlchemy instance (db) for the Flask application.
This instance is used throughout the application for ORM operations.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
