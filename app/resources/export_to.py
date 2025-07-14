"""
export.py
---------

This module defines the ExportCSVResource for exporting all Dummy records
from the database as a downloadable CSV file through a REST endpoint.
"""
import io
import csv
from flask_restful import Resource
from flask import make_response
from app.models.dummy import Dummy


class ExportCSVResource(Resource):
    """
    Resource for exporting data to a CSV file.

    Methods:
        get():
            Export data to a CSV file and return it as a response.
    """

    def get(self):
        """
        Export all Dummy records to a CSV file and return it as a response.

        Returns:
            Response: A CSV file containing all Dummy records.
        """
        # Retrieve all Dummy records
        dummies = Dummy.get_all()

        # Prepare CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        # Write header
        writer.writerow(["id", "name", "description"])
        # Write data rows
        for dummy in dummies:
            writer.writerow([dummy.id, dummy.name, dummy.description])

        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = (
                'attachment; filename=export.csv')
        return response
