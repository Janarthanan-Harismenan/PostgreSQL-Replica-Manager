import os
# import app
from flask import Blueprint, jsonify, request, send_from_directory
from utils.replica_manager import check_replica_paused, check_replica_status, manage_replication
from config import DATABASE_CONFIG, SERVER_CONFIG, environment
from utils.db_utils import connect_to_db, close_connections, up_to_enterprisedb
import subprocess
import logging
 
# Flask blueprint
replica_blueprint = Blueprint("replica", __name__)
 
@replica_blueprint.route("/static/replica_status", methods=["GET"])
def serve_csv():
    """Serve the replica status CSV file."""
    try:
        return send_from_directory(
            os.path.join(os.getcwd(), 'static'),  # Path to static folder
            'replica_status.csv',                 # File to serve
            mimetype='text/csv'                   # Correct mime type for CSV
        )
    except Exception as e:
        logging.error(f"Error serving CSV: {e}")
        return jsonify({"error": "Failed to fetch CSV file"}), 500
 
@replica_blueprint.route("/replica-status", methods=["GET"])
def get_replica_status():
    """
    Fetch the replication statuses for all database configurations.
    """
    try:
        print("Fetching replication statuses for all database configurations... (replica.py)")
 
        statuses = []
 
        # Iterate over all database configurations in SERVER_CONFIG
        for config_name, config in SERVER_CONFIG.items():
            print(f"Checking replica status for {config_name}... (replica.py)")
 
            try:
                data = DATABASE_CONFIG
                print(f"Request payload: {data} (catcheck.py)")
            
                # Extract parameters from the request
                ssh_host = data.get("ssh_host")
                ssh_user = data.get("ssh_user")
                ssh_password = data.get("ssh_password")
                
                print("(replica_manager.py) Checking replica status.")
                # shell = up_to_enterprisedb(ssh_host, ssh_user, ssh_password)
                if environment == "dev" :
                    shell = up_to_enterprisedb(ssh_host, ssh_user, ssh_password)
                else :
                    shell = subprocess.Popen(["/bin/bash"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True )
                # Check replica status for the current configuration
                # delayed_status = check_replica_status(config)  # Assuming this function uses the database connection
                delayed_status = check_replica_status(shell, config)
               
                # Extract the pg_host and other details
                pg_host = delayed_status.get("pg_host", "Unknown")
                statuses.append({
                    "name": pg_host,
                    "delay_name": config_name,
                    # "status": delayed_status.get("status", "Unknown"),
                    "delay": delayed_status.get("delay", "N/A")
                })
            except Exception as e:
                print(f"Error checking replica status for {config_name}: {str(e)} (replica.py)")
                statuses.append({
                    "name": config.get("pg_host", "Unknown"),
                    # "status": "error",
                    "error": str(e)
                })
 
        # Return the array with the replica stprintatuses
        return jsonify(statuses)
 
    except Exception as e:
        print(f"Error fetching replica statuses: {str(e)} (replica.py)")
        return jsonify({"status": "error", "error": str(e)}), 500

 
@replica_blueprint.route("/status", methods=["GET"])
def get_status():
    statuses = []
    for config_name, config in SERVER_CONFIG.items():
            print(f"Checking replica status for {config_name}... (replica.py)")
 
            try:
                data = DATABASE_CONFIG
                print(f"Request payload: {data} (catcheck.py)")
            
                # Extract parameters from the request
                ssh_host = data.get("ssh_host")
                ssh_user = data.get("ssh_user")
                ssh_password = data.get("ssh_password")
                
                print("(replica_manager.py) Checking replica status.")
                # shell = up_to_enterprisedb(ssh_host, ssh_user, ssh_password)
                if environment == "dev" :
                    shell = up_to_enterprisedb(ssh_host, ssh_user, ssh_password)
                else :
                    shell = subprocess.Popen(["/bin/bash"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True )
                state=check_replica_paused(shell, config)
                if state:
                    status="paused"
                else:
                    status="running"
                statuses.append({"status":status,
                                "name":config.get("pg_host", "Unknown"),
                                "delay_name" : config_name})
            except Exception as e:
                print(f"Error checking replica status for {config_name}: {str(e)} (replica.py)")
                statuses.append({
                    "name": config.get("pg_host", "Unknown"),
                    # "status": "error",
                    "error": str(e)
                })
    return jsonify(statuses)

@replica_blueprint.route("/replica/manage", methods=["POST"])
def manage_replica():
    """
    Manage replication for a specific database server (pause or resume) via a single endpoint.
    
    Expected JSON Payload:
    {
        "action": "pause" or "resume",
        "name": "<pg_host>"  # pg_host value in SERVER_CONFIG
    }
    """
    try:
        # Get the action and server name from the JSON payload
        print("Receiving action and server name from the client request... (replica.py)")
        data = request.get_json()
        action = data.get("action")
        
        delay_name = data.get("delay_name")
        config = SERVER_CONFIG.get(delay_name)
        if config:
            server_port = config.get("port")
        else:
            return f"Config key '{delay_name}' not found."
        
        if not action or not server_port:
            print(f"Missing required parameters in the request. (replica.py) {server_port} {action}")
            return jsonify({"status": "error", "error": "Missing required parameters (action or name)."}), 400

        print(f"Action received: {action}, server port received: {server_port}")

        # Loop through SERVER_CONFIG to find the matching configuration by pg_host
        selected_config = None
        for config_name, config in SERVER_CONFIG.items():
            if config.get("port") == server_port:
                selected_config = config
                break

        if not selected_config:
            print(f"No matching configuration found for server port: {server_port} (replica.py)")
            return jsonify({"status": "error", "error": f"No configuration found for port: {server_port}"}), 400

        print(f"Found matching configuration: {selected_config}")


        data = DATABASE_CONFIG
        print(f"Request payload: {data} (catcheck.py)")
    
        # Extract parameters from the request
        ssh_host = data.get("ssh_host")
        ssh_user = data.get("ssh_user")
        ssh_password = data.get("ssh_password")
        
        print("(replica_manager.py) Checking replica status.")
        # shell = up_to_enterprisedb(ssh_host, ssh_user, ssh_password)
        if environment == "dev" :
            shell = up_to_enterprisedb(ssh_host, ssh_user, ssh_password)
        else :
            shell = subprocess.Popen(["/bin/bash"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True )
        
        # Connect to the specified server's database
        print("Attempting to establish SSH tunnel and connect to the specified replica database... (replica.py)")
        conn = connect_to_db(shell, selected_config)
        
        # Call the manage_replication function with the selected configuration and the action
        print(f"Managing replication with action: {action} for server: {server_port} (replica.py)")
        result = manage_replication(shell, selected_config, action)

        # Close the connection and tunnel after the operation
        print("Closing the database connection and SSH tunnel... (replica.py)")
        close_connections(conn)
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Error managing replica: {str(e)} (replica.py)")
        return jsonify({"status": "error", "error": str(e)}), 500