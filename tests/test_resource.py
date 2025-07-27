"""
Resource API Endpoint Tests

This test module provides exhaustive tests for the /resources API endpoints, including:
    - GET /resources: List resources for a company
    - POST /resources: Create a new resource
    - GET /resources/<resources_id>: Retrieve a specific resource by ID

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
    - create_resource: Utility to insert a resource into the test database
"""

import uuid
from sqlalchemy.exc import SQLAlchemyError
from app.models.resource import Resource


############################################################
# GET /resources
############################################################
def create_resource(session, name="TestResource", description="desc"):
    """Helper function to create a resource in the database."""
    resource = Resource(
        name=name,
        description=description
    )
    session.add(resource)
    session.commit()
    return resource

def test_get_resources_success(client, session):
    """Should return 200 and a list of resources for a valid company_id."""
    res1 = create_resource(session, name="Res1")
    res2 = create_resource(session, name="Res2")
    resp = client.get("/resources")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) == 2
    names = [r["name"] for r in data]
    assert set(names) == {"Res1", "Res2"}

def test_get_resources_empty(client, session):
    """Should return 200 and an empty list if no resources exist for company_id."""
    resp = client.get("/resources")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data == []

def test_get_resources_missing_company_id(client):
    """Should return 200 and an empty list if no resources exist."""
    resp = client.get("/resources")
    assert resp.status_code == 200
    assert resp.get_json() == []

def test_get_resources_invalid_company_id_format(client):
    """Should return 200 and an empty list for a query param that is ignored."""
    resp = client.get("/resources?company_id=not-a-uuid")
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)



############################################################
# POST /resources
############################################################
def test_post_resources_success(client, session):
    """Should create a new resource and return 201 with the resource data."""
    payload = {"name": "Resource1", "description": "desc"}
    resp = client.post("/resources", json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "Resource1"

def test_post_resources_missing_name(client):
    """Should return 400 if name is missing."""
    company_id = str(uuid.uuid4())
    payload = {"description": "desc", "company_id": company_id}
    resp = client.post("/resources", json=payload)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "name" in str(data).lower() or "message" in data

def test_post_resources_missing_company_id(client):
    """Should return 201 if company_id is missing (now optional)."""
    payload = {"name": "Resource1", "description": "desc"}
    resp = client.post("/resources", json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "Resource1"

def test_post_resources_name_too_long(client):
    """Should return 400 if name is too long."""
    company_id = str(uuid.uuid4())
    payload = {"name": "A"*51, "description": "desc", "company_id": company_id}
    resp = client.post("/resources", json=payload)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "name" in str(data).lower() or "message" in data

def test_post_resources_description_too_long(client):
    """Should return 400 if description is too long."""
    company_id = str(uuid.uuid4())
    payload = {"name": "Resource1", "description": "D"*256, "company_id": company_id}
    resp = client.post("/resources", json=payload)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "description" in str(data).lower() or "message" in data

def test_post_resources_duplicate(client, session):
    """Should return 409 if resource with same name already exists for the company."""
    client.post("/resources", json={"name": "Resource1", "description": "desc"})
    resp = client.post("/resources", json={"name": "Resource1", "description": "desc"})
    assert resp.status_code == 409
    data = resp.get_json()
    assert "message" in data

def test_post_resources_db_error(client, monkeypatch):
    """Should return 500 if a database error occurs during resource creation."""
    def raise_sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("Mocked SQLAlchemyError")
    monkeypatch.setattr("app.models.db.db.session.commit", raise_sqlalchemy_error)
    company_id = str(uuid.uuid4())
    resp = client.post("/resources", json={"name": "Resource1", "description": "desc"})
    assert resp.status_code == 500
    data = resp.get_json()
    assert "message" in data


############################################################
# GET /resources/<resource_id>
############################################################
def test_get_resource_by_id_success(client, session):
    """Should return 200 and the resource data for a valid resource_id."""
    resource = create_resource(session, name="Res1")
    resp = client.get(f"/resources/{resource.id}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == str(resource.id)
    assert data["name"] == "Res1"

def test_get_resource_by_id_not_found(client):
    """Should return 404 if the resource does not exist."""
    non_existent_id = str(uuid.uuid4())
    resp = client.get(f"/resources/{non_existent_id}")
    assert resp.status_code == 404
    data = resp.get_json()
    assert "not found" in str(data).lower() or "message" in data

def test_get_resource_by_id_invalid_format(client):
    """Should return 404 or 500 for an invalid resource_id format (not a UUID)."""
    resp = client.get("/resources/not-a-uuid")
    assert resp.status_code in (404, 500)
    data = resp.get_json()
    assert "message" in data


############################################################
# PUT /resources/<resource_id>
############################################################
def test_put_resource_success(client, session):
    """Should update the resource and return 200 with updated data."""
    resource = create_resource(session, name="Res1", description="desc")
    payload = {"name": "UpdatedName", "description": "updated desc"}
    resp = client.put(f"/resources/{resource.id}", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == str(resource.id)
    assert data["name"] == "UpdatedName"
    assert data["description"] == "updated desc"

def test_put_resource_not_found(client):
    """Should return 404 if the resource does not exist."""
    non_existent_id = str(uuid.uuid4())
    payload = {"name": "Name", "description": "desc"}
    resp = client.put(f"/resources/{non_existent_id}", json=payload)
    assert resp.status_code == 404
    data = resp.get_json()
    assert "not found" in str(data).lower() or "message" in data

def test_put_resource_invalid_data(client, session):
    """Should return 400 if the payload is invalid (e.g., name too long)."""
    resource = create_resource(session, name="Res1")
    payload = {"name": "A"*51, "description": "desc"}
    resp = client.put(f"/resources/{resource.id}", json=payload)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "name" in str(data).lower() or "message" in data

def test_put_resource_db_error(client, session, monkeypatch):
    """Should return 500 if a database error occurs during update."""
    resource = create_resource(session, name="Res1")
    def raise_sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("Mocked SQLAlchemyError")
    monkeypatch.setattr("app.models.db.db.session.commit", raise_sqlalchemy_error)
    payload = {"name": "Res1", "description": "desc"}
    resp = client.put(f"/resources/{resource.id}", json=payload)
    assert resp.status_code == 500
    data = resp.get_json()
    assert "message" in data


############################################################
# PATCH /resources/<resource_id>
############################################################
def test_patch_resource_success(client, session):
    """Should partially update the resource and return 200 with updated data."""
    resource = create_resource(session, name="Res1", description="desc")
    payload = {"description": "patched desc"}
    resp = client.patch(f"/resources/{resource.id}", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == str(resource.id)
    assert data["description"] == "patched desc"
    assert data["name"] == "Res1"

def test_patch_resource_not_found(client):
    """Should return 404 if the resource does not exist."""
    non_existent_id = str(uuid.uuid4())
    payload = {"description": "patched desc"}
    resp = client.patch(f"/resources/{non_existent_id}", json=payload)
    assert resp.status_code == 404
    data = resp.get_json()
    assert "not found" in str(data).lower() or "message" in data

def test_patch_resource_invalid_data(client, session):
    """Should return 400 if the payload is invalid (e.g., name too long)."""
    resource = create_resource(session, name="Res1")
    payload = {"name": "A"*51}
    resp = client.patch(f"/resources/{resource.id}", json=payload)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "name" in str(data).lower() or "message" in data

def test_patch_resource_db_error(client, session, monkeypatch):
    """Should return 500 if a database error occurs during partial update."""
    resource = create_resource(session, name="Res1")
    def raise_sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("Mocked SQLAlchemyError")
    monkeypatch.setattr("app.models.db.db.session.commit", raise_sqlalchemy_error)
    payload = {"description": "desc"}
    resp = client.patch(f"/resources/{resource.id}", json=payload)
    assert resp.status_code == 500
    data = resp.get_json()
    assert "message" in data


############################################################
# DELETE /resources/<resource_id>
############################################################
def test_delete_resource_success(client, session):
    """Should delete the resource and return 204 with no content."""
    resource = create_resource(session, name="Res1")
    resp = client.delete(f"/resources/{resource.id}")
    assert resp.status_code == 204
    # Optionally, check that the resource is actually deleted
    get_resp = client.get(f"/resources/{resource.id}")
    assert get_resp.status_code == 404

def test_delete_resource_not_found(client):
    """Should return 404 if the resource does not exist."""
    non_existent_id = str(uuid.uuid4())
    resp = client.delete(f"/resources/{non_existent_id}")
    assert resp.status_code == 404
    data = resp.get_json()
    assert "not found" in str(data).lower() or "message" in data

def test_delete_resource_db_error(client, session, monkeypatch):
    """Should return 500 if a database error occurs during deletion."""
    resource = create_resource(session, name="Res1")
    def raise_sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("Mocked SQLAlchemyError")
    monkeypatch.setattr("app.models.db.db.session.commit", raise_sqlalchemy_error)
    resp = client.delete(f"/resources/{resource.id}")
    assert resp.status_code == 500
    data = resp.get_json()
    assert "message" in data

