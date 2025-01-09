from flask import Blueprint, jsonify, request
from utils.replica_manager import check_replica_status, manage_replication
from config import DATABASE_CONFIG, SERVER_CONFIG
from utils.db_utils import connect_to_db, close_connections, up_to_enterprisedb

# Flask blueprint
replica_blueprint = Blueprint("replica", __name__)

@replica_blueprint.route("/replica-status", methods=["GET"])
def get_replica_status():
    """
    Fetch the replication statuses for all database configurations.
    """
    try:
        print("Fetching replication statuses for all database configurations... (replica.py)")

        statuses = []
        
        data = DATABASE_CONFIG
        print(f"Request payload: {data} (catcheck.py)")
    
        # Extract parameters from the request
        ssh_host = data.get("ssh_host")
        ssh_user = data.get("ssh_user")
        ssh_password = data.get("ssh_password")
        
        print("(replica_manager.py) Checking replica status.")
        shell = up_to_enterprisedb(ssh_host, ssh_user, ssh_password)

        # Iterate over all database configurations in SERVER_CONFIG
        for config_name, config in SERVER_CONFIG.items():
            print(f"Checking replica status for {config_name}... (replica.py)")

            try:
                # Check replica status for the current configuration
                delayed_status = check_replica_status(shell, config)  # Assuming this function uses the database connection
                
                # Extract the pg_host and other details
                pg_host = delayed_status.get("pg_host", "Unknown")
                # port = delayed_status.get("port", "Unknown")
                port = str(delayed_status.get("port", "Unknown"))
                statuses.append({
                    "name": pg_host,
                    "port" : port,
                    "status": delayed_status.get("status", "Unknown"),
                    "delay": delayed_status.get("delay", "N/A")
                })
            except Exception as e:
                print(f"Error checking replica status for {config_name}: {str(e)} (replica.py)")
                statuses.append({
                    "name": config.get("pg_host", "Unknown"),
                    "port" : config.get("port", "Unknown"),
                    "status": "error",
                    "error": str(e)
                })

        # Return the array with the replica statuses
        return jsonify(statuses)

    except Exception as e:
        print(f"Error fetching replica statuses: {str(e)} (replica.py)")
        return jsonify({"status": "error", "error": str(e)}), 500

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
        server_port = data.get("port")
        
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
        shell = up_to_enterprisedb(ssh_host, ssh_user, ssh_password)
        
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