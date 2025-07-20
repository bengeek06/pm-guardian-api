
"""
app.models.user_role
--------------------

Defines the SQLAlchemy UserRole model for the PM Guardian API.
A UserRole represents the association between a user and a role within a
company, enabling role-based access control. All fields and relationships
are documented for clarity and maintainability.
"""

import uuid
from app.models.db import db


class UserRole(db.Model):
    """
    SQLAlchemy model for user-role associations in the PM Guardian API.

    Represents the assignment of a role to a user within a company.

    Attributes:
        id (str): Unique identifier for the user-role association.
        user_id (str): Unique identifier of the user.
        role_id (str): Unique identifier of the role.
        company_id (str): Unique identifier of the company.
        created_at (datetime): Timestamp when created.
        updated_at (datetime): Timestamp when last modified.
    """
    __tablename__ = 'user_roles'
    __table_args__ = (
        db.UniqueConstraint(
            'user_id', 'role_id', 'company_id',
            name='uq_user_role'
        ),
    )
    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    user_id = db.Column(db.String(36), nullable=False)
    role_id = db.Column(
        db.String(36),
        db.ForeignKey('roles.id'),
        nullable=False
    )
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

    def __repr__(self):
        """
        Return a string representation of the UserRole instance.

        Returns:
            str: A formatted string showing the user-role id for debugging.
        """
        return f"<UserRole {self.id}>"
