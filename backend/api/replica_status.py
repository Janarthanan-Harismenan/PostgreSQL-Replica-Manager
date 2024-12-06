from flask import Blueprint, jsonify
from utils.db_utils import check_replica_status
from config import REPLICAS

replica_blueprint = Blueprint('replica', __name__)

@replica_blueprint.route('/replica-status', methods=['GET'])
def get_replica_status():
    status_list = []
    for replica in REPLICAS:
        status = check_replica_status(replica['port'])
        status['port'] = replica['port']
        status_list.append(status)
    return jsonify(status_list)
