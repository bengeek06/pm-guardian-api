"""
test_config.py
--------------
This module contains tests for the /config endpoint to ensure it returns the
expected configuration values.
"""

import json

def test_config_endpoit(client):
    """
    Test the /config endpoint to ensure it returns the correct configuration.
    """
    response = client.get('/config')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert isinstance(data, dict)
    assert "FLASK_ENV" in data
    assert "DEBUG" in data
    assert "DATABASE_URI" in data
