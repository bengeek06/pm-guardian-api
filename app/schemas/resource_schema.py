"""
app.schemas.resource_schema
--------------------------

This module defines the Marshmallow ResourceSchema for the PM Guardian API.
It provides serialization, deserialization, and validation logic for resource
model instances, ensuring data integrity and proper formatting in API requests
and responses.
"""

import uuid
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, validate, ValidationError
from app.models.resource import Resource


class ResourceSchema(SQLAlchemyAutoSchema):
    """
    Marshmallow schema for the Resource model.

    Handles serialization and deserialization of Resource model instances,
    including validation of input data for creating or updating resources,
    and formatting output for API responses. Enforces field constraints and
    manages relationships with foreign keys.

    Attributes:
        Meta (class): Configuration for the schema, including model binding
            and field options.
        id (fields.UUID): Unique identifier for the resource (read-only).
        name (fields.String): Name of the resource (required, max 50 chars).
        description (fields.String): Description (optional, max 255 chars).
        company_id (fields.String): Company UUID (required, validated).
        created_at (fields.DateTime): Creation timestamp (read-only).
        updated_at (fields.DateTime): Update timestamp (read-only).
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the ResourceSchema instance.

        Args:
            *args: Positional arguments for the parent constructor.
            **kwargs: Keyword arguments for the parent constructor.
        """
        self.context = kwargs.pop('context', {})
        super().__init__(*args, **kwargs)

    class Meta:
        """
        Configuration class for ResourceSchema.

        Specifies schema options such as the model to bind, whether to load
        instances, inclusion of foreign keys, and fields that are read-only
        during serialization.

        Attributes:
          model (Resource): The SQLAlchemy model class to bind to the schema.
          load_instance (bool): If True, deserialization returns model instances.
          include_fk (bool): If True, includes foreign key fields in the schema.
          dump_only (tuple): Fields that are read-only and only included in
              output.
        """
        model = Resource
        load_instance = True
        include_fk = True
        dump_only = ('id', 'created_at', 'updated_at')

    id = fields.UUID(
        dump_only=True,
        metadata={
            "description": "Unique identifier for the resource (read-only)."
        }
    )
    name = fields.String(
        required=True,
        validate=validate.Length(max=50),
        metadata={
            "description": "Name of the resource (required, max 50 chars)."
        }
    )
    description = fields.String(
        validate=validate.Length(max=255),
        allow_none=True,
        metadata={
            "description": "Description (optional, max 255 chars)."
        }
    )

    @staticmethod
    def validate_company_id(value):
        """
        Validate that the company_id is a valid UUID string.

        Args:
            value (str): The company_id value to validate.

        Raises:
            ValidationError: If the value is not a valid UUID string.

        Returns:
            None
        """
        try:
            uuid.UUID(str(value))
        except Exception as exc:
            raise ValidationError(
                "company_id must be a valid UUID string."
            ) from exc

    company_id = fields.String(
        required=True,
        validate=validate_company_id,
        metadata={
            "description": "Company UUID (required, validated as UUID)."
        }
    )
    created_at = fields.DateTime(
        dump_only=True,
        metadata={
            "description": "Creation timestamp (read-only)."
        }
    )
    updated_at = fields.DateTime(
        dump_only=True,
        metadata={
            "description": "Update timestamp (read-only)."
        }
    )
