from flask import Blueprint, jsonify, request
from utils.replica_manager import check_replica_status, manage_replication
from config import DATABASE_CONFIG

replica_blueprint = Blueprint("replica", __name__)

@replica_blueprint.route("/replica-status", methods=["GET"])
def get_replica_status():
    """
    Fetch the replication statuses for the primary and delayed replicas.
    """
    statuses = {
        # "primary": check_replica_status(DATABASE_CONFIG["primary"]),
        "delayed": check_replica_status(DATABASE_CONFIG["delayed"]),
    }
    return jsonify(statuses)


@replica_blueprint.route("/replica/manage", methods=["POST"])
def manage_replica():
    """
    Manage replication for the delayed database (pause or resume) via a single endpoint.
    
    Expected JSON Payload:
    {
        "action": "pause" or "resume"
    }
    """
    
    print(9)
    
    try:
        data = request.get_json()
        action = data.get("action")
        
        if not action:
            return jsonify({"status": "error", "error": "Missing 'action' parameter."}), 400
        
        result = manage_replication(DATABASE_CONFIG["delayed"], action)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500