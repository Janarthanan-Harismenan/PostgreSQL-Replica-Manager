from flask import Blueprint, jsonify
from utils.ssh_utils import ssh_connect_and_execute
from utils.db_utils import connect_to_db, query_db
from config import DATABASE_CONFIG

connect_blueprint = Blueprint('connect', __name__)

@connect_blueprint.route('/', methods=['GET'])



def connect():
    print("Starting SSH connection to 172.20.224.175 (connect.py)")
    
    # First SSH login to 172.20.224.175
    output1, error1 = ssh_connect_and_execute(
        DATABASE_CONFIG['ssh_host'],
        DATABASE_CONFIG['ssh_user'],
        DATABASE_CONFIG['ssh_password'],
        # f"ssh {DATABASE_CONFIG['ssh_user']}@{DATABASE_CONFIG['pg_host']}"
        
        None
    )

    if error1:
        print(f"Error during SSH connection to 172.20.224.175: {error1} (connect.py)")
        return jsonify({"error": error1})

    print("SSH connection to 172.20.224.175 successful. Now logging into 172.20.224.149 (connect.py)")

    # Then SSH login to 172.20.224.149 after logging into 172.20.224.175
    output2, error2 = ssh_connect_and_execute(
        DATABASE_CONFIG['pg_host'],
        DATABASE_CONFIG['ssh_user'],
        DATABASE_CONFIG['ssh_password'],
        # f"ssh {DATABASE_CONFIG['ssh_user']}@{DATABASE_CONFIG['pg_host']}"
        None
    )

    if error2:
        print(f"Error during SSH connection to 172.20.224.149: {error2} (connect.py)")
        return jsonify({"error": error2})

    print("SSH connection to 172.20.224.149 successful. Now connecting to the database. (connect.py)")

    # After SSH login, connect to the PostgreSQL database
    conn = connect_to_db(DATABASE_CONFIG)

    if isinstance(conn, str) and conn.startswith("error"):
        print(f"Error during database connection: {conn} (connect.py)")
        return jsonify({"error": conn})

    print("Database connection successful. Executing the query. (connect.py)")

    # Execute the query and get the result
    db_output = query_db(conn)

    if isinstance(db_output, str) and db_output.startswith("error"):
        print(f"Error during query execution: {db_output} (connect.py)")
        return jsonify({"error": db_output})

    print(f"Query result: {db_output} ")
    return jsonify({"message": "Connected to the database", "db_version": db_output})
