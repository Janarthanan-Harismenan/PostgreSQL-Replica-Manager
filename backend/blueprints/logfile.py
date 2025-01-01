from flask import Blueprint, request, jsonify
from utils.log_handler import fetch_last_10_logs,search_log_file_for_keyword # Replace with the actual module containing the function
from config import DATABASE_CONFIG
import os
# Define the logs blueprint
logs_blueprint = Blueprint('logs', __name__)
 
@logs_blueprint.route('/fetch-last-10-logs', methods=['GET'])
def fetch_logs():
    """
    API endpoint to fetch the last 10 modified log files.
    """
    print("Executing fetch_logs endpoint.")
 
    ssh_host = DATABASE_CONFIG.get("ssh_host")
    ssh_user = DATABASE_CONFIG.get("ssh_user")
    ssh_password = DATABASE_CONFIG.get("ssh_password")
 
    print(f"Fetching last 10 logs for host={ssh_host}, user={ssh_user}")
 
    # Run the process to fetch the last 10 log files
    result = fetch_last_10_logs(
        host=ssh_host,
        ssh_user=ssh_user,
        ssh_password=ssh_password
    )
 
    print("Result from fetch_last_10_logs:", result)
    # Return the result as a JSON response
    return jsonify(result)
 
 
@logs_blueprint.route('/search-content-of-log-file', methods=['POST'])
def search_content_of_log_file():
    """
    API endpoint to search for a keyword in a specific log file.
    """
    print("Executing search-content-of-log-file endpoint.")
    data = request.json
 
    # Extract parameters from the request
    log_file_name = data.get("log_file_name")
    keyword = data.get("keyword")
 
    ssh_host = DATABASE_CONFIG.get("ssh_host")
    ssh_user = DATABASE_CONFIG.get("ssh_user")
    ssh_password = DATABASE_CONFIG.get("ssh_password")
 
    print(f"Request payload: log_file_name={log_file_name}, keyword={keyword}")
 
    # Validate required parameters
    if not all([log_file_name, keyword]):
        print("Missing required parameters in request.")
        return jsonify({"status": "error", "message": "Missing required parameters"}), 400
 
    try:
       
 
        # Specify the log directory path
        log_directory = "/u01/edb/as15/data/log"  # Adjust to your log directory
        log_file_path = os.path.join(log_directory, log_file_name)
        log_file_path = log_file_path.replace("\\", "/")
        # Search the log file for the keyword
        matched_lines = search_log_file_for_keyword(ssh_host, ssh_user, ssh_password, log_file_path, keyword)
 
        return jsonify({"status": "success", "matched_lines": matched_lines})
 
    except Exception as e:
        print(f"Error in search_log_file: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500