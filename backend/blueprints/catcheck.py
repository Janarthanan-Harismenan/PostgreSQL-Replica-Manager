from flask import Blueprint, request, jsonify, send_file
from utils.pg_catcheck import run_pg_catcheck_via_ssh, convert_log_to_pdf  # Import the updated function
import io
from config import DATABASE_CONFIG

# Define the catcheck blueprint
catcheck_blueprint = Blueprint('catcheck', __name__)

@catcheck_blueprint.route('/run-pg-catcheck')
def pg_catcheck():
    """
    API endpoint to run the pg_catcheck command via SSH.
    """
    print("Received request to run pg_catcheck. (catcheck.py)")

    data = DATABASE_CONFIG
    print(f"Request payload: {data} (catcheck.py)")

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
        print("Missing required parameters in the request. (catcheck.py)")
        return jsonify({"status": "error", "message": "Missing required parameters"}), 400

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
        return jsonify(result)
    except Exception as e:
        print(f"Error running pg_catcheck: {str(e)} (catcheck.py)")
        return jsonify({"status": "error", "message": str(e)}), 500

@catcheck_blueprint.route("/generate-pdf")
def generate_pdf():
    """
    API endpoint to generate a PDF from log output.
    """
    print("Received request to generate PDF. (catcheck.py)")

    log_output = "Some log output content"
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