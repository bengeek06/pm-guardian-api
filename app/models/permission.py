
"""
app.models.permission
---------------------

Defines the SQLAlchemy Permission model and the OperationEnum for the
PM Guardian API. The Permission model represents a permission entity
associated with a company, a resource, and an operation (create, read,
update, delete). All fields, relationships, and methods are documented
for clarity and maintainability.
"""

import uuid
import enum
from app.models.db import db


class OperationEnum(enum.Enum):
    """
    Enum for allowed operation types for permissions.

    Values:
        CREATE: Create operation
        READ: Read operation
        UPDATE: Update operation
        DELETE: Delete operation
    """
    CREATE = 'create'
    READ = 'read'
    UPDATE = 'update'
    DELETE = 'delete'


class Permission(db.Model):
    """
    SQLAlchemy model for permissions in the PM Guardian API.

    Represents a permission entity with a unique identifier, company
    association, operation type, and resource linkage. Includes automatic
    timestamps for creation and modification.

    Attributes:
        id (str): Unique identifier (UUID) for the permission.
        company_id (str): Foreign key linking the permission to a company.
        operation (OperationEnum): Allowed operation type.
        resource_id (str): Foreign key to the resource.
        created_at (datetime): Timestamp when created.
        updated_at (datetime): Timestamp when last modified.
    """
    __tablename__ = 'permissions'
    __table_args__ = (
        db.UniqueConstraint(
            'company_id', 'resource_id', 'operation',
            name='uq_permission_company_resource_operation'
        ),
    )
    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    company_id = db.Column(db.String(36), nullable=False)
    operation = db.Column(
        db.Enum(
            OperationEnum,
            values_callable=lambda x: [e.value for e in x]
        ),
        nullable=False
    )
    resource_id = db.Column(
        db.String(36),
        db.ForeignKey('resources.id'),
        nullable=False
    )
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
        Return a string representation of the Permission instance.

        Returns:
            str: A formatted string showing the permission id for debugging.
        """
        return f"<Permission {self.id}>"
