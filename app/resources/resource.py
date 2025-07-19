"""
resource.py
"""
from flask import request, g
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from flask_restful import Resource as ApiResource

from app.models import db
from app.logger import logger

from app.schemas.resource_schema import ResourceSchema
from app.models.resource import Resource

class ResourceListResource(ApiResource):
    """
    Resource for handling resource-related operations.

    This resource provides endpoints for creating and listing resources within a company.
    It supports resource creation with validation and handles errors appropriately.
    """

    def get(self):
        """
        List all resources for the authenticated company.

        Returns:
            JSON response with a list of resources and HTTP status code 200.
        """
        logger.info(
            "Fetching resources for company.",
            path=request.path,
            method=request.method,
            request_id=getattr(g, "request_id", None)
        )

        try:
            company_id = request.args.get('company_id')
            resources = Resource.query.filter_by(company_id=company_id).all()
            schema = ResourceSchema(session=db.session, many=True)
            return schema.dump(resources), 200
        except SQLAlchemyError as e:
            logger.error("Database error while fetching resources: %s", str(e))
            return {"message": "An error occurred while fetching resources."}, 500

    def post(self):
        """
        Create a new resource for the authenticated company.

        Returns:
            JSON response with the created resource and HTTP status code 201.
        """
        logger.info(
            "Creating new resource.",
            path=request.path,
            method=request.method,
            request_id=getattr(g, "request_id", None)
        )
        json_data = request.get_json()
        schema = ResourceSchema(session=db.session)
        try:
            new_resource = schema.load(json_data)
            db.session.add(new_resource)
            db.session.commit()
            return schema.dump(new_resource), 201
        except ValidationError as ve:
            logger.error("Validation error while creating resource: %s", str(ve))
            return {"message": str(ve)}, 400
        except IntegrityError as ie:
            logger.error("Integrity error while creating resource: %s", str(ie))
            return {"message": "Resource already exists."}, 409
        except SQLAlchemyError as e:
            logger.error("Database error while creating resource: %s", str(e))
            return {"message": "An error occurred while creating the resource."}, 500


class ResourceResource(ApiResource):
    """
    Resource for handling operations on a specific resource instance.

    This resource provides endpoints for retrieving, updating, and deleting a specific resource.
    It supports validation and error handling for operations on individual resources.
    """

    def get(self, resource_id):
        """
        Retrieve a specific resource by its ID.

        Args:
            resource_id (str): The unique identifier of the resource.

        Returns:
            JSON response with the resource data and HTTP status code 200.
        """
        logger.info(
            "Fetching resource by ID.",
            path=request.path,
            method=request.method,
            request_id=getattr(g, "request_id", None)
        )

        try:
            resource = Resource.query.get(resource_id)
            if not resource:
                return {"message": "Resource not found."}, 404
            schema = ResourceSchema(session=db.session)
            return schema.dump(resource), 200
        except SQLAlchemyError as e:
            logger.error("Database error while fetching resource: %s", str(e))
            return {"message": "An error occurred while fetching the resource."}, 500
        
    def put(self, resource_id):
        """
        Update a specific resource by its ID.

        Args:
            resource_id (str): The unique identifier of the resource.

        Returns:
            JSON response with the updated resource data and HTTP status code 200.
        """
        logger.info(
            "Updating resource by ID.",
            path=request.path,
            method=request.method,
            request_id=getattr(g, "request_id", None)
        )

        schema = ResourceSchema(session=db.session)
        try:
            resource = Resource.query.get(resource_id)
            if not resource:
                return {"message": "Resource not found."}, 404
            
            # Use Marshmallow to update the instance in place
            resource = schema.load(request.json, instance=resource)
            
            db.session.commit()
            return schema.dump(resource), 200
        except ValidationError as ve:
            logger.error("Validation error while updating resource: %s", str(ve))
            return {"message": str(ve)}, 400
        except SQLAlchemyError as e:
            logger.error("Database error while updating resource: %s", str(e))
            return {"message": "An error occurred while updating the resource."}, 500
    
    def patch(self, resource_id):
        """
        Partially update a specific resource by its ID.

        Args:
            resource_id (str): The unique identifier of the resource.

        Returns:
            JSON response with the updated resource data and HTTP status code 200.
        """
        logger.info(
            "Partially updating resource by ID.",
            path=request.path,
            method=request.method,
            request_id=getattr(g, "request_id", None)
        )

        schema = ResourceSchema(session=db.session, partial=True)
        try:
            resource = Resource.query.get(resource_id)
            if not resource:
                return {"message": "Resource not found."}, 404
            
            # Use Marshmallow to update the instance in place (partial=True)
            resource = schema.load(request.json, instance=resource)
            
            db.session.commit()
            return schema.dump(resource), 200
        except ValidationError as ve:
            logger.error("Validation error while partially updating resource: %s", str(ve))
            return {"message": str(ve)}, 400
        except SQLAlchemyError as e:
            logger.error("Database error while partially updating resource: %s", str(e))
            return {"message": "An error occurred while partially updating the resource."}, 500
    
    def delete(self, resource_id):
        """
        Delete a specific resource by its ID.

        Args:
            resource_id (str): The unique identifier of the resource.

        Returns:
            JSON response with a success message and HTTP status code 204.
        """
        logger.info(
            "Deleting resource by ID.",
            path=request.path,
            method=request.method,
            request_id=getattr(g, "request_id", None)
        )

        try:
            resource = Resource.query.get(resource_id)
            if not resource:
                return {"message": "Resource not found."}, 404
            
            db.session.delete(resource)
            db.session.commit()
            return {"message": "Resource deleted successfully."}, 204
        except SQLAlchemyError as e:
            logger.error("Database error while deleting resource: %s", str(e))
            return {"message": "An error occurred while deleting the resource."}, 500
        except Exception as e:
            logger.error("Unexpected error while deleting resource: %s", str(e))
            return {"message": "An unexpected error occurred."}, 500