"""
config.py
---------

This module defines the ConfigResource for exposing the current application
configuration through a REST endpoint.
"""

import os
from flask_restful import Resource


class ConfigResource(Resource):
    """
    Resource for providing the application configuration.

    Methods:
        get():
            Retrieve the current application configuration.
    """

    def get(self):
        """
        Retrieve the current application configuration.

        Returns:
            dict: A dictionary containing the application configuration and
            HTTP status code 200.
        """
        config = {
            "FLASK_ENV": os.getenv("FLASK_ENV"),
            "DEBUG": os.getenv("DEBUG"),
            "DATABASE_URI": os.getenv("DATABASE_URI")
        }
        return config, 200
