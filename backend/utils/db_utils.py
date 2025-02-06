import psycopg2
import time
from psycopg2 import OperationalError
from flask import Blueprint, jsonify, request
import paramiko
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def connect_via_ssh(host, ssh_user, ssh_password):
    """
    Establishes an SSH connection to the remote server.
    """
    try:
        logging.info("Establishing SSH connection...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=ssh_user, password=ssh_password)
        logging.info("SSH connection established.")
        return ssh
    except Exception as e:
        logging.error(f"Error connecting to SSH: {str(e)}")
        raise

def switch_to_root(shell, ssh_password):
    """
    Switches to the root user via sudo in the SSH session.
    """
    logging.info("Running sudo to switch to root user...")
    shell.send("sudo -i\n")
    time.sleep(1)  # Wait for sudo to prompt for password
    shell.send(ssh_password + "\n")  # Enter sudo password
    time.sleep(1)  # Wait for the command to execute

def switch_to_enterprisedb(shell):
    """
    Switches to the 'enterprisedb' user in the SSH session.
    """
    logging.info("Switching to 'enterprisedb' user...")
    shell.send("su - enterprisedb\n")
    time.sleep(1)  # Wait for the 'enterprisedb' user prompt
    
def up_to_enterprisedb(ssh_host, ssh_user, ssh_password):
    ssh = connect_via_ssh(ssh_host, ssh_user, ssh_password)
    shell = ssh.invoke_shell()
    switch_to_root(shell, ssh_password)
    switch_to_enterprisedb(shell)
    return ssh, shell

def switch_to_server(shell, pg_host):
    logging.info("Switching to 'server'...")
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

def connect(config):
    """
    Establish a connection to the PostgreSQL database using a configuration dictionary.
    """
    try:
        pg_host = config.get("pg_host", "localhost")  # Default to 'localhost' if not provided
        logging.info(f"Attempting to connect to the database: {config['database']} at {pg_host}:{config.get('port', 5444)}")
       
        # Establish the PostgreSQL connection
        conn = psycopg2.connect(
            host=pg_host,
            user=config["user"],
            password=config["pg_password"],
            dbname=config["database"],
            port=config.get("port", 5444)  # Default to 5444 if port is not in config
        )
        logging.info("Successfully connected to the database.")
        return conn
    except OperationalError as e:
        logging.error(f"Error while connecting to the database: {e}")
        raise e
   
def connect_to_db(shell, DATABASE_CONFIG):
    logging.info("Starting SSH connection to the database server.")
   
    data = DATABASE_CONFIG
    logging.info(f"Request payload: {data}")
 
    # Extract parameters from the request
    ssh_host = data.get("ssh_host")
    ssh_user = data.get("ssh_user")
    ssh_password = data.get("ssh_password")
    pg_host = data.get("pg_host")
    port = data.get("port")
    user = data.get("user")
    database = data.get("database")
    pg_password = data.get("pg_password")
    
    switch_to_server(shell, pg_host)
 
    logging.info("SSH connection successful. Now connecting to the database...")
 
    # After SSH login, connect to the PostgreSQL database
    conn = connect(DATABASE_CONFIG)
 
    if isinstance(conn, str) and conn.startswith("error"):
        logging.error(f"Error during database connection: {conn}")
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
            logging.info("Closing the database connection...")
            conn.close()
            logging.info("Database connection closed successfully.")
    except Exception as e:
        logging.error(f"Error closing the database connection: {str(e)}")