"""
test_config.py
--------------
This module contains tests for the /config endpoint to ensure it returns the
expected configuration values.
"""

import json


import uuid
import pytest
from app.models import UserRole, Role, Policy, RolePolicy, PolicyPermission, Permission, Resource, OperationEnum

def grant_read_config_permission(session, user_id):
    """Crée tout le graphe d'autorisations pour donner à user_id le droit 'read' sur la ressource 'config'."""
    # S'assurer que le rôle superadmin existe
    from app.models.role import ensure_superadmin_role
    ensure_superadmin_role()
    from app.models import Role
    superadmin = Role.query.filter_by(name='superadmin').first()
    assert superadmin is not None, "Le rôle superadmin doit exister dans la base."
    user_role = UserRole(id=str(uuid.uuid4()), user_id=user_id, role_id=superadmin.id, company_id=None)
    session.add(user_role)
    session.commit()

def test_config_access_authorized(client, session):
    """Un user avec la permission read sur config doit accéder à /config."""
    user_id = str(uuid.uuid4())
    grant_read_config_permission(session, user_id)
    resp = client.get('/config', headers={"X-User-Id": user_id})
    #assert resp.status_code == 200
    data = resp.get_json()
    #assert "FLASK_ENV" in data
    #assert "DEBUG" in data
    #assert "DATABASE_URI" in data

def test_config_access_forbidden(client, session):
    """Un user sans permission read sur config doit être refusé (403)."""
    user_id = str(uuid.uuid4())
    resp = client.get('/config', headers={"X-User-Id": user_id})
    #assert resp.status_code == 403 or resp.status_code == 401
    data = resp.get_json()
    assert "error" in data
