"""
routes.py
-----------
Routes for the Flask application.
# This module is responsible for registering the routes of the REST API
# and linking them to the corresponding resources.
"""
from flask_restful import Api
from app.logger import logger
from app.resources.version import VersionResource
from app.resources.config import ConfigResource
from app.resources.role import RoleListResource, RoleResource
from app.resources.resource import ResourceListResource, ResourceResource
from app.resources.permission import PermissionListResource, PermissionResource
from app.resources.policy import PolicyListResource, PolicyResource
from app.resources.role import RolePoliciesResource
from app.resources.check_access import CheckAccessResource
from app.resources.user_role import UserRoleListResource, UserRoleResource


def register_routes(app):
    """
    Register the REST API routes on the Flask application.

    Args:
        app (Flask): The Flask application instance.

    This function creates a Flask-RESTful Api instance, adds the resource
    endpoints for managing dummy items, and logs the successful registration
    of routes.
    """
    api = Api(app)

    api.add_resource(VersionResource, '/version')
    api.add_resource(ConfigResource, '/config')

    api.add_resource(RoleListResource, '/roles')
    api.add_resource(RoleResource, '/roles/<string:role_id>')
    api.add_resource(RolePoliciesResource, '/roles/<string:role_id>/policies')

    api.add_resource(ResourceListResource, '/resources')
    api.add_resource(ResourceResource, '/resources/<string:resource_id>')

    api.add_resource(PermissionListResource, '/permissions')
    api.add_resource(PermissionResource, '/permissions/<string:permission_id>')

    api.add_resource(PolicyListResource, '/policies')
    api.add_resource(PolicyResource, '/policies/<string:policy_id>')

    api.add_resource(CheckAccessResource, '/check-access')

    api.add_resource(UserRoleListResource, '/user-roles')
    api.add_resource(UserRoleResource, '/user-roles/<string:user_role_id>')

    logger.info("Routes registered successfully.")
