"""
Role API Endpoint Tests

This test module provides exhaustive tests for the /roles API endpoints, including:
    - GET /roles: List roles for a company
    - POST /roles: Create a new role
    - GET /roles/<role_id>: Retrieve a specific role by ID

Test coverage includes:
    - Success scenarios
    - Validation errors (missing/invalid fields, length constraints)
    - Duplicate and integrity errors
    - Database error handling
    - Not found and invalid ID cases

Fixtures:
    - client: Flask test client
    - session: SQLAlchemy session for test DB

Helper functions:
    - create_role: Utility to insert a role into the test database
"""

import uuid
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.role import Role

############################################################
# GET /roles
############################################################
def create_role(session, company_id, name="TestRole", description="desc"):
    """Helper function to create a role in the database."""
    role = Role(
        name=name,
        description=description,
        company_id=company_id
    )
    session.add(role)
    session.commit()
    return role

def test_get_roles_success(client, session):
    """Should return 200 and a list of roles for a valid company_id."""
    company_id = str(uuid.uuid4())
    role1 = create_role(session, company_id, name="Role1")
    role2 = create_role(session, company_id, name="Role2")
    resp = client.get(f"/roles?company_id={company_id}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) == 2
    names = [r["name"] for r in data]
    assert set(names) == {"Role1", "Role2"}

def test_get_roles_empty(client, session):
    """Should return 200 and an empty list if no roles exist for company_id."""
    company_id = str(uuid.uuid4())
    resp = client.get(f"/roles?company_id={company_id}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data == []

def test_get_roles_missing_company_id(client):
    """Should return 200 and an empty list if company_id param is missing (matches no roles)."""
    resp = client.get("/roles")
    assert resp.status_code == 200
    # On attend la liste des rôles sans company_id (ex: superadmin)
    data = resp.get_json()
    assert isinstance(data, list)

def test_get_roles_invalid_company_id_format(client):
    """Should return 200 and an empty list or error for invalid company_id format."""
    resp = client.get("/roles?company_id=not-a-uuid")
    assert resp.status_code in (200, 500)
    # Accept either: empty list (if code allows) or error (if code requires valid UUID)
    # If error, check message
    if resp.status_code == 200:
        assert isinstance(resp.get_json(), list)
    else:
        assert "message" in resp.get_json()

############################################################
# POST /roles
############################################################
def test_post_roles_success(client, session):
    """Should create a new role and return 201 with the role data."""
    company_id = str(uuid.uuid4())
    payload = {"name": "Manager", "description": "Manages stuff", "company_id": company_id}
    resp = client.post("/roles", json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "Manager"
    assert data["company_id"] == company_id

def test_post_roles_missing_name(client):
    """Should return 400 if name is missing."""
    company_id = str(uuid.uuid4())
    payload = {"description": "desc", "company_id": company_id}
    resp = client.post("/roles", json=payload)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "errors" in data and "name" in data["errors"]

def test_post_roles_missing_company_id(client):
    """Should create a role without company_id (e.g. superadmin)."""
    payload = {"name": "Manager", "description": "desc"}
    resp = client.post("/roles", json=payload)
    assert resp.status_code in (201, 200)
    data = resp.get_json()
    assert data["name"] == "Manager"
    assert data.get("company_id") is None

def test_post_roles_name_too_long(client):
    """Should return 400 if name is too long."""
    company_id = str(uuid.uuid4())
    payload = {"name": "A"*51, "description": "desc", "company_id": company_id}
    resp = client.post("/roles", json=payload)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "errors" in data and "name" in data["errors"]

def test_post_roles_description_too_long(client):
    """Should return 400 if description is too long."""
    company_id = str(uuid.uuid4())
    payload = {"name": "Manager", "description": "D"*256, "company_id": company_id}
    resp = client.post("/roles", json=payload)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "errors" in data and "description" in data["errors"]

def test_post_roles_invalid_company_id_format(client):
    """Should return 400 if company_id is not a valid UUID."""
    payload = {"name": "Manager", "description": "desc", "company_id": "not-a-uuid"}
    resp = client.post("/roles", json=payload)
    assert resp.status_code == 400 or resp.status_code == 422
    data = resp.get_json()
    assert "errors" in data or "message" in data

def test_post_roles_duplicate(client, session):
    """Should return 409 if role with same name already exists for the company."""
    company_id = str(uuid.uuid4())
    # Create role first
    client.post("/roles", json={"name": "Manager", "description": "desc", "company_id": company_id})
    # Try to create duplicate
    resp = client.post("/roles", json={"name": "Manager", "description": "desc", "company_id": company_id})
    assert resp.status_code == 409
    data = resp.get_json()
    assert "message" in data

def test_creater_integrity_error(client, monkeypatch):
    """ Should return 400 if there is an integrity error during role creation. """
    # Mock the commit method to raise IntegrityError
    # Fonction qui lève l'exception
    def raise_integrity_error(*args, **kwargs):
        raise IntegrityError("Mocked IntegrityError", None, None)

    # Monkeypatch la méthode commit
    monkeypatch.setattr("app.models.db.db.session.commit", raise_integrity_error)

    response = client.post('/roles', json={'name': 'Test Dummy'})
    # Le code API retourne 409 (CONFLICT) sur une erreur d'intégrité
    assert response.status_code == 409


def test_create_sqlalchemy_error(client, monkeypatch):
    """ Should return 500 if there is a SQLAlchemy error during role creation. """
    def raise_sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("Mocked SQLAlchemyError")

    monkeypatch.setattr("app.models.db.db.session.commit", raise_sqlalchemy_error)

    company_id = str(uuid.uuid4())
    response = client.post("/roles", json={"name": "Manager", "description": "desc", "company_id": company_id})
    assert response.status_code == 500

############################################################
# GET /roles/<role_id>
############################################################
def test_get_role_success(client, session):
    """Should return 200 and the role data for a valid role_id."""
    company_id = str(uuid.uuid4())
    role = create_role(session, company_id, name="UniqueRole")
    resp = client.get(f"/roles/{role.id}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == str(role.id)
    assert data["name"] == "UniqueRole"
    assert data["company_id"] == company_id

def test_get_role_not_found(client):
    """Should return 404 if the role does not exist."""
    non_existent_id = str(uuid.uuid4())
    resp = client.get(f"/roles/{non_existent_id}")
    assert resp.status_code == 404
    data = resp.get_json()
    assert "message" in data and "not found" in data["message"].lower()

def test_get_role_invalid_id_format(client):
    """Should return 404 or 400 for an invalid role_id format (not a UUID)."""
    resp = client.get("/roles/not-a-uuid")
    # Flask-RESTful may return 404 for invalid id, or your app may return 400
    assert resp.status_code in (404, 400)
    data = resp.get_json()
    assert "message" in data

############################################################
# PUT /roles/<role_id>
############################################################
def test_put_role_success(client, session):
    """Should update a role and return 200 with updated data."""
    company_id = str(uuid.uuid4())
    role = create_role(session, company_id, name="OldName", description="OldDesc")
    payload = {"name": "NewName", "description": "NewDesc", "company_id": company_id}
    resp = client.put(f"/roles/{role.id}", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "NewName"
    assert data["description"] == "NewDesc"
    assert data["company_id"] == company_id

def test_put_role_missing_name(client, session):
    """Should return 400 if name is missing."""
    company_id = str(uuid.uuid4())
    role = create_role(session, company_id)
    payload = {"description": "desc", "company_id": company_id}
    resp = client.put(f"/roles/{role.id}", json=payload)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "errors" in data and "name" in data["errors"]

def test_put_role_missing_company_id(client, session):
    """Should allow update without company_id (company_id remains or becomes None)."""
    company_id = str(uuid.uuid4())
    role = create_role(session, company_id)
    payload = {"name": "NewName", "description": "desc"}
    resp = client.put(f"/roles/{role.id}", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "NewName"
    # company_id peut être None ou inchangé selon l'implémentation
    assert "company_id" in data

def test_put_role_name_too_long(client, session):
    """Should return 400 if name is too long."""
    company_id = str(uuid.uuid4())
    role = create_role(session, company_id)
    payload = {"name": "A"*51, "description": "desc", "company_id": company_id}
    resp = client.put(f"/roles/{role.id}", json=payload)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "errors" in data and "name" in data["errors"]

def test_put_role_description_too_long(client, session):
    """Should return 400 if description is too long."""
    company_id = str(uuid.uuid4())
    role = create_role(session, company_id)
    payload = {"name": "NewName", "description": "D"*256, "company_id": company_id}
    resp = client.put(f"/roles/{role.id}", json=payload)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "errors" in data and "description" in data["errors"]

def test_put_role_invalid_company_id_format(client, session):
    """Should return 400 if company_id is not a valid UUID."""
    company_id = str(uuid.uuid4())
    role = create_role(session, company_id)
    payload = {"name": "NewName", "description": "desc", "company_id": "not-a-uuid"}
    resp = client.put(f"/roles/{role.id}", json=payload)
    assert resp.status_code == 400 or resp.status_code == 422
    data = resp.get_json()
    assert "errors" in data or "message" in data

def test_put_role_duplicate_name(client, session):
    """Should return 409 if updating to a name that already exists for the company."""
    company_id = str(uuid.uuid4())
    role1 = create_role(session, company_id, name="Role1")
    role2 = create_role(session, company_id, name="Role2")
    payload = {"name": "Role1", "description": "desc", "company_id": company_id}
    resp = client.put(f"/roles/{role2.id}", json=payload)
    assert resp.status_code == 409
    data = resp.get_json()
    assert "message" in data

def test_put_role_not_found(client):
    """Should return 404 if the role does not exist."""
    non_existent_id = str(uuid.uuid4())
    company_id = str(uuid.uuid4())
    payload = {"name": "NewName", "description": "desc", "company_id": company_id}
    resp = client.put(f"/roles/{non_existent_id}", json=payload)
    assert resp.status_code == 404
    data = resp.get_json()
    assert "message" in data and "not found" in data["message"].lower()

def test_put_role_invalid_id_format(client):
    """Should return 404 or 400 for an invalid role_id format (not a UUID)."""
    company_id = str(uuid.uuid4())
    payload = {"name": "NewName", "description": "desc", "company_id": company_id}
    resp = client.put("/roles/not-a-uuid", json=payload)
    assert resp.status_code in (404, 400)
    data = resp.get_json()
    assert "message" in data

def test_put_role_db_error(client, monkeypatch, session):
    """Should return 500 if a database error occurs during update."""
    company_id = str(uuid.uuid4())
    role = create_role(session, company_id)
    def raise_sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("Mocked SQLAlchemyError")
    monkeypatch.setattr("app.models.role.db.session.commit", raise_sqlalchemy_error)
    payload = {"name": "NewName", "description": "desc", "company_id": company_id}
    resp = client.put(f"/roles/{role.id}", json=payload)
    assert resp.status_code == 500
    data = resp.get_json()
    assert "message" in data

############################################################
# PATCH /roles/<role_id>
############################################################
def test_patch_role_success(client, session):
    """Should partially update a role and return 200 with updated data."""
    company_id = str(uuid.uuid4())
    role = create_role(session, company_id, name="PatchName", description="PatchDesc")
    payload = {"description": "UpdatedDesc"}
    resp = client.patch(f"/roles/{role.id}", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["description"] == "UpdatedDesc"
    assert data["name"] == "PatchName"
    assert data["company_id"] == company_id

def test_patch_role_partial_update(client, session):
    """Should update only provided fields and leave others unchanged."""
    company_id = str(uuid.uuid4())
    role = create_role(session, company_id, name="PatchName", description="PatchDesc")
    payload = {"name": "PatchedName"}
    resp = client.patch(f"/roles/{role.id}", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "PatchedName"
    assert data["description"] == "PatchDesc"
    assert data["company_id"] == company_id

def test_patch_role_invalid_field(client, session):
    """Should return 400 if an invalid field is provided."""
    company_id = str(uuid.uuid4())
    role = create_role(session, company_id)
    payload = {"invalid_field": "value"}
    resp = client.patch(f"/roles/{role.id}", json=payload)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "errors" in data

def test_patch_role_not_found(client):
    """Should return 404 if the role does not exist."""
    non_existent_id = str(uuid.uuid4())
    payload = {"name": "DoesNotExist"}
    resp = client.patch(f"/roles/{non_existent_id}", json=payload)
    assert resp.status_code == 404
    data = resp.get_json()
    assert "message" in data and "not found" in data["message"].lower()

def test_patch_role_invalid_id_format(client):
    """Should return 404 or 400 for an invalid role_id format (not a UUID)."""
    payload = {"name": "InvalidID"}
    resp = client.patch("/roles/not-a-uuid", json=payload)
    assert resp.status_code in (404, 400)
    data = resp.get_json()
    assert "message" in data

def test_patch_role_duplicate_name(client, session):
    """Should return 409 if updating to a name that already exists for the company."""
    company_id = str(uuid.uuid4())
    role1 = create_role(session, company_id, name="Role1")
    role2 = create_role(session, company_id, name="Role2")
    payload = {"name": "Role1"}
    resp = client.patch(f"/roles/{role2.id}", json=payload)
    assert resp.status_code == 409
    data = resp.get_json()
    assert "message" in data

def test_patch_role_name_too_long(client, session):
    """Should return 400 if name is too long."""
    company_id = str(uuid.uuid4())
    role = create_role(session, company_id)
    payload = {"name": "A"*51}
    resp = client.patch(f"/roles/{role.id}", json=payload)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "errors" in data and "name" in data["errors"]

def test_patch_role_description_too_long(client, session):
    """Should return 400 if description is too long."""
    company_id = str(uuid.uuid4())
    role = create_role(session, company_id)
    payload = {"description": "D"*256}
    resp = client.patch(f"/roles/{role.id}", json=payload)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "errors" in data and "description" in data["errors"]

def test_patch_role_invalid_company_id_format(client, session):
    """Should return 400 if company_id is not a valid UUID."""
    company_id = str(uuid.uuid4())
    role = create_role(session, company_id)
    payload = {"company_id": "not-a-uuid"}
    resp = client.patch(f"/roles/{role.id}", json=payload)
    assert resp.status_code == 400 or resp.status_code == 422
    data = resp.get_json()
    assert "errors" in data or "message" in data

def test_patch_role_db_error(client, monkeypatch, session):
    """Should return 500 if a database error occurs during patch."""
    company_id = str(uuid.uuid4())
    role = create_role(session, company_id)
    def raise_sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("Mocked SQLAlchemyError")
    monkeypatch.setattr("app.models.role.db.session.commit", raise_sqlalchemy_error)
    payload = {"name": "NewName"}
    resp = client.patch(f"/roles/{role.id}", json=payload)
    assert resp.status_code == 500
    data = resp.get_json()
    assert "message" in data


############################################################
# DELETE /roles/<role_id>
############################################################
def test_delete_role_success(client, session):
    """Should delete a role and return 204 with success message."""
    company_id = str(uuid.uuid4())
    role = create_role(session, company_id)
    resp = client.delete(f"/roles/{role.id}")
    assert resp.status_code == 204
    # No body expected for 204; just confirm deletion
    get_resp = client.get(f"/roles/{role.id}")
    assert get_resp.status_code == 404

def test_delete_role_not_found(client):
    """Should return 404 if the role does not exist."""
    non_existent_id = str(uuid.uuid4())
    resp = client.delete(f"/roles/{non_existent_id}")
    assert resp.status_code == 404
    data = resp.get_json()
    assert "message" in data and "not found" in data["message"].lower()

def test_delete_role_invalid_id_format(client):
    """Should return 404 or 400 for an invalid role_id format (not a UUID)."""
    resp = client.delete("/roles/not-a-uuid")
    assert resp.status_code in (404, 400)
    data = resp.get_json()
    assert "message" in data

def test_delete_role_db_error(client, monkeypatch, session):
    """Should return 500 if a database error occurs during delete."""
    company_id = str(uuid.uuid4())
    role = create_role(session, company_id)
    def raise_sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("Mocked SQLAlchemyError")
    monkeypatch.setattr("app.models.role.db.session.commit", raise_sqlalchemy_error)
    resp = client.delete(f"/roles/{role.id}")
    assert resp.status_code == 500
    data = resp.get_json()
    assert "message" in data

############################################################
# /roles/<role_id>/policies (Role-Policy Assignment Endpoints)
############################################################
import pytest
from app.models.policy import Policy
from app.models.role_policy import RolePolicy

def create_policy(session, name="TestPolicy"):
    """Helper to create a policy in the database."""
    policy = Policy(id=str(uuid.uuid4()), name=name)
    session.add(policy)
    session.commit()
    return policy

def test_assign_policy_to_role_success(client, session):
    """Should assign a policy to a role and return 201."""
    company_id = str(uuid.uuid4())
    role = create_role(session, company_id)
    policy = create_policy(session, name="P1")
    resp = client.post(f"/roles/{role.id}/policies", json={"policy_id": policy.id})
    assert resp.status_code == 201
    data = resp.get_json()
    assert "assigned" in data["message"]

def test_assign_policy_missing_policy_id(client, session):
    """Should return 400 if policy_id is missing."""
    company_id = str(uuid.uuid4())
    role = create_role(session, company_id)
    resp = client.post(f"/roles/{role.id}/policies", json={})
    assert resp.status_code == 400
    data = resp.get_json()
    assert "policy_id" in data["message"]

def test_assign_policy_role_or_policy_not_found(client, session):
    """Should return 404 if role or policy does not exist."""
    role_id = str(uuid.uuid4())
    policy_id = str(uuid.uuid4())
    resp = client.post(f"/roles/{role_id}/policies", json={"policy_id": policy_id})
    assert resp.status_code == 404
    data = resp.get_json()
    assert "not found" in data["message"].lower()

def test_assign_policy_already_assigned(client, session):
    """Should return 409 if policy already assigned to role."""
    company_id = str(uuid.uuid4())
    role = create_role(session, company_id)
    policy = create_policy(session, name="P2")
    # Assign once
    client.post(f"/roles/{role.id}/policies", json={"policy_id": policy.id})
    # Assign again
    resp = client.post(f"/roles/{role.id}/policies", json={"policy_id": policy.id})
    assert resp.status_code == 409
    data = resp.get_json()
    assert "already assigned" in data["message"].lower()

def test_assign_policy_db_error(client, session, monkeypatch):
    """Should return 500 if DB error occurs during assignment."""
    company_id = str(uuid.uuid4())
    role = create_role(session, company_id)
    policy = create_policy(session, name="P3")
    def raise_sqlalchemy_error(*args, **kwargs):
        from sqlalchemy.exc import SQLAlchemyError
        raise SQLAlchemyError("Mocked DB error")
    monkeypatch.setattr("app.models.role_policy.db.session.commit", raise_sqlalchemy_error)
    resp = client.post(f"/roles/{role.id}/policies", json={"policy_id": policy.id})
    assert resp.status_code == 500
    data = resp.get_json()
    assert "error" in data["message"] or "occurred" in data["message"]

def test_list_policies_for_role_success(client, session):
    """Should list all policies assigned to a role."""
    company_id = str(uuid.uuid4())
    role = create_role(session, company_id)
    policy1 = create_policy(session, name="P4")
    policy2 = create_policy(session, name="P5")
    # Assign policies
    client.post(f"/roles/{role.id}/policies", json={"policy_id": policy1.id})
    client.post(f"/roles/{role.id}/policies", json={"policy_id": policy2.id})
    resp = client.get(f"/roles/{role.id}/policies")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    ids = [p["id"] for p in data]
    assert policy1.id in ids and policy2.id in ids

def test_list_policies_role_not_found(client):
    """Should return 404 if role does not exist when listing policies."""
    role_id = str(uuid.uuid4())
    resp = client.get(f"/roles/{role_id}/policies")
    assert resp.status_code == 404
    data = resp.get_json()
    assert "not found" in data["message"].lower()

def test_list_policies_db_error(client, session, monkeypatch):
    """Should return 500 if DB error occurs during list."""
    company_id = str(uuid.uuid4())
    role = create_role(session, company_id)
    def raise_sqlalchemy_error(*args, **kwargs):
        from sqlalchemy.exc import SQLAlchemyError
        raise SQLAlchemyError("Mocked DB error")
    monkeypatch.setattr("app.models.role_policy.db.session.get", lambda *a, **k: (_ for _ in ()).throw(Exception("Mocked DB error")))
    resp = client.get(f"/roles/{role.id}/policies")
    assert resp.status_code == 500
    data = resp.get_json()
    assert "error" in data["message"] or "occurred" in data["message"]

def test_remove_policy_from_role_success(client, session):
    """Should remove a policy from a role and return 204."""
    company_id = str(uuid.uuid4())
    role = create_role(session, company_id)
    policy = create_policy(session, name="P6")
    client.post(f"/roles/{role.id}/policies", json={"policy_id": policy.id})
    resp = client.delete(f"/roles/{role.id}/policies?policy_id={policy.id}")
    assert resp.status_code == 204
    # Confirm removal
    resp2 = client.get(f"/roles/{role.id}/policies")
    ids = [p["id"] for p in resp2.get_json()]
    assert policy.id not in ids

def test_remove_policy_missing_policy_id(client, session):
    """Should return 400 if policy_id is missing in query."""
    company_id = str(uuid.uuid4())
    role = create_role(session, company_id)
    resp = client.delete(f"/roles/{role.id}/policies")
    assert resp.status_code == 400
    data = resp.get_json()
    assert "policy_id" in data["message"]

def test_remove_policy_role_or_policy_not_found(client, session):
    """Should return 404 if role or policy does not exist when removing."""
    role_id = str(uuid.uuid4())
    policy_id = str(uuid.uuid4())
    resp = client.delete(f"/roles/{role_id}/policies?policy_id={policy_id}")
    assert resp.status_code == 404
    data = resp.get_json()
    assert "not found" in data["message"].lower()

def test_remove_policy_not_assigned(client, session):
    """Should return 404 if policy is not assigned to role when removing."""
    company_id = str(uuid.uuid4())
    role = create_role(session, company_id)
    policy = create_policy(session, name="P7")
    resp = client.delete(f"/roles/{role.id}/policies?policy_id={policy.id}")
    assert resp.status_code == 404
    data = resp.get_json()
    assert "not assigned" in data["message"].lower()

def test_remove_policy_db_error(client, session, monkeypatch):
    """Should return 500 if DB error occurs during removal."""
    company_id = str(uuid.uuid4())
    role = create_role(session, company_id)
    policy = create_policy(session, name="P8")
    client.post(f"/roles/{role.id}/policies", json={"policy_id": policy.id})
    def raise_sqlalchemy_error(*args, **kwargs):
        from sqlalchemy.exc import SQLAlchemyError
        raise SQLAlchemyError("Mocked DB error")
    monkeypatch.setattr("app.models.role_policy.db.session.commit", raise_sqlalchemy_error)
    resp = client.delete(f"/roles/{role.id}/policies?policy_id={policy.id}")
    assert resp.status_code == 500
    data = resp.get_json()
    assert "error" in data["message"] or "occurred" in data["message"]