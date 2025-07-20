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
from app.resources_list import RESOURCES


class Resource(db.Model):
    """
    SQLAlchemy model for resources in the PM Guardian API.

    Represents a resource entity with a unique identifier, name, description,
    company association, and timestamps for creation and modification.

    Attributes:
        id (str): Unique identifier (UUID) for the resource.
        name (str): Name of the resource (max 50 chars).
        description (str, optional): Description (max 255 chars).
        created_at (datetime): Timestamp when created.
        updated_at (datetime): Timestamp when last modified.
        permissions (list): List of Permission objects linked to this resource.
    """

    __tablename__ = 'resources'

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)
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

def sync_resources():
    """
    Synchronize the Resource table with the canonical RESOURCES list.
    Creates missing resources and deletes those not in the list for the given company.

    """
    # Check if the table exists before syncing
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    if not inspector.has_table(Resource.__tablename__):
        # Table does not exist yet (e.g. before migrations)
        return

    current = Resource.query.all()
    current_names = {r.name for r in current}
    canonical_names = {r["name"] for r in RESOURCES}

    # Add missing resources
    for res in RESOURCES:
        if res["name"] not in current_names:
            db.session.add(Resource(
                name=res["name"],
                description=res.get("description"),
            ))

    # Delete resources not in canonical list
    for r in current:
        if r.name not in canonical_names:
            db.session.delete(r)

    db.session.commit()
