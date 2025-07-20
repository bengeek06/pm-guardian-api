"""
app.models.policy
----------------

This module defines the Policy SQLAlchemy model for the PM Guardian API.
A Policy represents a set of permissions and is linked to roles via
associations. All fields and relationships are documented for clarity.
"""

from app.models.db import db


class Policy(db.Model):
    """
    SQLAlchemy model for policies in the PM Guardian API.

    Attributes:
        id (str): Unique identifier for the policy.
        name (str): Name of the policy.
        created_at (datetime): Timestamp when created.
        updated_at (datetime): Timestamp when last modified.
        policy_permissions (list): List of PolicyPermission associations.
        role_policies (list): List of RolePolicy associations.
    """
    __tablename__ = "policies"
    __table_args__ = (
        db.UniqueConstraint('name', name='uq_policy_name'),
    )
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    created_at = db.Column(
        db.DateTime, server_default=db.func.current_timestamp()
    )
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )

    policy_permissions = db.relationship(
        "PolicyPermission", backref="policy", lazy=True
    )
    role_policies = db.relationship(
        "RolePolicy", backref="policy", lazy=True
    )

    def __repr__(self):
        """
        Return a string representation of the Policy instance.

        Returns:
            str: A formatted string showing the policy id for debugging.
        """
        return f"<Policy {self.id}>"
