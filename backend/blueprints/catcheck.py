import subprocess
from flask import Blueprint, request, jsonify, send_file
from utils.db_utils import up_to_enterprisedb
from utils.pg_catcheck import convert_log_to_pdf, run_pg_catcheck_via_ssh
import io
from config import DATABASE_CONFIG, SERVER_CONFIG, environment
from utils.shellWrapper import ShellWrapper
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Define the catcheck blueprint
catcheck_blueprint = Blueprint('catcheck', __name__)

# Store the latest pg_catcheck output for generating the PDF
latest_output = {"output": ""}

@catcheck_blueprint.route('/run-pg-catcheck', methods=['POST'])
def pg_catcheck():
    """
    API endpoint to run the pg_catcheck command via SSH.
    """
    global latest_output  # Use global variable to store output for the PDF generation

    logging.info("Received request to run pg_catcheck.")

    data = DATABASE_CONFIG
    logging.info(f"Request payload: {data}")

    # Extract parameters from the request
    ssh_host = data.get("ssh_host")
    ssh_user = data.get("ssh_user")
    ssh_password = data.get("ssh_password")
    pg_host = request.json.get("pg_host")
    
    config_key = request.json.get("config_key")
    
    config = SERVER_CONFIG.get(config_key)
        
    # Check if the config exists and return the port
    if config:
        user = config.get("user")
        database = config.get("database")
        pg_password = config.get("pg_password")
        port = config.get("port")
    else:
        return f"Config key '{config_key}' not found."

    # Validate required parameters
    if not all([ssh_host, ssh_user, ssh_password, pg_host, port, user, database, pg_password]):
        logging.error("Missing required parameters in the request.")
        return jsonify({"status": "error", "message": "Missing required parameters"}), 400

    ssh = None
    shell = None
    
    try:
        logging.info("Running pg_catcheck command via SSH...")
        if environment == "dev":
            ssh, shell = up_to_enterprisedb(ssh_host, ssh_user, ssh_password)
        else:
            shell = subprocess.Popen(["/bin/bash"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            shell = ShellWrapper(shell)
        
        logging.info("Switched to 'enterprisedb' user.")
        result = run_pg_catcheck_via_ssh(
            shell=shell,
            pg_host=pg_host,
            port=port,
            user=user,
            database=database,
            pg_password=pg_password
        )
        logging.info("pg_catcheck command executed successfully.")

        # Save the output for PDF generation
        latest_output["output"] = result.get("output", "")

        return jsonify(result)
    except Exception as e:
        logging.error(f"Error running pg_catcheck: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if shell:
            logging.info("Closing shell...")
            shell.close()
        if ssh:
            logging.info("Closing SSH connection...")
            ssh.close()

@catcheck_blueprint.route("/generate-pdf", methods=["GET"])
def generate_pdf():
    """
    API endpoint to generate a PDF from the latest pg_catcheck output.
    """
    global latest_output  # Access the global variable containing the latest output

    logging.info("Received request to generate PDF.")

    log_output = latest_output.get("output", "")
    if not log_output:
        logging.error("No log output available to generate PDF.")
        return jsonify({"status": "error", "message": "No log output available"}), 400

    try:
        logging.info("Generating PDF from log output...")
        pdf_filename = convert_log_to_pdf(log_output)  # Generate the PDF and get the filename
        logging.info(f"PDF generated successfully: {pdf_filename}")

        # Read the PDF content as bytes
        with open(pdf_filename, "rb") as pdf_file:
            pdf_data = pdf_file.read()

        logging.info("Returning generated PDF as response.")
        return send_file(
            io.BytesIO(pdf_data),
            mimetype="application/pdf",
            as_attachment=True,
            download_name="pg_catcheck_output.pdf"
        )
    except Exception as e:
        logging.error(f"Error generating PDF: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500