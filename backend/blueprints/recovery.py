import subprocess
from flask import Blueprint, request, jsonify
from utils.recovery_manager import recover_from_delay, promote_to_primary
from config import DATABASE_CONFIG

# Define the recovery blueprint
recover_blueprint = Blueprint('recovery', __name__)

@recover_blueprint.route('/recover', methods=['POST'])
def recover_replica():
    """
    Recover the delayed replica and promote it to primary.
    """
    data = request.json
    crash_time = data.get("crash_time")
    database = data.get("database")
 
    if not crash_time:
        return jsonify({"status": "error", "error": "Missing 'crash_time' in request body."}), 400
    if not database or database not in DATABASE_CONFIG:
        return jsonify({"status": "error", "error": "Invalid or missing 'database' in request body."}), 400

    # Get the configuration for the specified delayed database
    config = DATABASE_CONFIG[database]

    try:
        # First, attempt to recover from the delay (this could be your custom recovery logic)
        recovery_result = recover_from_delay(config, crash_time)

        if recovery_result.get("status") != "success":
            return jsonify({"status": "error", "message": "Failed to recover replica from delay."}), 500

        # Assuming you now want to rewind and promote the replica as in the previous logic
        target_wal = recovery_result.get('target_wal')  # Modify this according to your needs
        target_time = crash_time  # Use crash_time or specify another time

        # Run pg_rewind to recover the standby to the specified WAL
        result = subprocess.run(
            ['pg_rewind', '--source-server="host=localhost port=5432 user=youruser dbname=yourdb"',
             '--target-wal=' + target_wal],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            # After successful recovery, promote the replica to primary
            promote_result = subprocess.run(
                ['pg_ctl', 'promote', '-D', '/var/lib/postgresql/data/standby_directory'],
                capture_output=True,
                text=True
            )

            if promote_result.returncode == 0:
                return jsonify({'status': 'success', 'message': 'Replica recovered and promoted.'})
            else:
                return jsonify({'status': 'error', 'message': promote_result.stderr}), 500
        else:
            return jsonify({'status': 'error', 'message': result.stderr}), 500

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500