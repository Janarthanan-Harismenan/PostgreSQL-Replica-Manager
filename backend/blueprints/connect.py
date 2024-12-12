from flask import Blueprint, jsonify
from utils.ssh_utils import ssh_connect, ssh_execute_command
from utils.db_utils import connect_to_db, query_db
from config import DATABASE_CONFIG

connect_blueprint = Blueprint('connect', __name__)

@connect_blueprint.route('/', methods=['GET'])
def connect():
    print("Starting SSH connection to 172.20.224.175 (connect.py)")

    # First SSH login to 172.20.224.175
    ssh_client, error1 = ssh_connect(DATABASE_CONFIG['ssh_host'], DATABASE_CONFIG['ssh_user'], DATABASE_CONFIG['ssh_password'])

    if error1:
        print(f"Error during SSH connection to 172.20.224.175: {error1} (connect.py)")
        return jsonify({"error": error1})

    print("SSH connection to 172.20.224.175 successful. Elevating to root user...")

    # Elevate to root user with sudo
    output_sudo, error_sudo = ssh_execute_command(ssh_client, "sudo -i", password=DATABASE_CONFIG['ssh_password'])

    if error_sudo:
        print(f"Error during sudo elevation: {error_sudo} (connect.py)")
        return jsonify({"error": error_sudo})

    print("Elevated to root user. Switching to enterprisedb user...")
    
    # Switch to enterprisedb user with su
    output_su, error_su = ssh_execute_command(ssh_client, DATABASE_CONFIG['ssh_password'])

    if error_su:
        print(f"Error during su to enterprisedb user: {error_su} (connect.py)")
        return jsonify({"error": error_su})

    # Switch to enterprisedb user with su
    output_su, error_su = ssh_execute_command(ssh_client, "su - enterprisedb")

    if error_su:
        print(f"Error during su to enterprisedb user: {error_su} (connect.py)")
        return jsonify({"error": error_su})

    print("Switched to enterprisedb user. Now logging into 172.20.224.149...")

    # Then SSH login to 172.20.224.149 after logging into 172.20.224.175
    output2, error2 = ssh_execute_command(ssh_client, f"ssh {DATABASE_CONFIG['ssh_user']}@{DATABASE_CONFIG['pg_host']}")

    if error2:
        print(f"Error during SSH connection to 172.20.224.149: {error2} (connect.py)")
        return jsonify({"error": error2})

    print("SSH connection to 172.20.224.149 successful. Now connecting to the database...")

    # After SSH login, connect to the PostgreSQL database
    conn = connect_to_db(DATABASE_CONFIG)

    if isinstance(conn, str) and conn.startswith("error"):
        print(f"Error during database connection: {conn} (connect.py)")
        return jsonify({"error": conn})

    print("Database connection successful. Executing the query...")

    # Execute the query and get the result
    db_output = query_db(conn)

    if isinstance(db_output, str) and db_output.startswith("error"):
        print(f"Error during query execution: {db_output} (connect.py)")
        return jsonify({"error": db_output})

    print(f"Query result: {db_output}")
    return jsonify({"message": "Connected to the database", "db_version": db_output})
