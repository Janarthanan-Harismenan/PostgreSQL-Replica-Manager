from flask import Blueprint, request, jsonify
from utils.shellWrapper import ShellWrapper
from utils.db_utils import up_to_enterprisedb
from utils.recovery_manager import get_port_by_config_key, run_full_process_with_recovery_time, run_full_process_with_wal_file, switch_primary_database
from config import DATABASE_CONFIG, SERVER_CONFIG, environment
import subprocess
import logging

# Define the recovery blueprint
recovery_blueprint = Blueprint('recovery', __name__)

@recovery_blueprint.route('/start-recovery', methods=['POST'])
def start_recovery_process():
    """
    API endpoint to start the database recovery process.
    """
    logging.info("Executing start-recovery endpoint.")

    data = request.json

    # Extract parameters from the request
    recovery_host = data.get("recovery_host")
    recovery_method = data.get("recovery_method")
    wal_file_name = data.get("wal_file_name")  # WAL file name (if recovery method is WAL)
    recovery_time = data.get("recovery_time")  # Recovery time (if method is Log)
    config_key = data.get("config_key")
    recovery_port = get_port_by_config_key(config_key)

    if not all([recovery_host, recovery_method]):
        return jsonify({"status": "error", "message": "Missing required parameters: 'recovery_host' and/or 'recovery_method'"}), 400

    if recovery_method == "WAL" and not wal_file_name:
        return jsonify({"status": "error", "message": "WAL file name is required for WAL recovery method"}), 400

    if recovery_method == "Log" and not recovery_time:
        return jsonify({"status": "error", "message": "Recovery time is required for Log recovery method"}), 400

    ssh_host = DATABASE_CONFIG.get("ssh_host")
    ssh_user = DATABASE_CONFIG.get("ssh_user")
    ssh_password = DATABASE_CONFIG.get("ssh_password")

    logging.info(f"Request payload: recoveryOption={recovery_host}, recoveryMethod={recovery_method}, "
                 f"walFileName={wal_file_name}, recoveryTime={recovery_time}")

    ssh = None
    shell = None

    try:
        if environment == "dev":
            ssh, shell = up_to_enterprisedb(ssh_host, ssh_user, ssh_password)
        else:
            shell = subprocess.Popen(["/bin/bash"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            shell = ShellWrapper(shell)
        logging.info("Switched to 'enterprisedb' user.")
        
        if recovery_method == "WAL":
            result = run_full_process_with_wal_file(
                wal_file_name=wal_file_name,
                recovery_host=recovery_host,
                shell=shell,
                recovery_port=recovery_port
            )
        elif recovery_method == "Log":
            result = run_full_process_with_recovery_time(
                recovery_time=recovery_time,
                recovery_host=recovery_host,
                shell=shell,
                recovery_port=recovery_port
            )
        else:
            return jsonify({"status": "error", "message": "Invalid recovery method specified."}), 400
        
        return jsonify({"status": "success", "message": result}), 200

    except Exception as e:
        logging.error(f"Error during recovery: {e}")
        return jsonify({"status": "error", "message": f"An error occurred during recovery: {str(e)}"}), 500
    
    finally:
        if shell:
            logging.info("Closing shell...")
            shell.close()
        if ssh:
            logging.info("Closing SSH connection...")
            ssh.close()

@recovery_blueprint.route("/get-server-config", methods=["GET"])
def get_server_pg_hosts_and_ports():
    """API route to fetch pg_host addresses, ports, and their config keys from SERVER_CONFIG."""
    try:
        pg_hosts_and_ports = [
            {
                "pg_host": config.get("pg_host"),
                "config_key": key
            }
            for key, config in SERVER_CONFIG.items()
        ]
        
        return jsonify({"pg_hosts_and_ports": pg_hosts_and_ports}), 200
    except Exception as e:
        logging.error(f"Error fetching server config: {e}")
        return jsonify({"error": str(e)}), 500
    
@recovery_blueprint.route("/switch-primary", methods=["POST"])
def switch_primary():
    """
    API endpoint to make the secondary database the primary one.
    """
    data = request.json

    ssh_host = DATABASE_CONFIG.get("ssh_host")
    ssh_user = DATABASE_CONFIG.get("ssh_user")
    ssh_password = DATABASE_CONFIG.get("ssh_password")
    
    recovery_host = data.get("recovery_host")
    config_key = data.get("config_key")
    recovery_port = get_port_by_config_key(config_key)
    
    if not all([recovery_host]):
        return jsonify({"status": "error", "message": "Missing required parameters: 'recovery_host' and/or 'recovery_method'"}), 400

    ssh = None
    shell = None

    try:
        if environment == "dev":
            ssh, shell = up_to_enterprisedb(ssh_host, ssh_user, ssh_password)
        else:
            shell = subprocess.Popen(["/bin/bash"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            shell = ShellWrapper(shell)
        logging.info("Switched to 'enterprisedb' user.")
        result = switch_primary_database(shell, recovery_host, recovery_port)
        return jsonify({"status": "success", "message": result}), 200
    except Exception as e:
        logging.error(f"Error while switching primary: {e}")
        return jsonify({"status": "error", "message": f"An error occurred while switching primary: {str(e)}"}), 500
    
    finally:
        if shell:
            logging.info("Closing shell...")
            shell.close()
        if ssh:
            logging.info("Closing SSH connection...")
            ssh.close()