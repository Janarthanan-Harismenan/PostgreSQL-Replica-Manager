from flask import Blueprint, request, jsonify, Flask, send_file
from utils.pg_catcheck import run_pg_catcheck_via_ssh, convert_log_to_pdf  # Import the updated function
import io

# Define the catcheck blueprint
catcheck_blueprint = Blueprint('catcheck', __name__)

@catcheck_blueprint.route('/run-pg-catcheck', methods=['POST'])
def pg_catcheck():
    """
    API endpoint to run the pg_catcheck command via SSH.
    """
    data = request.json

    # Extract parameters from the request
    ssh_host = data.get("ssh_host")
    ssh_user = data.get("ssh_user")
    ssh_password = data.get("ssh_password")
    pg_host = data.get("pg_host")
    port = data.get("port")
    user = data.get("user")
    database = data.get("database")
    pg_password = data.get("pg_password")

    # Validate required parameters
    if not all([ssh_host, ssh_user, ssh_password, pg_host, port, user, database, pg_password]):
        return jsonify({"status": "error", "message": "Missing required parameters"}), 400

    # Run the pg_catcheck command via SSH
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

    # Return the result as a JSON response
    return jsonify(result)

@catcheck_blueprint.route("/generate-pdf")
def generate_pdf():
    log_output = "Some log output content"
    pdf_filename = convert_log_to_pdf(log_output)  # Generate the PDF and get the filename

    # Read the PDF content as bytes
    with open(pdf_filename, "rb") as pdf_file:
        pdf_data = pdf_file.read()

    # Return the PDF as an in-memory file
    return send_file(
        io.BytesIO(pdf_data),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="pg_catcheck_output.pdf"
    )
