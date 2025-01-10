from flask import Blueprint, request, jsonify, send_file
# from utils.recovery_manager import get_port_by_config_key
from utils.pg_catcheck import  convert_log_to_pdf,get_databases,run_pg_catcheck_via_ssh # Import updated utilities
import io
from config import DATABASE_CONFIG, SERVER_CONFIG
 
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
 
    print("Received request to run pg_catcheck. (catcheck.py)")
 
    data = DATABASE_CONFIG
    print(f"Request payload: {data} (catcheck.py)")
 
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
        # print(f"user : {user}")
        database = config.get("database")
        pg_password = config.get("pg_password")
        port = config.get("port")
    else:
        return f"Config key '{config_key}' not found."
 
    # Validate required parameters
    if not all([ssh_host, ssh_user, ssh_password, pg_host, port, user, database, pg_password]):
        print("Missing required parameters in the request. (catcheck.py)")
        return jsonify({"status": "error", "message": "Missing required parameters"}), 400
    
    print("Hello")
 
    # Run the pg_catcheck command via SSH
    try:
        print("Running pg_catcheck command via SSH... (catcheck.py)")
        result = run_pg_catcheck_via_ssh(
            host=ssh_host,
            ssh_user=ssh_user,
            ssh_password=ssh_password,
            pg_host=pg_host,
            port=port,
            user=user,
            database=database,
            pg_password=pg_password
        )
        print("pg_catcheck command executed successfully. (catcheck.py)")
 
        # Save the output for PDF generation
        latest_output["output"] = result.get("output", "")
 
        return jsonify(result)
    except Exception as e:
        print(f"Error running pg_catcheck: {str(e)} (catcheck.py)")
        return jsonify({"status": "error", "message": str(e)}), 500
 
 
@catcheck_blueprint.route("/generate-pdf", methods=["GET"])
def generate_pdf():
    """
    API endpoint to generate a PDF from the latest pg_catcheck output.
    """
    global latest_output  # Access the global variable containing the latest output
 
    print("Received request to generate PDF. (catcheck.py)")
 
    log_output = latest_output.get("output", "")
    if not log_output:
        print("No log output available to generate PDF. (catcheck.py)")
        return jsonify({"status": "error", "message": "No log output available"}), 400
 
    try:
        print("Generating PDF from log output... (catcheck.py)")
        pdf_filename = convert_log_to_pdf(log_output)  # Generate the PDF and get the filename
        print(f"PDF generated successfully: {pdf_filename} (catcheck.py)")
 
        # Read the PDF content as bytes
        with open(pdf_filename, "rb") as pdf_file:
            pdf_data = pdf_file.read()
 
        print("Returning generated PDF as response. (catcheck.py)")
        return send_file(
            io.BytesIO(pdf_data),
            mimetype="application/pdf",
            as_attachment=True,
            download_name="pg_catcheck_output.pdf"
        )
    except Exception as e:
        print(f"Error generating PDF: {str(e)} (catcheck.py)")
        return jsonify({"status": "error", "message": str(e)}), 500