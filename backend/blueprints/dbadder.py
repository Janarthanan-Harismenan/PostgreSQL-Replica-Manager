import os
import json  # Import the json module
from flask import Blueprint, request, jsonify

# Create blueprint
dbadder_blueprint = Blueprint("dbadder", __name__)

# Path to the JSON file
DATABASE_FILE = "database_details.json"

@dbadder_blueprint.route("/databases", methods=["GET"])
def get_databases():
    """
    Fetch stored database details from `database_details.json`.
    """
    try:
        if not os.path.exists(DATABASE_FILE):
            return jsonify({
                "status": "error",
                "message": "Database details file not found.",
                "databases": []
            }), 404

        with open(DATABASE_FILE, "r") as file:
            databases = json.load(file)

        return jsonify({
            "status": "success",
            "databases": databases
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to fetch database details: {str(e)}"
        }), 500

@dbadder_blueprint.route("dbadder", methods=['POST'])
def add_database():
    """
    API endpoint to add database details.
    """
    data = request.json
    name = data.get("name")
    dir = data.get("dir")

    if not name or not dir:
        return jsonify({"status": "error", "message": "Database name and directory are required"}), 400

    try:
        # Check if file exists
        if not os.path.exists(DATABASE_FILE):
            with open(DATABASE_FILE, "w") as file:
                file.write("[]")  # Initialize an empty list

        # Read existing data
        with open(DATABASE_FILE, "r") as file:
            databases = json.load(file)

        # Add new database
        databases.append({"name": name, "dir": dir})

        # Write updated data
        with open(DATABASE_FILE, "w") as file:
            json.dump(databases, file, indent=4)

        return jsonify({"status": "success", "message": "Database details added successfully"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
