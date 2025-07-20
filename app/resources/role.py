"""
app.resources.role
-----------------

This module defines RESTful resources for managing roles in the
PM Guardian API. It provides endpoints for creating, listing,
retrieving, updating, and deleting roles associated with a company.
All endpoints handle input validation, error management, and
serialization of role data for API responses.
"""
import uuid
from flask import request, g
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from flask_restful import Resource
from app.models.db import db
from app.logger import logger
from app.schemas.role_schema import RoleSchema
from app.models.role import Role
from app.models.role_policy import RolePolicy
from app.models.policy import Policy
from app.schemas.policy_schema import PolicySchema


class RoleListResource(Resource):
    """
    Resource for handling role-related operations.

    Provides endpoints for creating and listing roles within a company.
    Supports role creation with validation and handles errors
    appropriately.
    """
    def get(self):
        """
        List all roles for the authenticated company.

        Returns:
            tuple: JSON response with a list of roles and HTTP status code.
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
            schema = RoleSchema(session=db.session, many=True)
            return schema.dump(roles), 200
        except SQLAlchemyError as err:
            logger.error(
                "Database error while fetching roles: %s", str(err)
            )
            return {
                "message": "An error occurred while fetching roles."
            }, 500

    def post(self):
        """
        Create a new role for the authenticated company.

        Returns:
            tuple: JSON response with the created role and HTTP status code.
        """
        logger.info(
            "Creating new role.",
            path=request.path,
            method=request.method,
            request_id=getattr(g, "request_id", None)
        )
        json_data = request.get_json()
        schema = RoleSchema(session=db.session)
        try:
            new_role = schema.load(json_data)
            db.session.add(new_role)
            db.session.commit()
            return schema.dump(new_role), 201
        except ValidationError as err:
            logger.error(
                "Validation error while creating role: %s", err.messages
            )
            return {"errors": err.messages}, 400
        except IntegrityError as err:
            db.session.rollback()
            logger.error(
                "Integrity error while creating role: %s", str(err)
            )
            return {"message": "Role already exists."}, 409
        except SQLAlchemyError as err:
            db.session.rollback()
            logger.error(
                "Database error while creating role: %s", str(err)
            )
            return {
                "message": "An error occurred while creating the role."
            }, 500


class RoleResource(Resource):
    """
    Resource for handling operations on a specific role.

    Provides endpoints for retrieving, updating, and deleting a role by its
    ID. Supports role retrieval with validation and handles errors
    appropriately.
    """
    def get(self, role_id):
        """
        Retrieve a role by its ID.

        Args:
            role_id (str): The unique identifier of the role.

        Returns:
            tuple: JSON response with the role data and HTTP status code.
        """
        logger.info(
            "Fetching role by ID.",
            path=request.path,
            method=request.method,
            request_id=getattr(g, "request_id", None)
        )
        try:
            role = db.session.get(Role, role_id)
            if not role:
                return {"message": "Role not found."}, 404
            schema = RoleSchema(session=db.session)
            return schema.dump(role), 200
        except SQLAlchemyError as err:
            logger.error(
                "Database error while fetching role: %s", str(err)
            )
            return {
                "message": "An error occurred while fetching the role."
            }, 500

    def put(self, role_id):
        """
        Update a role by its ID.

        Args:
            role_id (str): The unique identifier of the role.

        Returns:
            tuple: JSON response with the updated role data and HTTP status code.
        """
        schema = RoleSchema(session=db.session)
        try:
            role = db.session.get(Role, role_id)
            if not role:
                return {"message": "Role not found."}, 404
            role = schema.load(request.json, instance=role)
            db.session.commit()
            return schema.dump(role), 200
        except ValidationError as err:
            logger.error(
                "Validation error while updating role: %s", err.messages
            )
            return {"errors": err.messages}, 400
        except IntegrityError as err:
            db.session.rollback()
            logger.error(
                "Integrity error while updating role: %s", str(err)
            )
            return {"message": "Role already exists."}, 409
        except SQLAlchemyError as err:
            db.session.rollback()
            logger.error(
                "Database error while updating role: %s", str(err)
            )
            return {
                "message": "An error occurred while updating the role."
            }, 500

    def patch(self, role_id):
        """
        Partially update a role by its ID.

        Args:
            role_id (str): The unique identifier of the role.

        Returns:
            tuple: JSON response with the updated role data and HTTP status code.
        """
        schema = RoleSchema(session=db.session, partial=True)
        try:
            role = db.session.get(Role, role_id)
            if not role:
                return {"message": "Role not found."}, 404
            role = schema.load(request.json, instance=role)
            db.session.commit()
            return schema.dump(role), 200
        except ValidationError as err:
            logger.error(
                "Validation error while partially updating role: %s", err.messages
            )
            return {"errors": err.messages}, 400
        except IntegrityError as err:
            db.session.rollback()
            logger.error(
                "Integrity error while partially updating role: %s", str(err)
            )
            return {"message": "Role already exists."}, 409
        except SQLAlchemyError as err:
            db.session.rollback()
            logger.error(
                "Database error while partially updating role: %s", str(err)
            )
            return {
                "message": "An error occurred while partially updating the role."
            }, 500

    def delete(self, role_id):
        """
        Delete a role by its ID.

        Args:
            role_id (str): The unique identifier of the role.

        Returns:
            tuple: JSON response with a success message and HTTP status code 204.
        """
        logger.info(
            "Deleting role by ID.",
            path=request.path,
            method=request.method,
            request_id=getattr(g, "request_id", None)
        )
        try:
            role = db.session.get(Role, role_id)
            if not role:
                return {
                    "message": "Role not found."
                }, 404
            db.session.delete(role)
            db.session.commit()
            return '', 204
        except SQLAlchemyError as err:
            db.session.rollback()
            logger.error(
                "Database error while deleting role: %s",
                str(err)
            )
            return {
                "message": (
                    "An error occurred while deleting the role."
                )
            }, 500
        except Exception as err:
            db.session.rollback()
            logger.error(
                "Unexpected error while deleting role: %s",
                str(err)
            )
            return {
                "message": "An unexpected error occurred."
            }, 500


class RolePoliciesResource(Resource):
    """
    Resource for managing policies assigned to a role.

    Provides endpoints to assign, list, and remove policies for a role.
    """
    def post(self, role_id):
        """
        Assign a policy to a role.

        Args:
            role_id (str): The unique identifier of the role.

        Returns:
            tuple: JSON response and HTTP status code.
        """
        logger.info(
            "Assigning policy to role.",
            path=request.path,
            method=request.method,
            request_id=getattr(g, "request_id", None)
        )
        json_data = request.get_json()
        policy_id = json_data.get("policy_id")
        if not policy_id:
            return {"message": "Missing policy_id."}, 400
        try:
            # Check if role and policy exist
            role = db.session.get(Role, role_id)
            policy = db.session.get(Policy, policy_id)
            if not role or not policy:
                return {"message": "Role or policy not found."}, 404
            # Check if already assigned
            existing = RolePolicy.query.filter_by(
                role_id=role_id, policy_id=policy_id
            ).first()
            if existing:
                return {"message": "Policy already assigned to role."}, 409

            role_policy = RolePolicy(id=str(uuid.uuid4()), role_id=role_id, policy_id=policy_id)
            db.session.add(role_policy)
            db.session.commit()
            return {"message": "Policy assigned to role."}, 201
        except SQLAlchemyError as err:
            db.session.rollback()
            logger.error(
                "Database error while assigning policy: %s", str(err)
            )
            return {
                "message": "An error occurred while assigning the policy."
            }, 500

    def get(self, role_id):
        """
        List policies assigned to a role.

        Args:
            role_id (str): The unique identifier of the role.

        Returns:
            tuple: JSON response with list of policies and HTTP status code.
        """
        logger.info(
            "Listing policies for role.",
            path=request.path,
            method=request.method,
            request_id=getattr(g, "request_id", None)
        )
        try:
            role = db.session.get(Role, role_id)
            if not role:
                return {"message": "Role not found."}, 404
            role_policies = RolePolicy.query.filter_by(role_id=role_id).all()
            policy_ids = [rp.policy_id for rp in role_policies]
            policies = Policy.query.filter(Policy.id.in_(policy_ids)).all()
            schema = PolicySchema(many=True, session=db.session)
            return schema.dump(policies), 200
        except SQLAlchemyError as err:
            logger.error(
                "Database error while listing policies: %s", str(err)
            )
            return {
                "message": "An error occurred while listing policies."
            }, 500
        except Exception as err:
            logger.error(
                "Unexpected error while listing policies: %s", str(err)
            )
            return {"message": "An unexpected error occurred."}, 500

    def delete(self, role_id):
        """
        Remove a policy from a role.

        Args:
            role_id (str): The unique identifier of the role.

        Returns:
            tuple: JSON response and HTTP status code 204.
        """
        logger.info(
            "Removing policy from role.",
            path=request.path,
            method=request.method,
            request_id=getattr(g, "request_id", None)
        )
        policy_id = request.args.get("policy_id")
        if not policy_id:
            return {"message": "Missing policy_id in query."}, 400
        try:
            role = db.session.get(Role, role_id)
            policy = db.session.get(Policy, policy_id)
            if not role or not policy:
                return {"message": "Role or policy not found."}, 404
            role_policy = RolePolicy.query.filter_by(
                role_id=role_id, policy_id=policy_id
            ).first()
            if not role_policy:
                return {"message": "Policy not assigned to role."}, 404
            db.session.delete(role_policy)
            db.session.commit()
            return '', 204
        except SQLAlchemyError as err:
            db.session.rollback()
            logger.error(
                "Database error while removing policy: %s", str(err)
            )
            return {
                "message": "An error occurred while removing the policy."
            }, 500
        except Exception as err:
            db.session.rollback()
            logger.error(
                "Unexpected error while removing policy: %s", str(err)
            )
            return {"message": "An unexpected error occurred."}, 500
