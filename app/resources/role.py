"""
Role Resource Module.

This module defines RESTful resources for managing roles within the PM Guardian API.
It provides endpoints for creating, listing, retrieving, updating, and deleting roles
associated with a company. The resources handle input validation, error management,
and serialization of role data for API responses.

Classes:
    RoleListResource: Resource for listing and creating roles for a company.
    RoleResource: Resource for retrieving, updating, and deleting a specific role by ID.

Dependencies:
    - Flask-RESTful for resource routing
    - Marshmallow for data validation and serialization
    - SQLAlchemy for ORM/database operations
    - Custom logging and error handling utilities
"""
from flask import request, g
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from flask_restful import Resource

from app.models import db
from app.logger import logger

from app.schemas.role_schema import RoleSchema
from app.models.role import Role

class RoleListResource(Resource):
    """
    Resource for handling role-related operations.

    This resource provides endpoints for creating and listing roles within a company.
    It supports role creation with validation and handles errors appropriately.
    """

    def get(self):
        """
        List all roles for the authenticated company.

        Returns:
            JSON response with a list of roles and HTTP status code 200.
        """
        logger.info(
            "Fetching roles for company.",
            path=request.path,
            method=request.method,
            request_id=getattr(g, "request_id", None)
        )
        
        try:
            company_id = request.args.get('company_id')
            roles = Role.query.filter_by(company_id=company_id).all()
            schema = RoleSchema(many=True)
            return schema.dump(roles), 200
        except SQLAlchemyError as e:
            logger.error("Database error while fetching roles: %s", str(e))
            return {"message": "An error occurred while fetching roles."}, 500

    def post(self):
        """
        Create a new role for the authenticated company.

        Returns:
            JSON response with the created role and HTTP status code 201.
        """
        schema = RoleSchema()
        try:
            role_data = schema.load(request.json)
            new_role = Role(**role_data)
            db.session.add(new_role)
            db.session.commit()
            return schema.dump(new_role), 201
        except ValidationError as err:
            logger.error("Validation error while creating role: %s", err.messages)
            return {"errors": err.messages}, 400
        except IntegrityError as e:
            db.session.rollback()
            logger.error("Integrity error while creating role: %s", str(e))
            return {"message": "Role already exists."}, 409
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error("Database error while creating role: %s", str(e))
            return {"message": "An error occurred while creating the role."}, 500

class RoleResource(Resource):
    """
    Resource for handling operations on a specific role.

    This resource provides endpoints for retrieving, updating, and deleting a role
    by its ID. It supports role retrieval with validation and handles errors appropriately.
    """

    def get(self, role_id):
        """
        Retrieve a role by its ID.

        Args:
            role_id (str): The unique identifier of the role.

        Returns:
            JSON response with the role data and HTTP status code 200.
        """
        logger.info(
            "Fetching role by ID.",
            path=request.path,
            method=request.method,
            request_id=getattr(g, "request_id", None)
        )
        
        try:
            role = Role.query.get(role_id)
            if not role:
                return {"message": "Role not found."}, 404
            
            schema = RoleSchema()
            return schema.dump(role), 200
        except SQLAlchemyError as e:
            logger.error("Database error while fetching role: %s", str(e))
            return {"message": "An error occurred while fetching the role."}, 500

    def put(self, role_id):
        """
        Update a role by its ID.

        Args:
            role_id (str): The unique identifier of the role.

        Returns:
            JSON response with the updated role data and HTTP status code 200.
        """
        schema = RoleSchema()
        try:
            role_data = schema.load(request.json)
            role = Role.query.get(role_id)
            if not role:
                return {"message": "Role not found."}, 404
            
            for key, value in role_data.items():
                setattr(role, key, value)
            
            db.session.commit()
            return schema.dump(role), 200
        except ValidationError as err:
            logger.error("Validation error while updating role: %s", err.messages)
            return {"errors": err.messages}, 400
        except IntegrityError as e:
            db.session.rollback()
            logger.error("Integrity error while updating role: %s", str(e))
            return {"message": "Role already exists."}, 409
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error("Database error while updating role: %s", str(e))
            return {"message": "An error occurred while updating the role."}, 500

    def patch(self, role_id):
        """
        Partially update a role by its ID.

        Args:
            role_id (str): The unique identifier of the role.

        Returns:
            JSON response with the updated role data and HTTP status code 200.
        """
        schema = RoleSchema(partial=True)
        try:
            role_data = schema.load(request.json)
            role = Role.query.get(role_id)
            if not role:
                return {"message": "Role not found."}, 404
            
            for key, value in role_data.items():
                setattr(role, key, value)
            
            db.session.commit()
            return schema.dump(role), 200
        except ValidationError as err:
            logger.error("Validation error while partially updating role: %s", err.messages)
            return {"errors": err.messages}, 400
        except IntegrityError as e:
            db.session.rollback()
            logger.error("Integrity error while partially updating role: %s", str(e))
            return {"message": "Role already exists."}, 409
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error("Database error while partially updating role: %s", str(e))
            return {"message": "An error occurred while partially updating the role."}, 500

    def delete(self, role_id):
        """
        Delete a role by its ID.

        Args:
            role_id (str): The unique identifier of the role.

        Returns:
            JSON response with a success message and HTTP status code 204.
        """
        logger.info(
            "Deleting role by ID.",
            path=request.path,
            method=request.method,
            request_id=getattr(g, "request_id", None)
        )
        
        try:
            role = Role.query.get(role_id)
            if not role:
                return {"message": "Role not found."}, 404
            
            db.session.delete(role)
            db.session.commit()
            return {"message": "Role deleted successfully."}, 204
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error("Database error while deleting role: %s", str(e))
            return {"message": "An error occurred while deleting the role."}, 500
        except Exception as e:
            db.session.rollback()
            logger.error("Unexpected error while deleting role: %s", str(e))
            return {"message": "An unexpected error occurred."}, 500
