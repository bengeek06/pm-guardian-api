"""
Resource Schema Module.

This module defines the Marshmallow schema for serializing and deserializing
Resource model instances. It provides validation and transformation logic for
handling resource data in API requests and responses, ensuring data integrity
and proper formatting.
"""

import uuid
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, validate, ValidationError

from app.models.resource import Resource

class ResourceSchema(SQLAlchemyAutoSchema):
    """Marshmallow schema for the Resource model.
    This schema handles serialization and deserialization of Resource model instances,
    including validation of input data for creating or updating resources, and formatting
    output for API responses. It enforces field constraints and manages relationships
    with foreign keys.
    Attributes:
        Meta (class): Configuration for the schema, including model binding and field options.
        id (fields.UUID): Unique identifier for the resource (read-only).
        name (fields.String): Name of the resource (required, max 50 chars).
        description (fields.String): Description of the resource (optional, max 255 chars).
        company_id (fields.UUID): Identifier of the company to which the resource belongs (required).
        created_at (fields.DateTime): Timestamp when the resource was created (read-only).
        updated_at (fields.DateTime): Timestamp when the resource was last updated (read-only).
    """
    def __init__(self, *args, **kwargs):
        self.context = kwargs.pop('context', {})
        super().__init__(*args, **kwargs)

    class Meta:
        """
        Configuration class for ResourceSchema.

        Specifies schema options such as the model to bind, whether to load instances,
        inclusion of foreign keys, and fields that are read-only during serialization.

        Attributes:
            model (Role): The SQLAlchemy model class to bind to the schema.
            load_instance (bool): If True, deserialization returns model instances.
            include_fk (bool): If True, includes foreign key fields in the schema.
            dump_only (tuple): Fields that are read-only and only included in output.
        """
        model = Resource
        load_instance = True
        include_fk = True
        dump_only = ('id', 'created_at', 'updated_at')

    id = fields.UUID(dump_only=True)
    name = fields.String(
        required=True,
        validate=validate.Length(max=50)
    )
    description = fields.String(
        validate=validate.Length(max=255),
        allow_none=True
    )
    @staticmethod
    def validate_company_id(value):
        """Validate that the company_id is a valid UUID string."""
        try:
            uuid.UUID(str(value))
        except Exception as exc:
            raise ValidationError("company_id must be a valid UUID string.") from exc

    company_id = fields.String(required=True, validate=validate_company_id)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
