"""
app.resources.policy
-------------------

This module defines RESTful resources for managing policies in the
PM Guardian API. It provides endpoints for creating, listing,
retrieving, updating, and deleting policies. All endpoints handle
input validation, error management, and serialization of policy data
for API responses.
"""

from flask import request, g
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from flask_restful import Resource
from app.models.db import db
from app.logger import logger
from app.schemas.policy_schema import PolicySchema
from app.models.policy import Policy


class PolicyListResource(Resource):
    """
    Resource for handling policy-related operations.

    Provides endpoints for creating and listing policies. Supports policy
    creation with validation and handles errors appropriately.
    """
    def get(self):
        """
        List all policies.

        Returns:
            tuple: JSON response with a list of policies and HTTP status code.
        """
        logger.info(
            "Fetching policies.",
            path=request.path,
            method=request.method,
            request_id=getattr(g, "request_id", None)
        )
        try:
            policies = Policy.query.all()
            schema = PolicySchema(session=db.session, many=True)
            return schema.dump(policies), 200
        except SQLAlchemyError as err:
            logger.error(
                "Database error while fetching policies: %s", str(err)
            )
            return {
                "message": "An error occurred while fetching policies."
            }, 500

    def post(self):
        """
        Create a new policy.

        Returns:
            tuple: JSON response with the created policy and HTTP status code.
        """
        logger.info(
            "Creating new policy.",
            path=request.path,
            method=request.method,
            request_id=getattr(g, "request_id", None)
        )
        json_data = request.get_json()
        schema = PolicySchema(session=db.session)
        try:
            new_policy = schema.load(json_data)
            db.session.add(new_policy)
            db.session.commit()
            return schema.dump(new_policy), 201
        except ValidationError as err:
            logger.error(
                "Validation error while creating policy: %s", str(err)
            )
            return {"message": str(err)}, 400
        except IntegrityError as err:
            db.session.rollback()
            logger.error(
                "Integrity error while creating policy: %s", str(err)
            )
            return {"message": "Policy already exists."}, 409
        except SQLAlchemyError as err:
            db.session.rollback()
            logger.error(
                "Database error while creating policy: %s", str(err)
            )
            return {
                "message": "An error occurred while creating the policy."
            }, 500


class PolicyResource(Resource):
    """
    Resource for handling operations on a specific policy.

    Provides endpoints for retrieving, updating, and deleting a policy by
    its ID. Supports policy retrieval with validation and handles errors
    appropriately.
    """
    def get(self, policy_id):
        """
        Retrieve a policy by its ID.

        Args:
            policy_id (str): The unique identifier of the policy.

        Returns:
            tuple: JSON response with the policy data and HTTP status code.
        """
        logger.info(
            "Fetching policy by ID.",
            path=request.path,
            method=request.method,
            request_id=getattr(g, "request_id", None)
        )
        try:
            policy = db.session.get(Policy, policy_id)
            if not policy:
                return {"message": "Policy not found."}, 404
            schema = PolicySchema(session=db.session)
            return schema.dump(policy), 200
        except SQLAlchemyError as err:
            logger.error(
                "Database error while fetching policy: %s", str(err)
            )
            return {
                "message": "An error occurred while fetching the policy."
            }, 500

    def put(self, policy_id):
        """
        Update a policy by its ID.

        Args:
            policy_id (str): The unique identifier of the policy.

        Returns:
            tuple: JSON response with the updated policy data and HTTP status code.
        """
        schema = PolicySchema(session=db.session)
        try:
            policy = db.session.get(Policy, policy_id)
            if not policy:
                return {"message": "Policy not found."}, 404
            policy = schema.load(request.json, instance=policy)
            db.session.commit()
            return schema.dump(policy), 200
        except ValidationError as err:
            logger.error(
                "Validation error while updating policy: %s", str(err)
            )
            return {"message": str(err)}, 400
        except SQLAlchemyError as err:
            logger.error(
                "Database error while updating policy: %s", str(err)
            )
            return {
                "message": "An error occurred while updating the policy."
            }, 500

    def patch(self, policy_id):
        """
        Partially update a policy by its ID.

        Args:
            policy_id (str): The unique identifier of the policy.

        Returns:
            tuple: JSON response with the updated policy data and HTTP status code.
        """
        schema = PolicySchema(session=db.session, partial=True)
        try:
            policy = db.session.get(Policy, policy_id)
            if not policy:
                return {"message": "Policy not found."}, 404
            policy = schema.load(request.json, instance=policy)
            db.session.commit()
            return schema.dump(policy), 200
        except ValidationError as err:
            logger.error(
                "Validation error while partially updating policy: %s", str(err)
            )
            return {"message": str(err)}, 400
        except SQLAlchemyError as err:
            logger.error(
                "Database error while partially updating policy: %s", str(err)
            )
            return {
                "message": "An error occurred while partially updating the policy."
            }, 500

    def delete(self, policy_id):
        """
        Delete a policy by its ID.

        Args:
            policy_id (str): The unique identifier of the policy.

        Returns:
            tuple: JSON response with a success message and HTTP status code 204.
        """
        logger.info(
            "Deleting policy by ID.",
            path=request.path,
            method=request.method,
            request_id=getattr(g, "request_id", None)
        )
        try:
            policy = db.session.get(Policy, policy_id)
            if not policy:
                return {
                    "message": "Policy not found."
                }, 404
            db.session.delete(policy)
            db.session.commit()
            return '', 204
        except SQLAlchemyError as err:
            db.session.rollback()
            logger.error(
                "Database error while deleting policy: %s",
                str(err)
            )
            return {
                "message": (
                    "An error occurred while deleting the policy."
                )
            }, 500
        except Exception as err:
            db.session.rollback()
            logger.error(
                "Unexpected error while deleting policy: %s",
                str(err)
            )
            return {
                "message": "An unexpected error occurred."
            }, 500
