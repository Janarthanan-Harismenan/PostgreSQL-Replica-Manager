from flask import Blueprint, request, jsonify
from utils.wal_handler import run_full_process  # Replace with the actual module containing the function
from config import DATABASE_CONFIG
 
# Define the WAL blueprint
wal_blueprint = Blueprint('wal', __name__)
 
@wal_blueprint.route('/run-wal-check', methods=['POST'])
def wal_check():
    """
    API endpoint to fetch WAL files and search for a keyword.
    """
    print("Executing walfounder.py: wal_check endpoint called.")
    data = request.json
 
    # Extract parameters from the request
    keyword = data.get("keyword")
    number_of_files = int(data.get("number_of_files"))
    selected_path = data.get("selected_path")  # Get the selected path from the request
    wal_file_name = data.get("wal_file_name", None)
   
    ssh_host = DATABASE_CONFIG.get("ssh_host")
    ssh_user = DATABASE_CONFIG.get("ssh_user")
    ssh_password = DATABASE_CONFIG.get("ssh_password")
 
    print(f"Request payload: keyword={keyword}, number_of_files={number_of_files}, selected_path={selected_path}")
 
    # Validate required parameters
    if not all([keyword, number_of_files, selected_path]):
        print("Missing required parameters in request.")
        return jsonify({"status": "error", "message": "Missing required parameters"}), 400
 
    # Run the process to fetch WAL files and search for the keyword
    result = run_full_process(
        host=ssh_host,
        ssh_user=ssh_user,
        ssh_password=ssh_password,
        keyword=keyword,
        number_of_files=number_of_files,
        selected_path=selected_path,  # Pass the selected path
        wal_file_name=wal_file_name
    )
 
    print("Result from run_full_process:", result)
    # Return the result as a JSON response
    return jsonify(result)