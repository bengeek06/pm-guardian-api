"""
Resource Model Module

This module defines the SQLAlchemy model for resources within the PM Guardian API.
It provides the `Resource` class, which represents a resource entity associated with a company.
The model includes fields for unique identification, name, description, company association,
and automatic timestamps for creation and modification. Class methods are provided for
retrieving resources by company or by ID, with robust error handling and logging.

Classes:
    Resource: SQLAlchemy model for application resources, with query helpers.

Usage:
    Import and use the `Resource` class to interact with the resources table in the database.
    Example:
        resources = Resource.get_all_resources(company_id)
        resource = Resource.get_resource_by_id(resource_id)
"""
import uuid
from sqlalchemy.exc import SQLAlchemyError
from app.models import db
from app.logger import logger

class Resource(db.Model):
    """
    Resource model for managing resources in the application.

    This model represents a resource with a unique identifier, name, description,
    and associated company. It includes metadata for tracking creation and modification times.

    Attributes:
        id (str): Unique identifier (UUID) for the resource.
        name (str): Name of the resource (max 50 chars).
        description (str, optional): Description of the resource (max 255 chars).
        company_id (str): Foreign key linking the resource to a specific company.
        created_at (datetime): Timestamp when the resource was created.
        updated_at (datetime): Timestamp when the resource was last modified.
    """


    __tablename__ = 'resources'
    __table_args__ = (
        db.UniqueConstraint('name', 'company_id', name='uq_resource_name_company'),
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

    def __repr__(self):
        """Return a string representation of the Resource instance."""
        return f"<Resource {self.name}>"

    @classmethod
    def get_all_resources(cls, company_id):
        """
        Retrieve all resources for a given company.

        Args:
            company_id (str): The ID of the company to filter resources by.
        Returns:
            list: A list of Resource instances associated with the company.
        """
        try:
            return cls.query.filter_by(company_id=company_id).all()
        except SQLAlchemyError as e:
            logger.error("Database error while fetching resources: %s", str(e))
            raise
        except Exception as e:
            logger.error("Unexpected error while fetching resources: %s", str(e))
            raise

    @classmethod
    def get_resource_by_id(cls, resource_id):
        """
        Retrieve a resource by its ID.

        Args:
            resource_id (str): The unique identifier of the resource.
        Returns:
            Resource: The Resource instance if found, None otherwise.
        """
        try:
            return cls.query.get(resource_id)
        except SQLAlchemyError as e:
            logger.error("Database error while fetching resource: %s", str(e))
            raise
        except Exception as e:
            logger.error("Unexpected error while fetching resource: %s", str(e))
            raise
