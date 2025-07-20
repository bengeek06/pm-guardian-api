"""
UserRole API Endpoint Tests

This test module provides exhaustive tests for the /user-roles API endpoints, including:
    - GET /user-roles: List user-role assignments
    - POST /user-roles: Create a new user-role assignment
    - GET /user-roles/<user_role_id>: Retrieve a specific user-role assignment by ID
    - PUT /user-roles/<user_role_id>: Update a user-role assignment
    - PATCH /user-roles/<user_role_id>: Partially update a user-role assignment
    - DELETE /user-roles/<user_role_id>: Delete a user-role assignment

Test coverage includes:
    - Success scenarios
    - Validation errors (missing/invalid fields)
    - Duplicate and integrity errors
    - Database error handling
    - Not found and invalid ID cases

Fixtures:
    - client: Flask test client
    - session: SQLAlchemy session for test DB

Helper functions:
    - create_user_role: Utility to insert a user-role assignment into the test database
"""
import uuid
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.user_role import UserRole

def create_user_role(session, user_id, role_id, company_id):
    """Helper function to create a user-role assignment in the database."""
    user_role = UserRole(
        id=str(uuid.uuid4()),
        user_id=user_id,
        role_id=role_id,
        company_id=company_id
    )
    session.add(user_role)
    session.commit()
    return user_role

############################################################
# GET /user-roles
############################################################
def test_get_user_roles_success(client, session):
    user_id = str(uuid.uuid4())
    role_id = str(uuid.uuid4())
    company_id = str(uuid.uuid4())
    ur1 = create_user_role(session, user_id, role_id, company_id)
    ur2 = create_user_role(session, user_id, str(uuid.uuid4()), company_id)
    resp = client.get("/user-roles")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) >= 2
    ids = [u["id"] for u in data]
    assert ur1.id in ids and ur2.id in ids

def test_get_user_roles_empty(client, session):
    resp = client.get("/user-roles")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)

############################################################
# POST /user-roles
############################################################
def test_post_user_roles_success(client):
    payload = {
        "user_id": str(uuid.uuid4()),
        "role_id": str(uuid.uuid4()),
        "company_id": str(uuid.uuid4())
    }
    resp = client.post("/user-roles", json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["user_id"] == payload["user_id"]
    assert data["role_id"] == payload["role_id"]
    assert data["company_id"] == payload["company_id"]
    assert "id" in data

def test_post_user_roles_missing_field(client):
    payload = {
        "user_id": str(uuid.uuid4()),
        "role_id": str(uuid.uuid4())
        # company_id missing
    }
    resp = client.post("/user-roles", json=payload)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "company_id" in str(data).lower() or "message" in data

def test_post_user_roles_duplicate(client, session):
    user_id = str(uuid.uuid4())
    role_id = str(uuid.uuid4())
    company_id = str(uuid.uuid4())
    create_user_role(session, user_id, role_id, company_id)
    payload = {"user_id": user_id, "role_id": role_id, "company_id": company_id}
    resp = client.post("/user-roles", json=payload)
    assert resp.status_code == 409
    data = resp.get_json()
    assert "message" in data

def test_post_user_roles_db_error(client, monkeypatch):
    def raise_sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("DB error")
    monkeypatch.setattr("app.models.db.db.session.commit", raise_sqlalchemy_error)
    payload = {
        "user_id": str(uuid.uuid4()),
        "role_id": str(uuid.uuid4()),
        "company_id": str(uuid.uuid4())
    }
    resp = client.post("/user-roles", json=payload)
    assert resp.status_code == 500
    data = resp.get_json()
    assert "message" in data

############################################################
# GET /user-roles/<user_role_id>
############################################################
def test_get_user_role_by_id_success(client, session):
    user_id = str(uuid.uuid4())
    role_id = str(uuid.uuid4())
    company_id = str(uuid.uuid4())
    ur = create_user_role(session, user_id, role_id, company_id)
    resp = client.get(f"/user-roles/{ur.id}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == ur.id
    assert data["user_id"] == user_id
    assert data["role_id"] == role_id
    assert data["company_id"] == company_id

def test_get_user_role_by_id_not_found(client):
    non_existent_id = str(uuid.uuid4())
    resp = client.get(f"/user-roles/{non_existent_id}")
    assert resp.status_code == 404
    data = resp.get_json()
    assert "not found" in str(data).lower() or "message" in data

def test_get_user_role_by_id_db_error(client, session, monkeypatch):
    ur = create_user_role(session, str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4()))
    def raise_sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("DB error")
    monkeypatch.setattr("app.models.db.db.session.get", raise_sqlalchemy_error)
    resp = client.get(f"/user-roles/{ur.id}")
    assert resp.status_code == 500
    data = resp.get_json()
    assert "message" in data

############################################################
# PUT /user-roles/<user_role_id>
############################################################
def test_put_user_role_success(client, session):
    user_id = str(uuid.uuid4())
    role_id = str(uuid.uuid4())
    company_id = str(uuid.uuid4())
    ur = create_user_role(session, user_id, role_id, company_id)
    payload = {"user_id": user_id, "role_id": role_id, "company_id": company_id}
    resp = client.put(f"/user-roles/{ur.id}", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == ur.id
    assert data["user_id"] == user_id
    assert data["role_id"] == role_id
    assert data["company_id"] == company_id

def test_put_user_role_not_found(client):
    non_existent_id = str(uuid.uuid4())
    payload = {"user_id": str(uuid.uuid4()), "role_id": str(uuid.uuid4()), "company_id": str(uuid.uuid4())}
    resp = client.put(f"/user-roles/{non_existent_id}", json=payload)
    assert resp.status_code == 404
    data = resp.get_json()
    assert "not found" in str(data).lower() or "message" in data

def test_put_user_role_invalid_data(client, session):
    user_id = str(uuid.uuid4())
    role_id = str(uuid.uuid4())
    company_id = str(uuid.uuid4())
    ur = create_user_role(session, user_id, role_id, company_id)
    payload = {"user_id": "", "role_id": role_id, "company_id": company_id}  # user_id vide
    resp = client.put(f"/user-roles/{ur.id}", json=payload)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "user_id" in str(data).lower() or "message" in data

def test_put_user_role_db_error(client, session, monkeypatch):
    user_id = str(uuid.uuid4())
    role_id = str(uuid.uuid4())
    company_id = str(uuid.uuid4())
    ur = create_user_role(session, user_id, role_id, company_id)
    def raise_sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("DB error")
    monkeypatch.setattr("app.models.db.db.session.commit", raise_sqlalchemy_error)
    payload = {"user_id": user_id, "role_id": role_id, "company_id": company_id}
    resp = client.put(f"/user-roles/{ur.id}", json=payload)
    assert resp.status_code == 500
    data = resp.get_json()
    assert "message" in data

############################################################
# PATCH /user-roles/<user_role_id>
############################################################
def test_patch_user_role_success(client, session):
    user_id = str(uuid.uuid4())
    role_id = str(uuid.uuid4())
    company_id = str(uuid.uuid4())
    ur = create_user_role(session, user_id, role_id, company_id)
    payload = {"role_id": str(uuid.uuid4())}
    resp = client.patch(f"/user-roles/{ur.id}", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == ur.id
    assert data["role_id"] == payload["role_id"]

def test_patch_user_role_not_found(client):
    non_existent_id = str(uuid.uuid4())
    payload = {"role_id": str(uuid.uuid4())}
    resp = client.patch(f"/user-roles/{non_existent_id}", json=payload)
    assert resp.status_code == 404
    data = resp.get_json()
    assert "not found" in str(data).lower() or "message" in data

def test_patch_user_role_invalid_data(client, session):
    user_id = str(uuid.uuid4())
    role_id = str(uuid.uuid4())
    company_id = str(uuid.uuid4())
    ur = create_user_role(session, user_id, role_id, company_id)
    payload = {"user_id": ""}  # user_id vide
    resp = client.patch(f"/user-roles/{ur.id}", json=payload)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "user_id" in str(data).lower() or "message" in data

def test_patch_user_role_db_error(client, session, monkeypatch):
    user_id = str(uuid.uuid4())
    role_id = str(uuid.uuid4())
    company_id = str(uuid.uuid4())
    ur = create_user_role(session, user_id, role_id, company_id)
    def raise_sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("DB error")
    monkeypatch.setattr("app.models.db.db.session.commit", raise_sqlalchemy_error)
    payload = {"role_id": str(uuid.uuid4())}
    resp = client.patch(f"/user-roles/{ur.id}", json=payload)
    assert resp.status_code == 500
    data = resp.get_json()
    assert "message" in data

############################################################
# DELETE /user-roles/<user_role_id>
############################################################
def test_delete_user_role_success(client, session):
    user_id = str(uuid.uuid4())
    role_id = str(uuid.uuid4())
    company_id = str(uuid.uuid4())
    ur = create_user_role(session, user_id, role_id, company_id)
    resp = client.delete(f"/user-roles/{ur.id}")
    assert resp.status_code == 204
    # Optionally, check that the user-role is actually deleted
    get_resp = client.get(f"/user-roles/{ur.id}")
    assert get_resp.status_code == 404

def test_delete_user_role_not_found(client):
    non_existent_id = str(uuid.uuid4())
    resp = client.delete(f"/user-roles/{non_existent_id}")
    assert resp.status_code == 404
    data = resp.get_json()
    assert "not found" in str(data).lower() or "message" in data

def test_delete_user_role_db_error(client, session, monkeypatch):
    user_id = str(uuid.uuid4())
    role_id = str(uuid.uuid4())
    company_id = str(uuid.uuid4())
    ur = create_user_role(session, user_id, role_id, company_id)
    def raise_sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("DB error")
    monkeypatch.setattr("app.models.db.db.session.commit", raise_sqlalchemy_error)
    resp = client.delete(f"/user-roles/{ur.id}")
    assert resp.status_code == 500
    data = resp.get_json()
    assert "message" in data

############################################################
# ADVANCED/EDGE CASES
############################################################
import pytest

@pytest.mark.parametrize("endpoint,method", [
    ("/user-roles/invalid-uuid", "get"),
    ("/user-roles/invalid-uuid", "put"),
    ("/user-roles/invalid-uuid", "patch"),
    ("/user-roles/invalid-uuid", "delete"),
])
def test_invalid_uuid_format(client, endpoint, method):
    """Should return 400 or 404 for invalid UUID format in endpoints."""
    payload = {"user_id": str(uuid.uuid4()), "role_id": str(uuid.uuid4()), "company_id": str(uuid.uuid4())}
    if method == "get":
        resp = client.get(endpoint)
    elif method == "put":
        resp = client.put(endpoint, json=payload)
    elif method == "patch":
        resp = client.patch(endpoint, json={"role_id": str(uuid.uuid4())})
    elif method == "delete":
        resp = client.delete(endpoint)
    else:
        pytest.skip("Unknown method")
        return  # Ensure resp is not used if skipped
    assert resp.status_code in (400, 404)
    data = resp.get_json()
    assert "message" in data

def test_post_user_roles_extra_fields(client):
    """Should return 400 if extra/unexpected fields are provided."""
    payload = {
        "user_id": str(uuid.uuid4()),
        "role_id": str(uuid.uuid4()),
        "company_id": str(uuid.uuid4()),
        "extra_field": "not allowed"
    }
    resp = client.post("/user-roles", json=payload)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "extra" in str(data).lower() or "message" in data

def test_put_user_role_extra_fields(client, session):
    """Should return 400 if extra/unexpected fields are provided on PUT."""
    ur = create_user_role(session, str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4()))
    payload = {
        "user_id": ur.user_id,
        "role_id": ur.role_id,
        "company_id": ur.company_id,
        "extra_field": "not allowed"
    }
    resp = client.put(f"/user-roles/{ur.id}", json=payload)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "extra" in str(data).lower() or "message" in data

def test_patch_user_role_extra_fields(client, session):
    """Should return 400 if extra/unexpected fields are provided on PATCH."""
    ur = create_user_role(session, str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4()))
    payload = {"extra_field": "not allowed"}
    resp = client.patch(f"/user-roles/{ur.id}", json=payload)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "extra" in str(data).lower() or "message" in data

def test_post_user_roles_empty_payload(client):
    """Should return 400 if payload is empty."""
    resp = client.post("/user-roles", json={})
    assert resp.status_code == 400
    data = resp.get_json()
    assert "message" in data or "errors" in data

def test_put_user_role_empty_payload(client, session):
    """Should return 400 if payload is empty on PUT."""
    ur = create_user_role(session, str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4()))
    resp = client.put(f"/user-roles/{ur.id}", json={})
    assert resp.status_code == 400
    data = resp.get_json()
    assert "message" in data or "errors" in data

def test_patch_user_role_empty_payload(client, session):
    """Should return 400 if payload is empty on PATCH."""
    ur = create_user_role(session, str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4()))
    resp = client.patch(f"/user-roles/{ur.id}", json={})
    assert resp.status_code == 400
    data = resp.get_json()
    assert "message" in data or "errors" in data

def test_post_user_roles_whitespace_fields(client):
    """Should return 400 if fields are whitespace-only strings."""
    payload = {"user_id": "   ", "role_id": "\t", "company_id": "\n"}
    resp = client.post("/user-roles", json=payload)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "user_id" in str(data).lower() or "role_id" in str(data).lower() or "company_id" in str(data).lower() or "message" in data

def test_put_user_role_duplicate_assignment(client, session):
    """Should return 409 if PUT would create a duplicate user-role assignment."""
    user_id = str(uuid.uuid4())
    role_id = str(uuid.uuid4())
    company_id = str(uuid.uuid4())
    ur1 = create_user_role(session, user_id, role_id, company_id)
    ur2 = create_user_role(session, str(uuid.uuid4()), str(uuid.uuid4()), company_id)
    payload = {"user_id": user_id, "role_id": role_id, "company_id": company_id}
    resp = client.put(f"/user-roles/{ur2.id}", json=payload)
    assert resp.status_code == 409
    data = resp.get_json()
    assert "already exists" in str(data).lower() or "message" in data

def test_patch_user_role_duplicate_assignment(client, session):
    """Should return 409 if PATCH would create a duplicate user-role assignment."""
    user_id = str(uuid.uuid4())
    role_id = str(uuid.uuid4())
    company_id = str(uuid.uuid4())
    ur1 = create_user_role(session, user_id, role_id, company_id)
    ur2 = create_user_role(session, str(uuid.uuid4()), str(uuid.uuid4()), company_id)
    payload = {"user_id": user_id, "role_id": role_id, "company_id": company_id}
    resp = client.patch(f"/user-roles/{ur2.id}", json=payload)
    assert resp.status_code == 409
    data = resp.get_json()
    assert "already exists" in str(data).lower() or "message" in data