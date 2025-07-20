"""
app.models.resource
------------------

This module defines the SQLAlchemy Resource model for the PM Guardian API.
A Resource represents an entity associated with a company, with unique name,
description, and automatic timestamps. All fields and relationships are
documented for clarity and maintainability.
"""

import uuid
from app.models.db import db


class Resource(db.Model):
    """
    SQLAlchemy model for resources in the PM Guardian API.

    Represents a resource entity with a unique identifier, name, description,
    company association, and timestamps for creation and modification.

    Attributes:
        id (str): Unique identifier (UUID) for the resource.
        name (str): Name of the resource (max 50 chars).
        description (str, optional): Description (max 255 chars).
        company_id (str): Foreign key to the company.
        created_at (datetime): Timestamp when created.
        updated_at (datetime): Timestamp when last modified.
        permissions (list): List of Permission objects linked to this resource.
    """

    __tablename__ = 'resources'
    __table_args__ = (
        db.UniqueConstraint('name', 'company_id',
                            name='uq_resource_name_company'),
    )
    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    name = db.Column(db.String(50), nullable=False)
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
    permissions = db.relationship(
        "Permission", backref="resource", lazy=True,
        doc="List of Permission objects linked to this resource."
    )

    def __repr__(self):
        """
        Return a string representation of the Resource instance.

        Returns:
            str: A formatted string showing the resource name for debugging.
        """
        return f"<Resource {self.name}>"
