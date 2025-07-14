"""
test_version.py
---------------
This module contains tests for the /version endpoint to ensure it returns the
correct version information.
"""

import json

def test_version_endpoint(client):
    """
    Test the /version endpoint to ensure it returns the correct version
    information.
    """

    response = client.get('/version')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert isinstance(data, dict)
    assert "version" in data
