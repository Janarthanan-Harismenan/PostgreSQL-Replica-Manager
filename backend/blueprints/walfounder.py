from flask import Blueprint, request, jsonify
from utils.db_utils import up_to_enterprisedb
from utils.wal_handler import run_full_process  # Replace with the actual module containing the function
from config import DATABASE_CONFIG, PATH_CONFIG, environment
import subprocess
 
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
    
    # shell = up_to_enterprisedb(ssh_host, ssh_user, ssh_password)
    if environment == "dev" :
        shell = up_to_enterprisedb(ssh_host, ssh_user, ssh_password)
    else :
        shell = subprocess.Popen(["/bin/bash"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True )
        
    print("Switched to 'enterprisedb' user.")
 
    # Run the process to fetch WAL files and search for the keyword
    result = run_full_process(
        shell = shell,
        keyword=keyword,
        number_of_files=number_of_files,
        selected_path=selected_path,  # Pass the selected path
        wal_file_name=wal_file_name
    )
 
    print("Result from run_full_process:", result)
    # Return the result as a JSON response
    return jsonify(result)

# Add route to fetch PATH_CONFIG
@wal_blueprint.route("/get-path-config", methods=["GET"])
def get_path_config():
    """API route to fetch paths from PATH_CONFIG."""
    try:
        paths = list(PATH_CONFIG.values())
        return jsonify({"paths": paths}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500