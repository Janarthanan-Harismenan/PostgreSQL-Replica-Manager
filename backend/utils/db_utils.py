import psycopg2
from psycopg2 import OperationalError
from flask import Blueprint, jsonify, request

# def connect_to_db(host, user, password, dbname, port=5444):
#     """
#     Establish a connection to the PostgreSQL database.
#     """
#     try:
#         print(f"Attempting to connect to the database: {dbname} at {host}:{port}")
        
#         # Establish PostgreSQL connection
#         conn = psycopg2.connect(
#             host=host,
#             user=user,
#             password=password,
#             dbname=dbname,
#             port=port
#         )
#         print("Successfully connected to the database.")
#         return conn
#     except OperationalError as e:
#         print(f"Error while connecting to the database: {e}")
#         return str(e)

def connect_to_db(config):
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

def query_db(conn, query="SELECT version();"):
    """
    Execute a query on the connected PostgreSQL database and return the result.
    """
    try:
        print(f"Executing query: {query}")
        
        cursor = conn.cursor()
        cursor.execute(query)
        
        result = cursor.fetchone()
        print(f"Query result: {result}")
        
        cursor.close()
        return result
    except Exception as e:
        print(f"Error executing query: {e}")
        return str(e)
