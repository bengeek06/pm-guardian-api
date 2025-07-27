"""
app.schemas.role_schema
----------------------

This module defines the Marshmallow RoleSchema for the PM Guardian API.
It provides serialization, deserialization, and validation logic for role
model instances, ensuring data integrity and proper formatting in API
requests and responses.
"""

import uuid
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, validate, post_load
from app.models.role import Role


class RoleSchema(SQLAlchemyAutoSchema):
    """
    Marshmallow schema for the Role model.

    Handles serialization and deserialization of Role model instances,
    including validation of input data for creating or updating roles,
    and formatting output for API responses. Enforces field constraints
    and manages relationships with foreign keys.

    Attributes:
        Meta (class): Configuration for the schema, including model binding
            and field options.
        id (fields.UUID): Unique identifier for the role (read-only).
        name (fields.String): Name of the role (required, max 50 chars).
        description (fields.String): Description (optional, max 255 chars).
        company_id (fields.UUID): Company UUID (optionnel, None pour superadmin).
        created_at (fields.DateTime): Creation timestamp (read-only).
        updated_at (fields.DateTime): Update timestamp (read-only).
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the RoleSchema instance.

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
        if 'company_id' in data and isinstance(data['company_id'], uuid.UUID):
            data['company_id'] = str(data['company_id'])
        return data

    class Meta:
        """
        Configuration class for RoleSchema.

        Specifies schema options such as the model to bind, whether to load
        instances, inclusion of foreign keys, and fields that are read-only
        during serialization.

        Attributes:
            model (Role): The SQLAlchemy model class to bind to the schema.
            load_instance (bool): If True, deserialization returns model
                instances.
            include_fk (bool): If True, includes foreign key fields in the
                schema.
            dump_only (tuple): Fields that are read-only and only included in
                output.
        """
        model = Role
        load_instance = True
        include_fk = True
        dump_only = ('id', 'created_at', 'updated_at')

    id = fields.UUID(dump_only=True)
    name = fields.String(
        required=True,
        validate=validate.Length(max=50)
    )
    description = fields.String(
        allow_none=True,
        validate=validate.Length(max=255)
    )
    company_id = fields.UUID(required=False, allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
