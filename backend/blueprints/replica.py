from flask import Blueprint, jsonify, request
from utils.db_utils import check_replica_status, pause_replication, resume_replication
from config import DATABASE_CONFIG

replica_blueprint = Blueprint("replica", __name__)


@replica_blueprint.route("/replica-status", methods=["GET"])
def get_replica_status():
    """
    Fetch the replication statuses for the primary and delayed replicas.
    """
    statuses = {
        "primary": check_replica_status(DATABASE_CONFIG["primary"]),
        "delayed": check_replica_status(DATABASE_CONFIG["delayed"]),
    }
    return jsonify(statuses)


@replica_blueprint.route("/replica/pause", methods=["POST"])
def pause_replica():
    """
    Pause replication for the delayed database.
    """
    result = pause_replication(DATABASE_CONFIG["delayed"])
    return jsonify(result)


@replica_blueprint.route("/replica/resume", methods=["POST"])
def resume_replica():
    """
    Resume replication for the delayed database.
    """
    result = resume_replication(DATABASE_CONFIG["delayed"])
    return jsonify(result)
