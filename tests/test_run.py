"""
Test suite for the run module of a Flask application.
This module tests the configuration of the Flask application based on the 
environment variable `FLASK_ENV`.
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

def test_run_config_class(monkeypatch, env, expected_config):
    """
    Test that the run module correctly sets the configuration class based on FLASK_ENV.
    This test patches the load_dotenv function to avoid loading real .env files,
    and patches the create_app function to capture the configuration class used.
    It then imports the run module to trigger the application creation process.
    """
    # Patch load_dotenv pour éviter de charger de vrais fichiers .env
    monkeypatch.setattr("run.load_dotenv", lambda *args, **kwargs: None)

    # Patch app.create_app AVANT d'importer run
    captured = {}
    def fake_create_app(config_class):
        captured["config_class"] = config_class
        class DummyApp:
            config = {"DEBUG": False}
            def run(self, *args, **kwargs):
                pass
        return DummyApp()
    monkeypatch.setattr("app.create_app", fake_create_app)

    # Nettoie le module run du cache sys.modules
    if "run" in sys.modules:
        del sys.modules["run"]
    os.environ["FLASK_ENV"] = env

    # Importe run (ce qui va appeler fake_create_app)
    run_mod = importlib.import_module("run")

    assert hasattr(run_mod, "app")
    assert "config_class" in captured, f"create_app was not called for env={env}"
    assert captured["config_class"] == expected_config
