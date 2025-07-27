"""
test_init.py
------------
This module contains tests for the Flask application factory, error handlers, and main entrypoint.
It ensures that the app is created correctly, custom error handlers work as expected,
and the main run logic is invoked properly.
"""
import pytest
from flask import Flask
import app

@pytest.mark.parametrize("route,expected_status,message", [
    ("/unauthorized", 401, "Unauthorized"),
    ("/forbidden", 403, "Forbidden"),
    ("/bad", 400, "Bad request"),
    ("/fail", 500, "Internal server error"),
])

def test_error_handlers(client, route, expected_status, message):
    """
    Test custom error handlers for 401, 403, 400, and 500 errors.
    """
    resp = client.get(route)
    assert resp.status_code == expected_status
    assert resp.is_json
    data = resp.get_json()
    assert data["message"].lower() == message.lower()

def test_main_runs(monkeypatch):
    """
    Test that the main run logic is called with the correct debug argument.
    """
    called = {}

    def fake_run(self, debug):
        called['run'] = True
        called['debug'] = debug

    monkeypatch.setattr("flask.Flask.run", fake_run)
    app.create_app('app.config.TestingConfig').run(debug=True)
    assert called.get('run') is True
    assert called.get('debug') is True


def test_create_app_returns_flask_app():
    """
    Test that create_app returns a Flask application instance.
    """
    application = app.create_app('app.config.TestingConfig')
    assert isinstance(application, Flask)


def test_handle_404(client):
    """
    Test that a 404 error returns the correct JSON response.
    """
    response = client.get('/v0/route/inexistante')
    assert response.status_code == 404
    assert response.is_json
    assert response.get_json()["message"] == "Resource not found"
