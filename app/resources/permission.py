"""
app.resources.permission
-----------------------

This module defines RESTful resources for managing permissions in the
PM Guardian API. It provides endpoints for creating, listing, retrieving,
updating, and deleting permissions associated with a company and resource.
All endpoints handle input validation, error management, and serialization
of permission data for API responses.
"""

from flask import request, g
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from flask_restful import Resource
from app.models.db import db
from app.logger import logger
from app.schemas.permission_schema import PermissionSchema
from app.models.permission import Permission


class PermissionListResource(Resource):
    """
    Resource for handling permission-related operations.

    Provides endpoints for creating and listing permissions within a company.
    Supports permission creation with validation and handles errors
    appropriately.
    """
    def get(self):
        """
        List all permissions for the authenticated company.

        Returns:
            tuple: JSON response with a list of permissions and HTTP status code.
        """
        logger.info(
            "Fetching permissions for company.",
            path=request.path,
            method=request.method,
            request_id=getattr(g, "request_id", None)
        )
        try:
            permissions = Permission.query.all()
            schema = PermissionSchema(session=db.session, many=True)
            return schema.dump(permissions), 200
        except SQLAlchemyError as err:
            logger.error(
                "Database error while fetching permissions: %s", str(err)
            )
            return {
                "message": "An error occurred while fetching permissions."
            }, 500

    def post(self):
        """
        Create a new permission for the authenticated company.

        Returns:
            tuple: JSON response with the created permission and HTTP status code.
        """
        logger.info(
            "Creating new permission.",
            path=request.path,
            method=request.method,
            request_id=getattr(g, "request_id", None)
        )
        json_data = request.get_json()
        schema = PermissionSchema(session=db.session)
        try:
            new_permission = schema.load(json_data)
            db.session.add(new_permission)
            db.session.commit()
            return schema.dump(new_permission), 201
        except ValidationError as err:
            logger.error(
                "Validation error while creating permission: %s", str(err)
            )
            return {"message": str(err)}, 400
        except IntegrityError as err:
            db.session.rollback()
            logger.error(
                "Integrity error while creating permission: %s", str(err)
            )
            return {"message": "Permission already exists."}, 409
        except SQLAlchemyError as err:
            db.session.rollback()
            logger.error(
                "Database error while creating permission: %s", str(err)
            )
            return {
                "message": "An error occurred while creating the permission."
            }, 500


class PermissionResource(Resource):
    """
    Resource for handling operations on a specific permission.

    Provides endpoints for retrieving, updating, and deleting a permission by
    its ID. Supports permission retrieval with validation and handles errors
    appropriately.
    """
    def get(self, permission_id):
        """
        Retrieve a permission by its ID.

        Args:
            permission_id (str): The unique identifier of the permission.

        Returns:
            tuple: JSON response with the permission data and HTTP status code.
        """
        logger.info(
            "Fetching permission by ID.",
            path=request.path,
            method=request.method,
            request_id=getattr(g, "request_id", None)
        )
        try:
            permission = db.session.get(Permission, permission_id)
            if not permission:
                return {"message": "Permission not found."}, 404
            schema = PermissionSchema(session=db.session)
            return schema.dump(permission), 200
        except SQLAlchemyError as err:
            logger.error(
                "Database error while fetching permission: %s", str(err)
            )
            return {
                "message": "An error occurred while fetching the permission."
            }, 500

    def put(self, permission_id):
        """
        Update a permission by its ID.

        Args:
            permission_id (str): The unique identifier of the permission.

        Returns:
            tuple: JSON response with the updated permission data and HTTP status code.
        """
        schema = PermissionSchema(session=db.session)
        try:
            permission = db.session.get(Permission, permission_id)
            if not permission:
                return {"message": "Permission not found."}, 404
            permission = schema.load(request.json, instance=permission)
            db.session.commit()
            return schema.dump(permission), 200
        except ValidationError as err:
            logger.error(
                "Validation error while updating permission: %s", str(err)
            )
            return {"message": str(err)}, 400
        except SQLAlchemyError as err:
            logger.error(
                "Database error while updating permission: %s", str(err)
            )
            return {
                "message": "An error occurred while updating the permission."
            }, 500

    def patch(self, permission_id):
        """
        Partially update a permission by its ID.

        Args:
            permission_id (str): The unique identifier of the permission.

        Returns:
            tuple: JSON response with the updated permission data and HTTP status code.
        """
        schema = PermissionSchema(session=db.session, partial=True)
        try:
            permission = db.session.get(Permission, permission_id)
            if not permission:
                return {"message": "Permission not found."}, 404
            permission = schema.load(request.json, instance=permission)
            db.session.commit()
            return schema.dump(permission), 200
        except ValidationError as err:
            logger.error(
                "Validation error while partially updating permission: %s", str(err)
            )
            return {"message": str(err)}, 400
        except SQLAlchemyError as err:
            logger.error(
                "Database error while partially updating permission: %s", str(err)
            )
            return {
                "message": "An error occurred while partially updating the permission."
            }, 500

    def delete(self, permission_id):
        """
        Delete a permission by its ID.

        Args:
            permission_id (str): The unique identifier of the permission.

        Returns:
            tuple: JSON response with a success message and HTTP status code 204.
        """
        logger.info(
            "Deleting permission by ID.",
            path=request.path,
            method=request.method,
            request_id=getattr(g, "request_id", None)
        )
        try:
            permission = db.session.get(Permission, permission_id)
            if not permission:
                return {
                    "message": "Permission not found."
                }, 404
            db.session.delete(permission)
            db.session.commit()
            return {
                "message": "Permission deleted successfully."
            }, 204
        except SQLAlchemyError as err:
            logger.error(
                "Database error while deleting permission: %s",
                str(err)
            )
            return {
                "message": (
                    "An error occurred while deleting the permission."
                )
            }, 500
        except Exception as err:
            logger.error(
                "Unexpected error while deleting permission: %s",
                str(err)
            )
            return {
                "message": "An unexpected error occurred."
            }, 500
