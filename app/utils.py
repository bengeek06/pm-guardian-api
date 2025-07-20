"""
app.utils
---------

Utility functions and decorators for the PM Guardian API.
Includes access control decorators using CheckAccessResource logic.
"""

from functools import wraps
from flask import request, jsonify, g
from app.models import (
    UserRole, RolePolicy, PolicyPermission, Permission, OperationEnum, Resource
)
from app.logger import logger


def check_access_required(operation):
    """
    Decorator to check access rights for a given CRUD operation on a resource.

    Args:
        operation (str): The CRUD operation to check (e.g., 'create', 'read', 'update', 'delete').

    Usage:
        @check_access_required('read')
        def get(...):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            resource_name = kwargs.get('resource_name') or request.view_args.get('resource_name')
            user_id = getattr(g, 'user_id', None) or request.headers.get('X-User-Id')
            if not user_id or not resource_name:
                return jsonify({
                    'error': 'Missing user_id or resource_name for access check.'
                }), 400
            # Use CheckAccessResource logic
            access_granted, reason, status = check_access(
                user_id, resource_name, operation
            )
            if access_granted:
                return view_func(*args, **kwargs)
            return jsonify({
                'error': 'Access denied',
                'reason': reason
            }), status if isinstance(status, int) else 403
        return wrapped
    return decorator

def check_access(user_id, resource_name, operation):
    """
    Pure function to check access rights for a given CRUD operation on a resource.

    Args:
        user_id (str): The user identifier.
        resource_name (str): The resource name.
        operation (str): The CRUD operation to check.

    Returns:
        tuple: (access_granted: bool, reason: str, status_code: int)
    """
    try:
        # 1. Find the resource
        resource = Resource.query.filter_by(name=resource_name).first()
        if not resource:
            return False, f"Resource '{resource_name}' not found.", 404
        # 2. Validate the operation
        try:
            op_enum = OperationEnum(operation)
        except ValueError:
            return False, f"Operation '{operation}' is invalid.", 400
        # 3. Get all user roles
        user_roles = UserRole.query.filter_by(user_id=user_id).all()
        if not user_roles:
            return False, "User has no roles assigned.", 403
        role_ids = [ur.role_id for ur in user_roles]
        # 4. Get all policies for these roles
        role_policies = RolePolicy.query.filter(
            RolePolicy.role_id.in_(role_ids)
        ).all()
        if not role_policies:
            return False, "User's roles have no policies assigned.", 403
        policy_ids = [rp.policy_id for rp in role_policies]
        # 5. Get all policy_permissions for these policies
        policy_permissions = PolicyPermission.query.filter(
            PolicyPermission.policy_id.in_(policy_ids)
        ).all()
        if not policy_permissions:
            return False, "Policies have no permissions assigned.", 403
        permission_ids = [pp.permission_id for pp in policy_permissions]
        # 6. Check for a matching permission
        permission = Permission.query.filter(
            Permission.id.in_(permission_ids),
            Permission.resource_id == resource.id,
            Permission.operation == op_enum
        ).first()
        if permission:
            return True, "Access granted by user role and policy.", 200
        return False, "No matching permission found for user roles.", 403
    except Exception as err:
        logger.error(
            "Unexpected error during access check: %s", str(err)
        )
        return False, "An unexpected error occurred.", 500
