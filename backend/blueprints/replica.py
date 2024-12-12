from flask import Blueprint, jsonify, request
from utils.replica_manager import check_replica_status, manage_replication
from config import DATABASE_CONFIG
from utils.db_utils import connect_to_db

# Flask blueprint
replica_blueprint = Blueprint("replica", __name__)

@replica_blueprint.route("/replica-status", methods=["GET"])
def get_replica_status():
    """
    Fetch the replication statuses for the primary and delayed replicas.
    """
    try:
        # Get replica status for the delayed replica by establishing an SSH tunnel and connecting to DB
        print("Attempting to establish SSH tunnel and connect to the delayed replica database... (replica.py)")
        conn = connect_to_db(DATABASE_CONFIG)
        
        # Call the existing replica status function (assuming it uses the established connection)
        print("Checking the replica status for the delayed replica... (replica.py)")
        statuses = {
            "delayed": check_replica_status(conn)  # Assuming this function uses the database connection
        }
        
        return jsonify(statuses)
    
    except Exception as e:
        print(f"Error fetching replica status: {str(e)} (replica.py)")
        return jsonify({"status": "error", "error": str(e)}), 500

@replica_blueprint.route("/replica/manage", methods=["POST"])
def manage_replica():
    """
    Manage replication for the delayed database (pause or resume) via a single endpoint.
    
    Expected JSON Payload:
    {
        "action": "pause" or "resume"
    }
    """
    
    try:
        # Get the action from the JSON payload
        print("Receiving action from the client request... (replica.py)")
        data = request.get_json()
        action = data.get("action")
        
        if not action:
            print("Missing 'action' parameter in the request. (replica.py)")
            return jsonify({"status": "error", "error": "Missing 'action' parameter."}), 400

        print(f"Action received: {action}")

        # Connect to the delayed replica's database
        print("Attempting to establish SSH tunnel and connect to the delayed replica database... (replica.py)")
        conn, tunnel = connect_to_db(DATABASE_CONFIG)
        
        # Call the manage_replication function with the connection and the action
        print(f"Managing replication with action: {action} (replica.py)")
        result = manage_replication(conn, action)  # Assuming this function can accept a connection

        # Close the connection and tunnel after the operation
        print("Closing the database connection and SSH tunnel... (replica.py)")
        close_connections(conn, tunnel)
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Error managing replica: {str(e)} (replica.py)")
        return jsonify({"status": "error", "error": str(e)}), 500