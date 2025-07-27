
"""
app.resources.check_access
-------------------------

This module defines the RESTful resource for checking if a user has access
to perform an action on a resource. It provides the POST /check-access endpoint
as specified in the OpenAPI schema.
"""

from flask import request, g
from flask_restful import Resource as ApiResource
from app.models import (
    UserRole, RolePolicy, PolicyPermission, Permission, OperationEnum,
    Resource
)
from app.logger import logger


class CheckAccessResource(ApiResource):
    """
    Resource for checking if a user has access to perform an action.

    Provides an endpoint to check access rights for a user on a resource
    and operation, returning a boolean and an explanation.
    """

    def post(self):
        """
        Check if a user has access to perform an operation on a resource.

        Expects a JSON body with user_id, resource, and operation.

        Returns:
            tuple: JSON response with access_granted and reason, and status
            code.
        """
        logger.info(
            "Checking access.",
            path=request.path,
            method=request.method,
            request_id=getattr(g, "request_id", None)
        )
        json_data = request.get_json()
        user_id = json_data.get("user_id")
        resource_name = json_data.get("resource")
        operation = json_data.get("operation")
        if not user_id or not resource_name or not operation:
            return {
                "error": "Missing user_id, resource, or operation."
            }, 400
        try:
            # 1. Find the resource
            resource = Resource.query.filter_by(name=resource_name).first()
            if not resource:
                return {
                    "access_granted": False,
                    "reason": (
                        f"Resource '{resource_name}' not found."
                    )
                }, 404
            # 2. Validate the operation
            try:
                op_enum = OperationEnum(operation)
            except ValueError:
                return {
                    "access_granted": False,
                    "reason": (
                        f"Operation '{operation}' is invalid."
                    )
                }, 400
            # 3. Get all user roles
            user_roles = UserRole.query.filter_by(user_id=user_id).all()
            if not user_roles:
                return {
                    "access_granted": False,
                    "reason": "User has no roles assigned."
                }, 403
            role_ids = [ur.role_id for ur in user_roles]
            # 4. Get all policies for these roles
            role_policies = RolePolicy.query.filter(
                RolePolicy.role_id.in_(role_ids)
            ).all()
            if not role_policies:
                return {
                    "access_granted": False,
                    "reason": (
                        "User's roles have no policies assigned."
                    )
                }, 403
            policy_ids = [rp.policy_id for rp in role_policies]
            # 5. Get all policy_permissions for these policies
            policy_permissions = PolicyPermission.query.filter(
                PolicyPermission.policy_id.in_(policy_ids)
            ).all()
            if not policy_permissions:
                return {
                    "access_granted": False,
                    "reason": (
                        "Policies have no permissions assigned."
                    )
                }, 403
            permission_ids = [pp.permission_id for pp in policy_permissions]
            # 6. Check for a matching permission
            permission = Permission.query.filter(
                Permission.id.in_(permission_ids),
                Permission.resource_id == resource.id,
                Permission.operation == op_enum
            ).first()
            if permission:
                return {
                    "access_granted": True,
                    "reason": (
                        "Access granted by user role and policy."
                    )
                }, 200
            return {
                "access_granted": False,
                "reason": (
                    "No matching permission found for user roles."
                )
            }, 403
        except Exception as err:
            logger.error(
                "Unexpected error during access check: %s", str(err)
            )
            return {
                "error": "An unexpected error occurred."
            }, 500
