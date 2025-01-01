from flask import Blueprint, jsonify, request
from utils.replica_manager import check_replica_status, manage_replication
from config import DATABASE_CONFIG
from utils.db_utils import connect_to_db, close_connections

# Flask blueprint
replica_blueprint = Blueprint("replica", __name__)

# @replica_blueprint.route("/replica-status", methods=["GET"])
# def get_replica_status():
#     """
#     Fetch the replication statuses for the primary and delayed replicas.
#     """
#     try:
#         # Get replica status for the delayed replica by establishing an SSH tunnel and connecting to DB
#         print("Attempting to establish SSH tunnel and connect to the delayed replica database... (replica.py)")
#         # conn = connect_to_db(DATABASE_CONFIG)
        
#         # Call the existing replica status function (assuming it uses the established connection)
#         print("Checking the replica status for the delayed replica... (replica.py)")
#         statuses = {
#             "delayed": check_replica_status(DATABASE_CONFIG)  # Assuming this function uses the database connection
#         }
        
#         return jsonify(statuses)
    
#     except Exception as e:
#         print(f"Error fetching replica status: {str(e)} (replica.py)")
#         return jsonify({"status": "error", "error": str(e)}), 500

@replica_blueprint.route("/replica-status", methods=["GET"])
def get_replica_status():
    """
    Fetch the replication statuses for the primary and delayed replicas.
    """
    try:
        # Get replica status for the delayed replica by establishing an SSH tunnel and connecting to DB
        print("Attempting to establish SSH tunnel and connect to the delayed replica database... (replica.py)")
        
        # Call the existing replica status function
        print("Checking the replica status for the delayed replica... (replica.py)")
        delayed_status = check_replica_status(DATABASE_CONFIG)  # Assuming this function uses the database connection
        
        # Get the pg_host from the delayed replica status
        pg_host = delayed_status.get("pg_host", "Unknown")
        
        # Define the dummy data for different pg_hosts
        # if pg_host == "172.20.224.149":
        #     replica_name = "10 mins delay"
        # elif pg_host == "172.20.224.150":
        #     replica_name = "2 hrs delay"
        # elif pg_host == "172.20.224.151":
        #     replica_name = "24 hrs delay"
        # else:
        #     replica_name = "Unknown delay"
        
        # Return the array with the replica status
        statuses = [
            {
                "name": pg_host,
                "status": delayed_status.get("status", "Unknown"),
                "delay": delayed_status.get("delay", "N/A")
            }
        ]
        
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
        conn = connect_to_db(DATABASE_CONFIG)
        
        # Call the manage_replication function with the connection and the action
        print(f"Managing replication with action: {action} (replica.py)")
        result = manage_replication(DATABASE_CONFIG, action)  # Assuming this function can accept a connection

        # Close the connection and tunnel after the operation
        print("Closing the database connection and SSH tunnel... (replica.py)")
        close_connections(conn)
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Error managing replica: {str(e)} (replica.py)")
        return jsonify({"status": "error", "error": str(e)}), 500