"""
Policy API Endpoint Tests

This test module provides exhaustive tests for the /policies API endpoints, including:
    - GET /policies: List policies
    - POST /policies: Create a new policy
    - GET /policies/<policy_id>: Retrieve a specific policy by ID
    - PUT /policies/<policy_id>: Update a policy
    - PATCH /policies/<policy_id>: Partially update a policy
    - DELETE /policies/<policy_id>: Delete a policy

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
    - create_policy: Utility to insert a policy into the test database
"""
import uuid
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.policy import Policy

def create_policy(session, name="TestPolicy"):
    """Helper function to create a policy in the database."""
    policy = Policy(
        id=str(uuid.uuid4()),
        name=name
    )
    session.add(policy)
    session.commit()
    return policy

############################################################
# GET /policies
############################################################
def test_get_policies_success(client, session):
    policy1 = create_policy(session, name="Policy1")
    policy2 = create_policy(session, name="Policy2")
    resp = client.get("/policies")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) >= 2
    names = [p["name"] for p in data]
    assert "Policy1" in names and "Policy2" in names

def test_get_policies_empty(client, session):
    # Assuming DB is empty at start
    resp = client.get("/policies")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)

def test_get_policies_db_error(client, monkeypatch):
    def raise_sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("DB error")
    monkeypatch.setattr(type(Policy.query), "all", lambda self: raise_sqlalchemy_error())
    resp = client.get("/policies")
    assert resp.status_code == 500
    data = resp.get_json()
    assert "message" in data

############################################################
# POST /policies
############################################################
def test_post_policies_success(client):
    payload = {"name": "NewPolicy"}
    resp = client.post("/policies", json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "NewPolicy"
    assert "id" in data

def test_post_policies_missing_name(client):
    payload = {}
    resp = client.post("/policies", json=payload)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "message" in data or "name" in str(data).lower()

def test_post_policies_duplicate(client, session):
    policy = create_policy(session, name="DupPolicy")
    payload = {"name": "DupPolicy"}
    resp = client.post("/policies", json=payload)
    assert resp.status_code == 409
    data = resp.get_json()
    assert "message" in data

def test_post_policies_db_error(client, monkeypatch):
    def raise_sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("DB error")
    monkeypatch.setattr("app.models.db.db.session.commit", raise_sqlalchemy_error)
    payload = {"name": "ErrPolicy"}
    resp = client.post("/policies", json=payload)
    assert resp.status_code == 500
    data = resp.get_json()
    assert "message" in data

############################################################
# GET /policies/<policy_id>
############################################################
def test_get_policy_by_id_success(client, session):
    policy = create_policy(session, name="GetByIdPolicy")
    resp = client.get(f"/policies/{policy.id}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == policy.id
    assert data["name"] == "GetByIdPolicy"

def test_get_policy_by_id_not_found(client):
    non_existent_id = str(uuid.uuid4())
    resp = client.get(f"/policies/{non_existent_id}")
    assert resp.status_code == 404
    data = resp.get_json()
    assert "message" in data and "not found" in str(data["message"]).lower()

def test_get_policy_by_id_db_error(client, monkeypatch, session):
    policy = create_policy(session, name="ErrPolicy")
    def raise_sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("DB error")
    monkeypatch.setattr("app.models.db.db.session.get", raise_sqlalchemy_error)
    resp = client.get(f"/policies/{policy.id}")
    assert resp.status_code == 500
    data = resp.get_json()
    assert "message" in data

############################################################
# PUT /policies/<policy_id>
############################################################
def test_put_policy_success(client, session):
    policy = create_policy(session, name="OldName")
    payload = {"name": "NewName"}
    resp = client.put(f"/policies/{policy.id}", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "NewName"
    assert data["id"] == policy.id

def test_put_policy_not_found(client):
    non_existent_id = str(uuid.uuid4())
    payload = {"name": "AnyName"}
    resp = client.put(f"/policies/{non_existent_id}", json=payload)
    assert resp.status_code == 404
    data = resp.get_json()
    assert "message" in data and "not found" in str(data["message"]).lower()

def test_put_policy_invalid_data(client, session):
    policy = create_policy(session, name="PutInvalid")
    payload = {}  # missing name
    resp = client.put(f"/policies/{policy.id}", json=payload)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "message" in data or "name" in str(data).lower()

def test_put_policy_db_error(client, session, monkeypatch):
    policy = create_policy(session, name="PutErr")
    def raise_sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("DB error")
    monkeypatch.setattr("app.models.db.db.session.commit", raise_sqlalchemy_error)
    payload = {"name": "NewName"}
    resp = client.put(f"/policies/{policy.id}", json=payload)
    assert resp.status_code == 500
    data = resp.get_json()
    assert "message" in data

############################################################
# PATCH /policies/<policy_id>
############################################################
def test_patch_policy_success(client, session):
    policy = create_policy(session, name="PatchMe")
    payload = {"name": "PatchedName"}
    resp = client.patch(f"/policies/{policy.id}", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "PatchedName"
    assert data["id"] == policy.id

def test_patch_policy_not_found(client):
    non_existent_id = str(uuid.uuid4())
    payload = {"name": "AnyName"}
    resp = client.patch(f"/policies/{non_existent_id}", json=payload)
    assert resp.status_code == 404
    data = resp.get_json()
    assert "message" in data and "not found" in str(data["message"]).lower()

def test_patch_policy_invalid_data(client, session):
    policy = create_policy(session, name="PatchInvalid")
    payload = {"name": ""}  # name required, cannot be empty
    resp = client.patch(f"/policies/{policy.id}", json=payload)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "message" in data or "name" in str(data).lower()

def test_patch_policy_db_error(client, session, monkeypatch):
    policy = create_policy(session, name="PatchErr")
    def raise_sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("DB error")
    monkeypatch.setattr("app.models.db.db.session.commit", raise_sqlalchemy_error)
    payload = {"name": "PatchedName"}
    resp = client.patch(f"/policies/{policy.id}", json=payload)
    assert resp.status_code == 500
    data = resp.get_json()
    assert "message" in data

############################################################
# DELETE /policies/<policy_id>
############################################################
def test_delete_policy_success(client, session):
    policy = create_policy(session, name="DeleteMe")
    resp = client.delete(f"/policies/{policy.id}")
    assert resp.status_code == 204

def test_delete_policy_not_found(client):
    non_existent_id = str(uuid.uuid4())
    resp = client.delete(f"/policies/{non_existent_id}")
    assert resp.status_code == 404
    data = resp.get_json()
    assert "message" in data and "not found" in str(data["message"]).lower()

def test_delete_policy_db_error(client, session, monkeypatch):
    policy = create_policy(session, name="DeleteErr")
    def raise_sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("DB error")
    monkeypatch.setattr("app.models.db.db.session.commit", raise_sqlalchemy_error)
    resp = client.delete(f"/policies/{policy.id}")
    assert resp.status_code == 500
    data = resp.get_json()
    assert "message" in data
