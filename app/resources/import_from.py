"""
import.py
---------

This module defines resources for importing data into the application
from CSV and JSON files via REST endpoints.
"""
import csv
import json
from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.models import db
from app.models.dummy import Dummy
from app.schemas.dummy_schema import DummySchema
from app.logger import logging

dummy_schema = DummySchema(session=db.session)

class ImportJSONResource(Resource):
    """
    Resource for importing data from a JSON file.

    Methods:
        post():
            Import data from a JSON file and return a success message.
    """

    def post(self):
        """
        Import data from a JSON file uploaded via multipart/form-data.

        Expects:
            A file field named 'file' containing a JSON file with a list of
            dummy items.

        Returns:
            dict: A success message indicating the number of records imported,
            or an error message.
        """
        if 'file' not in request.files:
            logging.error("No file part in the request.")
            return {"message": "No file part in the request."}, 400

        file = request.files['file']
        if file.filename == '':
            logging.error("No selected file.")
            return {"message": "No selected file."}, 400

        try:
            data = json.load(file)
            if not isinstance(data, list):
                logging.error("JSON must be a list of objects.")
                return {"message": "JSON must be a list of objects."}, 400

            count = 0
            errors = []
            for idx, item in enumerate(data):
                try:
                    validated = dummy_schema.load(item)
                    Dummy.create(
                        name=validated.name,
                        description=validated.description
                    )
                    count += 1
                except ValidationError as e:
                    errors.append({"index": idx, "error": str(e)})

            if errors:
                logging.warning(f"{len(errors)} errors encountered during import.")
                return {
                    "message": f"{count} records imported, {len(errors)} errors.",
                    "errors": errors
                }, 400 if count == 0 else 207  # 207: Multi-Status

            return {"message": f"{count} records imported successfully."}, 200
        except (json.JSONDecodeError, TypeError) as e:
            logging.error(f"JSON parsing error: {str(e)}")
            return {"message": f"Invalid JSON file: {str(e)}"}, 400
        except SQLAlchemyError as e:
            logging.error(f"Database error: {str(e)}")
            db.session.rollback()
            return {"message": f"Database error: {str(e)}"}, 400


class ImportCSVResource(Resource):
    """
    Resource for importing data from a CSV file.

    Methods:
        post():
            Import data from a CSV file and return a success message.
    """

    def post(self):
        """
        Import data from a CSV file uploaded via multipart/form-data.

        Expects:
            A file field named 'file' containing a CSV file with columns: name,
            description.

        Returns:
            dict: A success message indicating the number of records imported,
            or an error message.
        """
        if 'file' not in request.files:
            logging.error("No file part in the request.")
            return {"message": "No file part in the request."}, 400

        file = request.files['file']
        if file.filename == '':
            logging.error("No selected file.")
            return {"message": "No selected file."}, 400

        try:
            # Read CSV file
            stream = file.stream.read().decode('utf-8').splitlines()
            reader = csv.DictReader(stream)

            count = 0
            errors = []
            for idx, row in enumerate(reader):
                try:
                    validated = dummy_schema.load(row)
                    Dummy.create(
                        name=validated.name,
                        description=validated.description
                    )
                    count += 1
                except ValidationError as e:
                    logging.error(f"Validation error at row {idx}: {e.messages}")
                    errors.append({"index": idx, "error": str(e)})

            if errors:
                logging.warning(f"{len(errors)} errors encountered during import.")
                return {
                    "message": f"{count} records imported, {len(errors)} errors.",
                    "errors": errors
                }, 400 if count == 0 else 207  # 207: Multi-Status

            return {"message": f"{count} records imported successfully."}, 200
        except (csv.Error, UnicodeDecodeError) as e:
            logging.error(f"CSV parsing error: {str(e)}")
            return {"message": f"Invalid CSV file: {str(e)}"}, 400
        except SQLAlchemyError as e:
            logging.error(f"Database error: {str(e)}")
            db.session.rollback()
            return {"message": f"Database error: {str(e)}"}, 400
