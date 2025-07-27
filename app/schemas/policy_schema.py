
"""
app.schemas.policy_schema
------------------------

Defines the Marshmallow PolicySchema for the PM Guardian API.
Provides serialization, deserialization, and validation logic for policy
model instances, ensuring data integrity and proper formatting in API
requests and responses.
"""

import uuid
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, post_load, validate
from app.models.policy import Policy


class PolicySchema(SQLAlchemyAutoSchema):
    """
    Marshmallow schema for the Policy model.

    Handles serialization and deserialization of Policy model instances,
    including validation of input data for creating or updating policies,
    and formatting output for API responses. Enforces field constraints and
    manages relationships with foreign keys.

    Attributes:
        Meta (class): Configuration for the schema, including model binding
            and field options.
        id (fields.String): Unique identifier for the policy (read-only).
        name (fields.String): Name of the policy (required).
        created_at (fields.DateTime): Creation timestamp (read-only).
        updated_at (fields.DateTime): Update timestamp (read-only).
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the PolicySchema instance.

        Args:
            *args: Positional arguments for the parent constructor.
            **kwargs: Keyword arguments for the parent constructor.
        """
        self.context = kwargs.pop('context', {})
        super().__init__(*args, **kwargs)

    @post_load
    def ensure_id(self, data, **kwargs):
        """
        Generate a UUID on the backend if missing when creating a Policy.

        Args:
            data (dict or object): The data to process after loading.
            **kwargs: Additional keyword arguments.

        Returns:
            dict or object: The processed data with a generated UUID if needed.
        """
        _ = kwargs
        if hasattr(data, 'id'):
            if not getattr(data, 'id', None):
                data.id = str(uuid.uuid4())
        else:
            # data may be a dict if load_instance=False
            data['id'] = str(uuid.uuid4())
        return data

    class Meta:
        """
        Configuration class for PolicySchema.

        Specifies schema options such as the model to bind, whether to load
        instances, inclusion of foreign keys, and fields that are read-only
        during serialization.

        Attributes:
            model (Policy): The SQLAlchemy model class to bind to the schema.
            load_instance (bool): If True, deserialization returns model
                instances.
            include_fk (bool): If True, includes foreign key fields in the
                schema.
            dump_only (tuple): Fields that are read-only and only included in
                output.
        """
        model = Policy
        load_instance = True
        include_fk = True
        dump_only = ('id', 'created_at', 'updated_at')

    id = fields.String(
        dump_only=True
    )
    name = fields.String(
        required=True,
        validate=validate.Length(min=1)
    )
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
