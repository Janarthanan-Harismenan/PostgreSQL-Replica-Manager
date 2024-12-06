import subprocess
from flask import Blueprint, request, jsonify

wal_blueprint = Blueprint('wal', __name__)

@wal_blueprint.route('/search-wal', methods=['POST'])
def search_wal():
    try:
        data = request.json
        keyword = data.get('keyword')
        number_of_files = data.get('number_of_files')

        # Example command to inspect WAL files
        result = subprocess.run(
            ['pg_waldump', '-n', str(number_of_files), '-p', '/var/lib/postgresql/data/pg_wal'],
            capture_output=True,
            text=True
        )

        output = result.stdout
        filtered_output = [line for line in output.split('\n') if keyword in line]
        return jsonify({'status': 'success', 'filtered_wal': filtered_output})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
