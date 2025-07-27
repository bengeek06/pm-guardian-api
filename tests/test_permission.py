"""
Permission API Endpoint Tests

This test module provides exhaustive tests for the /permissions API endpoints, including:
    - GET /permissions: List permissions for a company
    - POST /permissions: Create a new permission
    - GET /permissions/<permission_id>: Retrieve a specific permission by ID
    - PUT /permissions/<permission_id>: Update a permission
    - PATCH /permissions/<permission_id>: Partially update a permission
    - DELETE /permissions/<permission_id>: Delete a permission

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
    - create_permission: Utility to insert a permission into the test database
"""
import uuid
from sqlalchemy.exc import SQLAlchemyError
from app.models.permission import Permission, OperationEnum

def create_permission(session, resource_id, operation=OperationEnum.READ.value):
    """Helper function to create a permission in the database."""
    permission = Permission(
        resource_id=resource_id,
        operation=OperationEnum(operation)
    )
    session.add(permission)
    session.commit()
    return permission

############################################################
# GET /permissions
############################################################
def test_get_permissions_success(client, session, resource):
    res = resource()
    create_permission(session, res.id, OperationEnum.READ.value)
    create_permission(session, res.id, OperationEnum.UPDATE.value)
    resp = client.get(f"/permissions")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) == 2
    ops = [p["operation"] for p in data]
    ops = [str(op).lower().replace('operationenum.', '') for op in ops]
    assert set(ops) == {OperationEnum.READ.value, OperationEnum.UPDATE.value}

def test_get_permissions_empty(client, session, resource):
    resource()  # crée une resource mais pas de permission
    resp = client.get(f"/permissions")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data == []

def test_get_permissions_missing_company_id(client):
    resp = client.get("/permissions")
    assert resp.status_code == 200
    assert resp.get_json() == []

def test_get_permissions_invalid_company_id_format(client, resource):
    resource()
    resp = client.get("/permissions?company_id=not-a-uuid")
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)

############################################################
# POST /permissions
############################################################
def test_post_permissions_success(client, resource):
    res = resource()
    payload = {"resource_id": res.id, "operation": OperationEnum.READ.value}
    resp = client.post("/permissions", json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["resource_id"] == res.id
    op = data["operation"]
    op = str(op).lower().replace('operationenum.', '')
    assert op == OperationEnum.READ.value

def test_post_permissions_missing_company_id(client, resource):
    res = resource()
    payload = {"resource_id": res.id, "operation": OperationEnum.READ.value}
    resp = client.post("/permissions", json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["resource_id"] == res.id

def test_post_permissions_missing_resource_id(client, resource):
    resource()
    payload = {"operation": OperationEnum.READ.value}
    resp = client.post("/permissions", json=payload)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "resource_id" in str(data).lower() or "message" in data

def test_post_permissions_missing_operation(client, resource):
    res = resource()
    payload = {"resource_id": res.id}
    resp = client.post("/permissions", json=payload)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "operation" in str(data).lower() or "message" in data

def test_post_permissions_duplicate(client, session, resource):
    res = resource()
    create_permission(session, res.id, OperationEnum.READ.value)
    payload = {"resource_id": res.id, "operation": OperationEnum.READ.value}
    resp = client.post("/permissions", json=payload)
    assert resp.status_code == 409
    data = resp.get_json()
    assert "message" in data

def test_post_permissions_db_error(client, resource, monkeypatch):
    def raise_sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("DB error")
    res = resource()
    monkeypatch.setattr("app.models.db.db.session.commit", raise_sqlalchemy_error)
    payload = {"resource_id": res.id, "operation": OperationEnum.READ.value}
    resp = client.post("/permissions", json=payload)
    assert resp.status_code == 500
    data = resp.get_json()
    assert "message" in data

############################################################
# GET /permissions/<permission_id>
############################################################
def test_get_permission_by_id_success(client, session, resource):
    res = resource()
    perm = create_permission(session, res.id, OperationEnum.READ.value)
    resp = client.get(f"/permissions/{perm.id}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == str(perm.id)
    assert data["resource_id"] == res.id

def test_get_permission_by_id_not_found(client):
    non_existent_id = str(uuid.uuid4())
    resp = client.get(f"/permissions/{non_existent_id}")
    assert resp.status_code == 404
    data = resp.get_json()
    assert "not found" in str(data).lower() or "message" in data

def test_get_permission_by_id_invalid_format(client):
    resp = client.get("/permissions/not-a-uuid")
    assert resp.status_code in (404, 500)
    data = resp.get_json()
    assert "message" in data

############################################################
# PUT /permissions/<permission_id>
############################################################
def test_put_permission_success(client, session, resource):
    res = resource()
    perm = create_permission(session, res.id, OperationEnum.READ.value)
    payload = {"resource_id": res.id, "operation": OperationEnum.UPDATE.value}
    resp = client.put(f"/permissions/{perm.id}", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == str(perm.id)
    op = data["operation"]
    op = str(op).lower().replace('operationenum.', '')
    assert op == OperationEnum.UPDATE.value

def test_put_permission_not_found(client):
    non_existent_id = str(uuid.uuid4())
    payload = {"resource_id": str(uuid.uuid4()), "operation": OperationEnum.READ.value}
    resp = client.put(f"/permissions/{non_existent_id}", json=payload)
    assert resp.status_code == 404
    data = resp.get_json()
    assert "not found" in str(data).lower() or "message" in data

def test_put_permission_invalid_data(client, session, resource):
    res = resource()
    perm = create_permission(session, res.id, OperationEnum.READ.value)
    payload = {"resource_id": res.id}
    resp = client.put(f"/permissions/{perm.id}", json=payload)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "operation" in str(data).lower() or "message" in data

def test_put_permission_db_error(client, session, resource, monkeypatch):
    res = resource()
    perm = create_permission(session, res.id, OperationEnum.READ.value)
    def raise_sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("DB error")
    monkeypatch.setattr("app.models.db.db.session.commit", raise_sqlalchemy_error)
    payload = {"resource_id": res.id, "operation": OperationEnum.UPDATE.value}
    resp = client.put(f"/permissions/{perm.id}", json=payload)
    assert resp.status_code == 500
    data = resp.get_json()
    assert "message" in data

############################################################
# PATCH /permissions/<permission_id>
############################################################
def test_patch_permission_success(client, session, resource):
    res = resource()
    perm = create_permission(session, res.id, OperationEnum.READ.value)
    payload = {"operation": OperationEnum.DELETE.value}
    resp = client.patch(f"/permissions/{perm.id}", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == str(perm.id)
    op = data["operation"]
    op = str(op).lower().replace('operationenum.', '')
    assert op == OperationEnum.DELETE.value

def test_patch_permission_not_found(client):
    non_existent_id = str(uuid.uuid4())
    payload = {"operation": OperationEnum.DELETE.value}
    resp = client.patch(f"/permissions/{non_existent_id}", json=payload)
    assert resp.status_code == 404
    data = resp.get_json()
    assert "not found" in str(data).lower() or "message" in data

def test_patch_permission_invalid_data(client, session, resource):
    res = resource()
    perm = create_permission(session, res.id, OperationEnum.READ.value)
    payload = {"operation": "not-an-op"}
    resp = client.patch(f"/permissions/{perm.id}", json=payload)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "operation" in str(data).lower() or "message" in data

def test_patch_permission_db_error(client, session, resource, monkeypatch):
    res = resource()
    perm = create_permission(session, res.id, OperationEnum.READ.value)
    def raise_sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("DB error")
    monkeypatch.setattr("app.models.db.db.session.commit", raise_sqlalchemy_error)
    payload = {"operation": OperationEnum.UPDATE.value}
    resp = client.patch(f"/permissions/{perm.id}", json=payload)
    assert resp.status_code == 500
    data = resp.get_json()
    assert "message" in data

############################################################
# DELETE /permissions/<permission_id>
############################################################
def test_delete_permission_success(client, session, resource):
    res = resource()
    perm = create_permission(session, res.id, OperationEnum.READ.value)
    resp = client.delete(f"/permissions/{perm.id}")
    assert resp.status_code == 204
    # Optionally, check that the permission is actually deleted
    get_resp = client.get(f"/permissions/{perm.id}")
    assert get_resp.status_code == 404

def test_delete_permission_not_found(client):
    non_existent_id = str(uuid.uuid4())
    resp = client.delete(f"/permissions/{non_existent_id}")
    assert resp.status_code == 404
    data = resp.get_json()
    assert "not found" in str(data).lower() or "message" in data

def test_delete_permission_db_error(client, session, resource, monkeypatch):
    res = resource()
    perm = create_permission(session, res.id, OperationEnum.READ.value)
    def raise_sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("DB error")
    monkeypatch.setattr("app.models.db.db.session.commit", raise_sqlalchemy_error)
    resp = client.delete(f"/permissions/{perm.id}")
    assert resp.status_code == 500
    data = resp.get_json()
    assert "message" in data
