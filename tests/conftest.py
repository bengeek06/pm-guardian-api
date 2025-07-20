"""
conftest.py
-----------
Fixtures et configuration pour les tests du projet PM Guardian API.
"""

import os
import uuid
import pytest
from dotenv import load_dotenv
from app import create_app
from app.models.db import db
from app.models.policy import Policy
from app.models.resource import Resource as ResourceModel
from app.models.permission import Permission

# Chargement de l'environnement de test
os.environ['FLASK_ENV'] = 'testing'
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env.test'))

@pytest.fixture(scope="session")
def app():
    """
    Crée et configure l'application Flask pour les tests.
    Initialise la base, crée et drop toutes les tables pour chaque session de test.
    """
    app = create_app('app.config.TestingConfig')
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """
    Fournit un client Flask pour les requêtes HTTP de test.
    """
    return app.test_client()

@pytest.fixture
def session(app):
    """
    Fournit une session SQLAlchemy liée à l'app Flask de test.
    """
    with app.app_context():
        yield db.session
        db.session.remove()

@pytest.fixture(autouse=True)
def reset_database(app):
    """
    Réinitialise la base de données avant chaque test pour garantir une isolation parfaite.
    Drop puis recreate toutes les tables.
    """
    with app.app_context():
        db.drop_all()
        db.create_all()

@pytest.fixture
def resource(session):
    """
    Permet de créer une ressource de test liée à un company_id.
    Nettoie les ressources créées après chaque test.
    """
    created_resources = []

    def _create_resource(company_id):
        res = ResourceModel(
            id=str(uuid.uuid4()),
            name="test_resource",
            description="Ressource de test pour les permissions.",
            company_id=company_id
        )
        session.add(res)
        session.commit()
        created_resources.append(res)
        return res

    yield _create_resource

    for res in created_resources:
        # Delete dependent permissions first
        session.query(Permission).filter_by(resource_id=res.id).delete()
        session.delete(res)
    session.commit()
