import subprocess
from flask import Blueprint, jsonify

catalog_blueprint = Blueprint('catalog', __name__)

@catalog_blueprint.route('/pg-catcheck', methods=['GET'])
def run_pg_catcheck():
    try:
        result = subprocess.run(['pg_catcheck', '-U', 'youruser', '-d', 'yourdb'], capture_output=True, text=True)
        report = result.stdout
        return jsonify({'status': 'success', 'report': report})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
