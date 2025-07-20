"""
app.models.role
---------------

This module defines the Role SQLAlchemy model for the PM Guardian API.
A Role represents a user role within a company context, supporting
multi-tenancy and RBAC. All fields and relationships are documented for
clarity and maintainability.
"""

import uuid
from app.models.db import db


class Role(db.Model):
    """
    SQLAlchemy model for roles in the PM Guardian API.

    Represents a user role within a company, with unique name, description,
    company association, and timestamps for creation and modification.

    Attributes:
        id (str): Unique identifier (UUID) for the role.
        name (str): Name of the role (max 50 chars, unique per company).
        description (str, optional): Description (max 255 chars).
        company_id (str): Foreign key to the company.
        created_at (datetime): Timestamp when created.
        updated_at (datetime): Timestamp when last modified.
        role_policies (list): List of RolePolicy objects linked to this role.
    """
    __tablename__ = 'roles'
    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)
    company_id = db.Column(db.String(36), nullable=False)
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )
    role_policies = db.relationship(
        "RolePolicy", backref="role", lazy=True,
        doc="List of RolePolicy objects linked to this role."
    )

    def __repr__(self):
        """
        Return a string representation of the Role instance.

        Returns:
            str: A formatted string showing the role name for debugging.
        """
        return f"<Role {self.name}>"
