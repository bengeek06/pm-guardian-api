"""
test_wsgi.py
------------
This module contains tests for the WSGI entrypoint to ensure the correct configuration
class is selected based on the FLASK_ENV environment variable.
"""
import importlib
import sys
import os
import pytest

@pytest.mark.parametrize("env,expected_config", [
    ("production", "app.config.ProductionConfig"),
    ("staging", "app.config.StagingConfig"),
    ("testing", "app.config.TestingConfig"),
    ("development", "app.config.DevelopmentConfig"),
    ("unknown", "app.config.DevelopmentConfig"),
])


def test_wsgi_config_class(monkeypatch, env, expected_config):
    """
    Test that the WSGI entrypoint selects the correct configuration class
    based on the FLASK_ENV environment variable.

    This test patches load_dotenv and app.create_app to avoid side effects,
    sets the FLASK_ENV, imports the wsgi module, and checks that the correct
    config class is passed to create_app.
    """
    # Patch load_dotenv to avoid loading real .env files
    monkeypatch.setattr("wsgi.load_dotenv", lambda *args, **kwargs: None)

    # Patch app.create_app BEFORE importing wsgi
    captured = {}
    def fake_create_app(config_class):
        captured["config_class"] = config_class
        class DummyApp:
            pass
        return DummyApp()
    monkeypatch.setattr("app.create_app", fake_create_app)

    if "wsgi" in sys.modules:
        del sys.modules["wsgi"]
    os.environ["FLASK_ENV"] = env

    wsgi = importlib.import_module("wsgi")

    assert hasattr(wsgi, "app")
    assert "config_class" in captured, f"create_app was not called for env={env}"
    assert captured["config_class"] == expected_config
