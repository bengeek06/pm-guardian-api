"""
app.schemas.role_policy_schema
-----------------------------

This module defines the Marshmallow RolePolicySchema for the PM Guardian API.
It provides serialization, deserialization, and validation logic for
role-policy association model instances, ensuring data integrity and proper
formatting in API requests and responses.
"""

import uuid
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, post_load, ValidationError
from app.models.role_policy import RolePolicy


class RolePolicySchema(SQLAlchemyAutoSchema):
    """
    Marshmallow schema for the RolePolicy model.

    Handles serialization and deserialization of RolePolicy model instances,
    including validation of input data for creating or updating associations,
    and formatting output for API responses. Enforces field constraints and
    manages relationships with foreign keys.

    Attributes:
        Meta (class): Configuration for the schema, including model binding
            and field options.
        id (fields.String): Unique identifier for the association (read-only).
        role_id (fields.String): Role UUID (required, validated).
        policy_id (fields.String): Policy UUID (required, validated).
        created_at (fields.DateTime): Creation timestamp (read-only).
        updated_at (fields.DateTime): Update timestamp (read-only).
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the RolePolicySchema instance.

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
        if 'role_id' in data and isinstance(data['role_id'], uuid.UUID):
            data['role_id'] = str(data['role_id'])
        if 'policy_id' in data and isinstance(data['policy_id'], uuid.UUID):
            data['policy_id'] = str(data['policy_id'])
        return data

    @staticmethod
    def validate_role_id(value):
        """
        Validate that the role_id is a valid UUID string.

        Args:
            value (str): The role_id value to validate.

        Raises:
            ValidationError: If the value is not a valid UUID string.
        """
        try:
            uuid.UUID(str(value))
        except Exception as exc:
            raise ValidationError(
                "role_id must be a valid UUID string."
            ) from exc

    @staticmethod
    def validate_policy_id(value):
        """
        Validate that the policy_id is a valid UUID string.

        Args:
            value (str): The policy_id value to validate.

        Raises:
            ValidationError: If the value is not a valid UUID string.
        """
        try:
            uuid.UUID(str(value))
        except Exception as exc:
            raise ValidationError(
                "policy_id must be a valid UUID string."
            ) from exc

    class Meta:
        """
        Configuration class for RolePolicySchema.

        Specifies schema options such as the model to bind, whether to load
        instances, inclusion of foreign keys, and fields that are read-only
        during serialization.

        Attributes:
            model (RolePolicy): The SQLAlchemy model class to bind to the
                schema.
            load_instance (bool): If True, deserialization returns model
                instances.
            include_fk (bool): If True, includes foreign key fields in the
                schema.
            dump_only (tuple): Fields that are read-only and only included in
                output.
        """
        model = RolePolicy
        load_instance = True
        include_fk = True
        dump_only = ('id', 'created_at', 'updated_at')

    id = fields.String(dump_only=True)
    role_id = fields.String(
        required=True,
        validate=validate_role_id
    )
    policy_id = fields.String(
        required=True,
        validate=validate_policy_id
    )
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
