from flask import Blueprint, request, jsonify
from utils.db_utils import up_to_enterprisedb
from utils.wal_handler import run_full_process
from config import DATABASE_CONFIG, PATH_CONFIG, environment
import subprocess
from utils.shellWrapper import ShellWrapper
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Define the WAL blueprint
wal_blueprint = Blueprint('wal', __name__)

@wal_blueprint.route('/run-wal-check', methods=['POST'])
def wal_check():
    """
    API endpoint to fetch WAL files and search for a keyword.
    """
    logging.info("Executing wal_check endpoint.")
    data = request.json

    # Extract parameters from the request
    keyword = data.get("keyword")
    number_of_files = int(data.get("number_of_files"))
    selected_path = data.get("selected_path")  # Get the selected path from the request
    wal_file_name = data.get("wal_file_name", None)
   
    ssh_host = DATABASE_CONFIG.get("ssh_host")
    ssh_user = DATABASE_CONFIG.get("ssh_user")
    ssh_password = DATABASE_CONFIG.get("ssh_password")

    logging.info(f"Request payload: keyword={keyword}, number_of_files={number_of_files}, selected_path={selected_path}")

    # Validate required parameters
    if not all([keyword, number_of_files, selected_path]):
        logging.error("Missing required parameters in request.")
        return jsonify({"status": "error", "message": "Missing required parameters"}), 400
    
    ssh = None
    shell = None
    try:
        logging.info("Establishing SSH connection...")
        if environment == "dev":
            ssh, shell = up_to_enterprisedb(ssh_host, ssh_user, ssh_password)
        else:
            shell = subprocess.Popen(["/bin/bash"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            shell = ShellWrapper(shell)
        
        logging.info("Switched to 'enterprisedb' user.")

        # Run the process to fetch WAL files and search for the keyword
        result = run_full_process(
            shell=shell,
            keyword=keyword,
            number_of_files=number_of_files,
            selected_path=selected_path,  # Pass the selected path
            wal_file_name=wal_file_name
        )

        logging.info("WAL check process completed successfully.")
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error running wal_check: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
    
    finally:
        if shell:
            logging.info("Closing shell...")
            shell.close()
        if ssh:
            logging.info("Closing SSH connection...")
            ssh.close()

# Add route to fetch PATH_CONFIG
@wal_blueprint.route("/get-path-config", methods=["GET"])
def get_path_config():
    """API route to fetch paths from PATH_CONFIG."""
    try:
        paths = list(PATH_CONFIG.values())
        return jsonify({"paths": paths}), 200
    except Exception as e:
        logging.error(f"Error fetching path config: {str(e)}")
        return jsonify({"error": str(e)}), 500