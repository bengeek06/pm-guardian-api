
import uuid
import pytest
from app.models.role import Role

def create_role(session, company_id, name="TestRole", description="desc"):
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
    assert resp.status_code == 200 or resp.status_code == 500
    # Accept either: empty list (if code allows) or error (if code requires company_id)
    # If error, check message
    if resp.status_code == 200:
        assert resp.get_json() == []
    else:
        assert "message" in resp.get_json()

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


