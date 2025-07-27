"""
app.models.role_policy
---------------------

This module defines the RolePolicy SQLAlchemy model for the PM Guardian API.
A RolePolicy represents the association between a role and a policy, with
automatic timestamps for creation and modification.
"""

from app.models.db import db


class RolePolicy(db.Model):
    """
    SQLAlchemy model for linking roles and policies.

    Attributes:
        id (str): Unique identifier for the association.
        role_id (str): Foreign key to the role.
        policy_id (str): Foreign key to the policy.
        created_at (datetime): Timestamp when created.
        updated_at (datetime): Timestamp when last modified.
    """

    __tablename__ = "role_policies"
    id = db.Column(db.String, primary_key=True)
    role_id = db.Column(
        db.String, db.ForeignKey("roles.id"), nullable=False
    )
    policy_id = db.Column(
        db.String, db.ForeignKey("policies.id"), nullable=False
    )
    created_at = db.Column(
        db.DateTime, server_default=db.func.current_timestamp()
    )
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )

    def __repr__(self):
        """
        Return a string representation of the RolePolicy instance.

        Returns:
            str: A formatted string showing the role_policy id.
        """
        return f"<RolePolicy {self.id}>"
