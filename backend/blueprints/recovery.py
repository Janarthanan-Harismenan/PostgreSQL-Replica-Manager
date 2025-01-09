from flask import Blueprint, request, jsonify
from utils.recovery_manager import run_full_process_with_recovery_time, run_full_process_with_wal_file, switch_primary_database  # Import the function for recovery
from config import DATABASE_CONFIG, SERVER_CONFIG

# Define the recovery blueprint
recovery_blueprint = Blueprint('recovery', __name__)

@recovery_blueprint.route('/start-recovery', methods=['POST'])
def start_recovery_process():
    """
    API endpoint to start the database recovery process.
    """
    print("Executing start-recovery endpoint.")

    data = request.json

    # Extract parameters from the request
    # Extract parameters from the request
    recovery_host = data.get("recovery_host")
    recovery_method = data.get("recovery_method")
    wal_file_name = data.get("wal_file_name")  # WAL file name (if recovery method is WAL)
    recovery_time = data.get("recovery_time")  # Recovery time (if method is Log)
    recovery_database = data.get("recovery_database")

    if not all([recovery_host, recovery_method]):
        return jsonify({"status": "error", "message": "Missing required parameters: 'recovery_host' and/or 'recovery_method'"}), 400

    if recovery_method == "WAL" and not wal_file_name:
        return jsonify({"status": "error", "message": "WAL file name is required for WAL recovery method"}), 400

    if recovery_method == "Log" and not recovery_time:
        return jsonify({"status": "error", "message": "Recovery time is required for Log recovery method"}), 400


    # Retrieve database connection details from config
    ssh_host = DATABASE_CONFIG.get("ssh_host")
    ssh_user = DATABASE_CONFIG.get("ssh_user")
    ssh_password = DATABASE_CONFIG.get("ssh_password")
    # pg_host = DATABASE_CONFIG.get("pg_host")

    print(f"Request payload: recoveryOption={recovery_host}, recoveryMethod={recovery_method}, "
          f"walFileName={wal_file_name}, recoveryTime={recovery_time}")

    try:
        # Call the appropriate recovery function based on the recovery method
        if recovery_method == "WAL":
            # Call the function for WAL recovery
            result = run_full_process_with_wal_file(
                # recovery_host=recovery_host,
                wal_file_name=wal_file_name,
                ssh_host=ssh_host,
                # pg_host=pg_host,
                recovery_host =recovery_host,
                ssh_user=ssh_user,
                ssh_password=ssh_password,
                recovery_database = recovery_database
            )
            
        elif recovery_method == "Log":
            # Call the function for Log recovery (using recovery_time)
            result = run_full_process_with_recovery_time(
                # recovery_host=recovery_host,
                recovery_time=recovery_time,
                ssh_host=ssh_host,
                # pg_host=pg_host,
                recovery_host = recovery_host,
                ssh_user=ssh_user,
                ssh_password=ssh_password,
                recovery_database = recovery_database
            )
        else:
            return jsonify({"status": "error", "message": "Invalid recovery method specified."}), 400
        
        # Return the result of the recovery process
        return jsonify({"status": "success", "message": result}), 200

    except Exception as e:
        print(f"Error during recovery: {e}")
        return jsonify({"status": "error", "message": f"An error occurred during recovery: {str(e)}"}), 500

# @recovery_blueprint.route("/get-server-config", methods=["GET"])
# def get_server_pg_hosts():
#     """API route to fetch pg_host addresses from SERVER_CONFIG."""
#     try:
#         # Extract all pg_host addresses from SERVER_CONFIG
#         pg_hosts = [config.get("pg_host") for config in SERVER_CONFIG.values()]
#         return jsonify({"pg_hosts": pg_hosts}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@recovery_blueprint.route("/get-server-config", methods=["GET"])
def get_server_pg_hosts_and_ports():
    """API route to fetch pg_host addresses and ports from SERVER_CONFIG."""
    try:
        # Extract all pg_host addresses and ports from SERVER_CONFIG
        pg_hosts_and_ports = [
            {"pg_host": config.get("pg_host"), "port": config.get("port")}
            for config in SERVER_CONFIG.values()
        ]
        return jsonify({"pg_hosts_and_ports": pg_hosts_and_ports}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@recovery_blueprint.route("/switch-primary", methods=["POST"])
def switch_primary():
    """
    API endpoint to make the secondary database the primary one.
    """
    # data = request.json
    # secondary_host = data.get("secondary_host")
    # recovery_database = data.get("recovery_database")

    # if not all([recovery_host, secondary_host, recovery_database]):
    #     return jsonify({"status": "error", "message": "Missing required parameters"}), 400
    
    data = request.json

    # Extract parameters from the request
    # Extract parameters from the request
    
    ssh_host = DATABASE_CONFIG.get("ssh_host")
    ssh_user = DATABASE_CONFIG.get("ssh_user")
    ssh_password = DATABASE_CONFIG.get("ssh_password")
    
    recovery_host = data.get("recovery_host")
    recovery_database = data.get("recovery_database")
    
    if not all([recovery_host, recovery_database]):
        return jsonify({"status": "error", "message": "Missing required parameters: 'recovery_host' and/or 'recovery_method'"}), 400

    try:
        result = switch_primary_database(ssh_host, ssh_user, ssh_password, recovery_database, recovery_host)
        return jsonify({"status": "success", "message": result}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"An error occurred while switching primary: {str(e)}"}), 500