import psycopg2
import time
from psycopg2 import OperationalError
from flask import Blueprint, jsonify, request
import paramiko
import re
 
def connect_via_ssh(host, ssh_user, ssh_password):
    """
    Establishes an SSH connection to the remote server.
    """
    try:
        print("Establishing SSH connection... (pg_catcheck.py)")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=ssh_user, password=ssh_password)
        print("SSH connection established. (pg_catcheck.py)")
        return ssh
    except Exception as e:
        print(f"Error connecting to SSH: {str(e)} (pg_catcheck.py)")
        raise
 
def switch_to_root(shell, ssh_password):
    """
    Switches to the root user via sudo in the SSH session.
    """
    print("Running sudo to switch to root user... (pg_catcheck.py)")
    shell.send("sudo -i\n")
    time.sleep(1)  # Wait for sudo to prompt for password
    shell.send(ssh_password + "\n")  # Enter sudo password
    time.sleep(1)  # Wait for the command to execute
 
def switch_to_enterprisedb(shell):
    """
    Switches to the 'enterprisedb' user in the SSH session.
    """
    print("Switching to 'enterprisedb' user... (pg_catcheck.py)")
    shell.send("su - enterprisedb\n")
    time.sleep(1)  # Wait for the 'enterprisedb' user prompt
    
def up_to_enterprisedb(ssh_host, ssh_user, ssh_password):
    ssh = connect_via_ssh(ssh_host, ssh_user, ssh_password)
    shell = ssh.invoke_shell()
    switch_to_root(shell, ssh_password)
    switch_to_enterprisedb(shell)
    return shell
 
def switch_to_server(shell, pg_host):
    print("Switching to 'server' (pg_catcheck.py)")
    command = f"ssh enterprisedb@{pg_host}\n"
    shell.send(command)
    time.sleep(1)  # Wait for the 'enterprisedb' user prompt
 
def flush_shell_output(shell):
    """
    Flushes any existing output in the shell buffer to ensure clean output for the next command.
    """
    output = ""
    while shell.recv_ready():
        output += shell.recv(1024).decode()
    return output
 
def list_databases_via_shell(shell,port):
    """
    Lists available databases on the PostgreSQL server via an interactive shell.
    """
    try:
        print("Flushing shell buffer... (pg_catcheck.py)")
        flush_shell_output(shell)  # Clear any previous output in the shell
 
        print("Listing available databases (pg_catcheck.py)")
        command = f"psql -p {port} -lqt | cut -d \\| -f 1 | tr -d ' ' | grep -v '^$'\n"
        shell.send(command)
        print("command: ",command)
        time.sleep(2)  # Allow some time for the command to execute and output to be generated
 
        # Capture the output for this command only
        output = ""
        while shell.recv_ready():
            output += shell.recv(1024).decode()
 
        # Process the output to filter only valid database names
        lines = output.split("\n")
        databases = []
        for line in lines:
            line = line.strip()
            if re.match(r"^[a-zA-Z0-9_]+$", line):  # Match valid database names
                databases.append(line)
 
        print(f"Databases found: {databases} (pg_catcheck.py)")
        return databases
 
    except Exception as e:
        print(f"Error while listing databases: {str(e)} (pg_catcheck.py)")
        return {"status": "error", "message": str(e)} 
 
def connect(config):
    """
    Establish a connection to the PostgreSQL database using a configuration dictionary.
    """
    try:
        # Use 'pg_host' instead of 'host'
        pg_host = config.get("pg_host", "localhost")  # Default to 'localhost' if not provided
        print(f"Attempting to connect to the database: {config['database']} at {pg_host}:{config.get('port', 5444)}")
       
        # Establish the PostgreSQL connection
        conn = psycopg2.connect(
            host=pg_host,  # Corrected key
            user=config["user"],
            password=config["pg_password"],  # Corrected key for PostgreSQL password
            dbname=config["database"],
            port=config.get("port", 5444)  # Default to 5444 if port is not in config
        )
        print("Successfully connected to the database.")
        return conn
    except OperationalError as e:
        print(f"Error while connecting to the database: {e}")
        raise e
   
def connect_to_db(shell, DATABASE_CONFIG):
    print("Starting SSH connection to 172.20.224.175 (connect.py)")
   
    data = DATABASE_CONFIG
    print(f"Request payload: {data} (catcheck.py)")
 
    # Extract parameters from the request
    ssh_host = data.get("ssh_host")
    ssh_user = data.get("ssh_user")
    ssh_password = data.get("ssh_password")
    pg_host = data.get("pg_host")
    port = data.get("port")
    user = data.get("user")
    database = data.get("database")
    pg_password = data.get("pg_password")
    
    # shell = up_to_enterprisedb(ssh_host, ssh_user, ssh_password)
    switch_to_server(shell, pg_host)
 
    print("SSH connection to 172.20.224.149 successful. Now connecting to the database...")
 
    # After SSH login, connect to the PostgreSQL database
    conn = connect(DATABASE_CONFIG)
 
    if isinstance(conn, str) and conn.startswith("error"):
        print(f"Error during database connection: {conn} (connect.py)")
        return jsonify({"error": conn})
   
    return conn

def close_connections(conn):
    """
    Close the database connection safely.
 
    Args:
        conn: The database connection object to be closed.
    """
    try:
        if conn:
            print("Closing the database connection... (utils.db_utils.py)")
            conn.close()
            print("Database connection closed successfully. (utils.db_utils.py)")
    except Exception as e:
        print(f"Error closing the database connection: {str(e)} (utils.db_utils.py)")