from flask import Blueprint, request, jsonify, Flask
from utils.wal_handler import run_full_process  # Replace with the actual module containing the function

# Define the WAL blueprint
wal_blueprint = Blueprint('wal', __name__)

@wal_blueprint.route('/run-wal-check', methods=['POST'])
def wal_check():
    """
    API endpoint to fetch WAL files and search for a keyword.
    """
    data = request.json

    # Extract parameters from the request
    ssh_host = data.get("ssh_host")
    ssh_user = data.get("ssh_user")
    ssh_password = data.get("ssh_password")
    wal_dir = data.get("wal_dir")
    num_files = data.get("num_files", 5)  # Default to last 5 WAL files if not provided
    keyword = data.get("keyword")

    # Validate required parameters
    if not all([ssh_host, ssh_user, ssh_password, wal_dir, keyword]):
        return jsonify({"status": "error", "message": "Missing required parameters"}), 400

    # Run the process to fetch WAL files and search for the keyword
    result = run_full_process(
        host=ssh_host,
        ssh_user=ssh_user,
        ssh_password=ssh_password,
        wal_dir=wal_dir,
        num_files=num_files,
        keyword=keyword
    )

    # Return the result as a JSON response
    return jsonify(result)