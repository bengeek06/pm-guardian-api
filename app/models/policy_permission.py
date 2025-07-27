"""
app.models.policy_permission
---------------------------

This module defines the PolicyPermission SQLAlchemy model for the
PM Guardian API. It represents the association between a policy and a
permission, with automatic timestamps for creation and modification.
"""

from app.models.db import db


class PolicyPermission(db.Model):
    """
    SQLAlchemy model for linking policies and permissions.

    Attributes:
        id (str): Unique identifier for the association.
        policy_id (str): Foreign key to the policy.
        permission_id (str): Foreign key to the permission.
        created_at (datetime): Timestamp when created.
        updated_at (datetime): Timestamp when last modified.
    """

    __tablename__ = "policy_permissions"
    id = db.Column(db.String, primary_key=True)
    policy_id = db.Column(
        db.String, db.ForeignKey("policies.id"), nullable=False
    )
    permission_id = db.Column(
        db.String, db.ForeignKey("permissions.id"), nullable=False
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
        Return a string representation of the PolicyPermission instance.

        Returns:
            str: A formatted string showing the policy_permission id.
        """
        return f"<PolicyPermission {self.id}>"
