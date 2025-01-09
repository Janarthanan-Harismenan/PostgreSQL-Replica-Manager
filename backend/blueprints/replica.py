from flask import Blueprint, jsonify, request
from utils.replica_manager import check_replica_status, manage_replication
from config import DATABASE_CONFIG, SERVER_CONFIG
from utils.db_utils import connect_to_db, close_connections

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

        # Iterate over all database configurations in SERVER_CONFIG
        for config_name, config in SERVER_CONFIG.items():
            print(f"Checking replica status for {config_name}... (replica.py)")

            try:
                # Check replica status for the current configuration
                delayed_status = check_replica_status(config)  # Assuming this function uses the database connection
                
                # Extract the pg_host and other details
                pg_host = delayed_status.get("pg_host", "Unknown")
                statuses.append({
                    "name": pg_host,
                    "status": delayed_status.get("status", "Unknown"),
                    "delay": delayed_status.get("delay", "N/A")
                })
            except Exception as e:
                print(f"Error checking replica status for {config_name}: {str(e)} (replica.py)")
                statuses.append({
                    "name": config.get("pg_host", "Unknown"),
                    "status": "error",
                    "error": str(e)
                })

        # Return the array with the replica statuses
        return jsonify(statuses)

    except Exception as e:
        print(f"Error fetching replica statuses: {str(e)} (replica.py)")
        return jsonify({"status": "error", "error": str(e)}), 500

# @replica_blueprint.route("/replica/manage", methods=["POST"])
# def manage_replica():
#     """
#     Manage replication for the delayed database (pause or resume) via a single endpoint.
    
#     Expected JSON Payload:
#     {
#         "action": "pause" or "resume"
#     }
#     """
    
#     try:
#         # Get the action from the JSON payload
#         print("Receiving action from the client request... (replica.py)")
#         data = request.get_json()
#         action = data.get("action")
#         server = data.get("name")
        
#         if not action:
#             print("Missing required parameters in the request. (replica.py)")
#             return jsonify({"status": "error", "error": "Missing required parameters."}), 400

#         print(f"Action received: {action}, server received: {server}")

#         # Connect to the delayed replica's database
#         print("Attempting to establish SSH tunnel and connect to the delayed replica database... (replica.py)")
#         # conn = connect_to_db(DATABASE_CONFIG, server)
#         conn = connect_to_db(DATABASE_CONFIG)
        
#         # Call the manage_replication function with the connection and the action
#         print(f"Managing replication with action: {action} (replica.py)")
#         result = manage_replication(DATABASE_CONFIG, action)  # Assuming this function can accept a connection

#         # Close the connection and tunnel after the operation
#         print("Closing the database connection and SSH tunnel... (replica.py)")
#         close_connections(conn)
        
#         return jsonify(result)
    
#     except Exception as e:
#         print(f"Error managing replica: {str(e)} (replica.py)")
#         return jsonify({"status": "error", "error": str(e)}), 500

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
        server_name = data.get("name")
        
        if not action or not server_name:
            print("Missing required parameters in the request. (replica.py)")
            return jsonify({"status": "error", "error": "Missing required parameters (action or name)."}), 400

        print(f"Action received: {action}, server name (pg_host) received: {server_name}")

        # Loop through SERVER_CONFIG to find the matching configuration by pg_host
        selected_config = None
        for config_name, config in SERVER_CONFIG.items():
            if config.get("pg_host") == server_name:
                selected_config = config
                break

        if not selected_config:
            print(f"No matching configuration found for server name (pg_host): {server_name} (replica.py)")
            return jsonify({"status": "error", "error": f"No configuration found for server: {server_name}"}), 400

        print(f"Found matching configuration: {selected_config}")

        # Connect to the specified server's database
        print("Attempting to establish SSH tunnel and connect to the specified replica database... (replica.py)")
        conn = connect_to_db(selected_config)
        
        # Call the manage_replication function with the selected configuration and the action
        print(f"Managing replication with action: {action} for server: {server_name} (replica.py)")
        result = manage_replication(selected_config, action)

        # Close the connection and tunnel after the operation
        print("Closing the database connection and SSH tunnel... (replica.py)")
        close_connections(conn)
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Error managing replica: {str(e)} (replica.py)")
        return jsonify({"status": "error", "error": str(e)}), 500