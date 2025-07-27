"""
app.models.__init__
-------------------

This module initializes and imports all SQLAlchemy models for the
PM Guardian API. Importing this module ensures all models are registered
with the SQLAlchemy metadata, so that table creation and migrations work
correctly. All models should be imported here.
"""

from .role import Role
from .policy import Policy
from .role_policy import RolePolicy
from .resource import Resource
from .permission import Permission, OperationEnum
from .policy_permission import PolicyPermission
from .user_role import UserRole
