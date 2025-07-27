"""
app.schemas.permission_schema
----------------------------

This module defines the Marshmallow PermissionSchema for the PM Guardian API.
It provides serialization, deserialization, and validation logic for permission
model instances, ensuring data integrity and proper formatting in API requests
and responses.
"""

import uuid
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, validate, post_load, ValidationError
from app.models.permission import Permission, OperationEnum


class PermissionSchema(SQLAlchemyAutoSchema):
    """
    Marshmallow schema for the Permission model.

    Handles serialization and deserialization of Permission model instances,
    including validation of input data for creating or updating permissions,
    and formatting output for API responses. Enforces field constraints and
    manages relationships with foreign keys.

    Attributes:
        Meta (class): Configuration for the schema, including model binding
            and field options.
        id (fields.UUID): Unique identifier for the permission (read-only).
        company_id (fields.String): Company UUID (required, validated).
        operation (fields.String): Operation type (required, enum).
        resource_id (fields.String): Resource UUID (required).
        created_at (fields.DateTime): Creation timestamp (read-only).
        updated_at (fields.DateTime): Update timestamp (read-only).
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the PermissionSchema instance.

        Args:
            *args: Positional arguments for the parent constructor.
            **kwargs: Keyword arguments for the parent constructor.
        """
        self.context = kwargs.pop('context', {})
        super().__init__(*args, **kwargs)

    @post_load
    def convert_uuids_to_str(self, data, **kwargs):
        """
        Convert UUID fields to string format after loading data.

        Args:
            data (dict): The loaded data.
            **kwargs: Additional keyword arguments.

        Returns:
            dict: The data with UUID fields converted to strings.
        """
        _ = kwargs
        if (
            'company_id' in data and isinstance(data['company_id'], uuid.UUID)
        ):
            data['company_id'] = str(data['company_id'])
        if (
            'resource_id' in data and isinstance(data['resource_id'], uuid.UUID)
        ):
            data['resource_id'] = str(data['resource_id'])
        return data

    @staticmethod
    def validate_company_id(value):
        """
        Validate that the company_id is a valid UUID string.

        Args:
            value (str): The company_id value to validate.

        Raises:
            ValidationError: If the value is not a valid UUID string.
        """
        try:
            uuid.UUID(str(value))
        except Exception as exc:
            raise ValidationError(
                "company_id must be a valid UUID string."
            ) from exc

    @staticmethod
    def validate_resource_id(value):
        """
        Validate that the resource_id is a valid UUID string.

        Args:
            value (str): The resource_id value to validate.

        Raises:
            ValidationError: If the value is not a valid UUID string.
        """
        try:
            uuid.UUID(str(value))
        except Exception as exc:
            raise ValidationError(
                "resource_id must be a valid UUID string."
            ) from exc

    class Meta:
        """
        Configuration class for PermissionSchema.

        Specifies schema options such as the model to bind, whether to load
        instances, inclusion of foreign keys, and fields that are read-only
        during serialization.

        Attributes:
            model (Permission): The SQLAlchemy model class to bind the schema.
            load_instance (bool): If True, deserialization returns model
                instances.
            include_fk (bool): If True, includes foreign key fields in the
                schema.
            dump_only (tuple): Fields that are read-only and only included in
                output.
        """
        model = Permission
        load_instance = True
        include_fk = True
        dump_only = ('id', 'created_at', 'updated_at')

    id = fields.UUID(dump_only=True)
    operation = fields.String(
        required=True,
        validate=validate.OneOf([
            e.value for e in OperationEnum
        ])
    )
    resource_id = fields.String(
        required=True,
        validate=validate_resource_id
    )
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
