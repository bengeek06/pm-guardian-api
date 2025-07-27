"""
app.resources.user_role
----------------------

This module defines RESTful resources for managing user-role associations
in the PM Guardian API. It provides endpoints for creating, listing,
retrieving, updating, and deleting user-role assignments. All endpoints
handle input validation, error management, and serialization of user-role
data for API responses.
"""
from flask import request, g
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from flask_restful import Resource
from app.models.db import db
from app.logger import logger
from app.schemas.user_role_schema import UserRoleSchema
from app.models.user_role import UserRole


class UserRoleListResource(Resource):
    """
    Resource for handling user-role assignment operations.

    Provides endpoints for creating and listing user-role assignments.
    """
    def get(self):
        """
        List all user-role assignments.

        Returns:
            tuple: JSON response with a list of user-role assignments and HTTP status code.
        """
        logger.info(
            "Fetching user-role assignments.",
            path=request.path,
            method=request.method,
            request_id=getattr(g, "request_id", None)
        )
        try:
            user_roles = UserRole.query.all()
            schema = UserRoleSchema(session=db.session, many=True)
            return schema.dump(user_roles), 200
        except SQLAlchemyError as err:
            logger.error(
                "Database error while fetching user-role assignments: %s", str(err)
            )
            return {
                "message": "An error occurred while fetching user-role assignments."
            }, 500

    def post(self):
        """
        Create a new user-role assignment.

        Returns:
            tuple: JSON response with the created user-role assignment and HTTP status code.
        """
        logger.info(
            "Creating new user-role assignment.",
            path=request.path,
            method=request.method,
            request_id=getattr(g, "request_id", None)
        )
        json_data = request.get_json()
        schema = UserRoleSchema(session=db.session)
        try:
            new_user_role = schema.load(json_data)
            db.session.add(new_user_role)
            db.session.commit()
            return schema.dump(new_user_role), 201
        except ValidationError as err:
            logger.error(
                "Validation error while creating user-role assignment: %s", err.messages
            )
            return {"errors": err.messages}, 400
        except IntegrityError as err:
            db.session.rollback()
            logger.error(
                "Integrity error while creating user-role assignment: %s", str(err)
            )
            return {"message": "User-role assignment already exists."}, 409
        except SQLAlchemyError as err:
            db.session.rollback()
            logger.error(
                "Database error while creating user-role assignment: %s", str(err)
            )
            return {
                "message": "An error occurred while creating the user-role assignment."
            }, 500


class UserRoleResource(Resource):
    """
    Resource for handling operations on a specific user-role assignment.

    Provides endpoints for retrieving, updating, and deleting a user-role assignment by its ID.
    """
    def patch(self, user_role_id):
        """
        Partially update a user-role assignment by its ID.

        Returns 400 if the payload is empty.

        Args:
            user_role_id (str): The unique identifier of the user-role assignment.

        Returns:
            tuple: JSON response with the updated user-role assignment data and
            HTTP status code.
        """
        schema = UserRoleSchema(session=db.session)
        json_data = request.get_json()
        if not json_data or not any(json_data.values()):
            return {
                "message": "Empty payload is not allowed."
            }, 400
        try:
            user_role = db.session.get(UserRole, user_role_id)
            if not user_role:
                return {
                    "message": "User-role assignment not found."
                }, 404
            user_role = schema.load(
                json_data, instance=user_role, partial=True
            )
            db.session.commit()
            return schema.dump(user_role), 200
        except ValidationError as err:
            logger.error(
                "Validation error while partially updating user-role "
                "assignment: %s", err.messages
            )
            return {"errors": err.messages}, 400
        except IntegrityError as err:
            db.session.rollback()
            logger.error(
                "Integrity error while partially updating user-role "
                "assignment: %s", str(err)
            )
            return {
                "message": "User-role assignment already exists."
            }, 409
        except SQLAlchemyError as err:
            db.session.rollback()
            logger.error(
                "Database error while partially updating user-role "
                "assignment: %s", str(err)
            )
            return {
                "message": (
                    "An error occurred while updating the user-role assignment."
                )
            }, 500

    def get(self, user_role_id):
        """
        Retrieve a user-role assignment by its ID.

        Args:
            user_role_id (str): The unique identifier of the user-role assignment.

        Returns:
            tuple: JSON response with the user-role assignment data and HTTP status code.
        """
        logger.info(
            "Fetching user-role assignment by ID.",
            path=request.path,
            method=request.method,
            request_id=getattr(g, "request_id", None)
        )
        try:
            user_role = db.session.get(UserRole, user_role_id)
            if not user_role:
                return {"message": "User-role assignment not found."}, 404
            schema = UserRoleSchema(session=db.session)
            return schema.dump(user_role), 200
        except SQLAlchemyError as err:
            logger.error(
                "Database error while fetching user-role assignment: %s", str(err)
            )
            return {
                "message": "An error occurred while fetching the user-role assignment."
            }, 500

    def put(self, user_role_id):
        """
        Update a user-role assignment by its ID.

        Args:
            user_role_id (str): The unique identifier of the user-role assignment.

        Returns:
            tuple: JSON response with the updated user-role assignment data and HTTP status code.
        """
        schema = UserRoleSchema(session=db.session)
        try:
            user_role = db.session.get(UserRole, user_role_id)
            if not user_role:
                return {"message": "User-role assignment not found."}, 404
            user_role = schema.load(request.json, instance=user_role)
            db.session.commit()
            return schema.dump(user_role), 200
        except ValidationError as err:
            logger.error(
                "Validation error while updating user-role assignment: %s", err.messages
            )
            return {"errors": err.messages}, 400
        except IntegrityError as err:
            db.session.rollback()
            logger.error(
                "Integrity error while updating user-role assignment: %s", str(err)
            )
            return {"message": "User-role assignment already exists."}, 409
        except SQLAlchemyError as err:
            db.session.rollback()
            logger.error(
                "Database error while updating user-role assignment: %s", str(err)
            )
            return {
                "message": "An error occurred while updating the user-role assignment."
            }, 500

    def delete(self, user_role_id):
        """
        Delete a user-role assignment by its ID.

        Args:
            user_role_id (str): The unique identifier of the user-role assignment.

        Returns:
            tuple: JSON response with a success message and HTTP status code 204.
        """
        logger.info(
            "Deleting user-role assignment by ID.",
            path=request.path,
            method=request.method,
            request_id=getattr(g, "request_id", None)
        )
        try:
            user_role = db.session.get(UserRole, user_role_id)
            if not user_role:
                return {"message": "User-role assignment not found."}, 404
            db.session.delete(user_role)
            db.session.commit()
            return '', 204
        except SQLAlchemyError as err:
            db.session.rollback()
            logger.error(
                "Database error while deleting user-role assignment: %s", str(err)
            )
            return {
                "message": "An error occurred while deleting the user-role assignment."
            }, 500
        except Exception as err:
            db.session.rollback()
            logger.error(
                "Unexpected error while deleting user-role assignment: %s", str(err)
            )
            return {"message": "An unexpected error occurred."}, 500
