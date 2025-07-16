"""
Role Model Module.

This module contains the Role model for implementing Role-Based Access Control (RBAC)
in the PM Guardian API. It provides functionality to manage user roles within companies,
including creation, retrieval, and validation of roles.

The Role model supports multi-tenancy through company_id and includes standard
CRUD operations with proper error handling and logging.
"""
import uuid
from sqlalchemy.exc import SQLAlchemyError
from app.models import db
from app.logger import logger

class Role(db.Model):
    """
    Role model for Role-Based Access Control (RBAC).
    
    This model represents user roles within a company context, providing
    the foundation for implementing role-based permissions and access control.
    Each role is unique within a company and includes metadata for tracking
    creation and modification times.
    
    Attributes:
        id (str): Unique identifier (UUID) for the role.
        name (str): Human-readable name of the role (max 50 chars, unique per company).
        description (str, optional): Detailed description of the role (max 255 chars).
        company_id (str): Foreign key linking the role to a specific company.
        created_at (datetime): Timestamp when the role was created.
        updated_at (datetime): Timestamp when the role was last modified.
    
    Note:
        The name field has a unique constraint, ensuring no duplicate role names
        within the same company. The UUID primary key ensures global uniqueness.
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

    def __repr__(self):
        """
        Return a string representation of the Role instance.
        
        Returns:
            str: A formatted string showing the role name for debugging purposes.
        """
        return f"<Role {self.name}>"

    @classmethod
    def get_all_roles(cls, company_id):
        """
        Retrieve all roles for a specific company.
        
        This method fetches all role records associated with the given company ID,
        providing a complete list of available roles within the company context.
        
        Args:
            company_id (str): The unique identifier of the company whose roles
                            should be retrieved.
        
        Returns:
            list[Role]: A list of Role instances belonging to the specified company.
                       Returns an empty list if no roles are found or if an error occurs.
        
        Raises:
            SQLAlchemyError: Database-related errors are caught and logged,
                           but not re-raised to maintain API stability.
        
        Example:
            >>> roles = Role.get_all_roles("company-uuid-123")
            >>> print(f"Found {len(roles)} roles")
        """
        try:
            return cls.query.filter_by(company_id=company_id).all()
        except SQLAlchemyError as e:
            logger.error("Error retrieving roles: %s", str(e))
            return []

    @classmethod
    def get_role_by_id(cls, role_id):
        """
        Retrieve a role by its unique identifier.
        
        This method performs a direct lookup of a role using its primary key,
        providing fast access to role information when the ID is known.
        
        Args:
            role_id (str): The unique identifier (UUID) of the role to retrieve.
        
        Returns:
            Role | None: The Role instance if found, None if the role doesn't exist
                         or if a database error occurs.
        
        Raises:
            SQLAlchemyError: Database-related errors are caught and logged,
                           but not re-raised to maintain API stability.
        
        Example:
            >>> role = Role.get_role_by_id("role-uuid-456")
            >>> if role:
            ...     print(f"Found role: {role.name}")
            ... else:
            ...     print("Role not found")
        """
        try:
            return cls.query.get(role_id)
        except SQLAlchemyError as e:
            logger.error("Error retrieving role by ID %s: %s", role_id, str(e))
            return None

    @classmethod
    def get_role_by_name(cls, name, company_id):
        """
        Retrieve a role by its name within a specific company context.
        
        This method performs a compound lookup using both the role name and company ID,
        ensuring that role names are unique within each company while allowing
        the same role name to exist across different companies.
        
        Args:
            name (str): The name of the role to search for (case-sensitive).
            company_id (str): The unique identifier of the company to search within.
        
        Returns:
            Role | None: The first Role instance matching the name and company,
                         or None if no match is found or if a database error occurs.
        
        Raises:
            SQLAlchemyError: Database-related errors are caught and logged,
                           but not re-raised to maintain API stability.
        
        Example:
            >>> role = Role.get_role_by_name("admin", "company-uuid-123")
            >>> if role:
            ...     print(f"Admin role ID: {role.id}")
            ... else:
            ...     print("Admin role not found for this company")
        
        Note:
            This method returns the first match found. Given the unique constraint
            on (name, company_id), there should only be one match per company.
        """
        try:
            return cls.query.filter_by(name=name, company_id=company_id).first()
        except SQLAlchemyError as e:
            logger.error("Error retrieving role by name %s: %s", name, str(e))
            return None
