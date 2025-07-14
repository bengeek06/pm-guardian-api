"""
version.py
----------

This module defines the VersionResource for exposing the current API version
through a REST endpoint.
"""
from flask_restful import Resource

API_VERSION = "1.0.0"


class VersionResource(Resource):
    """
    Resource for providing the API version.

    Methods:
        get():
            Retrieve the current API version.
    """

    def get(self):
        """
        Retrieve the current API version.

        Returns:
            dict: A dictionary containing the API version and HTTP status
            code 200.
        """
        return {"version": API_VERSION}, 200
