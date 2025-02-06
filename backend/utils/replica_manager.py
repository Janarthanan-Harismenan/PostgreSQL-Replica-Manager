import csv
import logging
import time
import requests
from utils.db_utils import connect_to_db
from psycopg2.extras import RealDictCursor
import os
from config import MAX_FILE_SIZE_MB, INTERVAL_SECONDS

# Configuration for periodic API calls
API_URL = "http://localhost:5000/api/replica-status"
CSV_FILE = "static/replica_status.csv"  # Save file in static directory

def get_last_update_time(conn):
    """
    Get the delay time from the database for the delayed replica.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        try:
            logging.info("Executing query to fetch delay time.")
            cursor.execute("""
                SELECT now() AS current_time,
                       pg_last_xact_replay_timestamp() AS replay_time,
                       now() - pg_last_xact_replay_timestamp() AS delay_time
                """)
            result = cursor.fetchone()
            if result and result['delay_time']:
                logging.info(f"Current Time: {result['current_time']}, Replay Time: {result['replay_time']}, Delay Time: {result['delay_time']}")
                return result['delay_time']
        except Exception as e:
            logging.error(f"Error fetching delay time: {e}")
        return None

def check_replica_status(shell, config):
    """
    Check the replication status of the database and return the host address.
    """
    try:
        logging.info("Checking replica status.")
        conn = connect_to_db(shell, config)

        # Fetch the host address of the database
        with conn.cursor() as cursor:
            cursor.execute("SELECT current_setting('server_version');")
            result = cursor.fetchone()
            pg_host = conn.info.host  # Extracting the host address

        delay_time = get_last_update_time(conn)
        conn.close()

        return {
            "pg_host": pg_host,
            "delay": str(delay_time) if delay_time else "N/A"
        }
    except Exception as e:
        logging.error(f"Error checking replica status: {e}")
        return {
            "pg_host": None,
            "delay": None,
            "error": str(e)
        }

def check_replica_paused(shell, config):
    """
    Check if the replication for the delayed database is paused.
    """
    try:
        logging.info("Checking if replica is paused.")
        conn = connect_to_db(shell, config)
        with conn.cursor() as cursor:
            cursor.execute("SELECT pg_is_wal_replay_paused();")
            result = cursor.fetchone()
            is_paused = result[0] if result else False
            logging.info(f"WAL replay paused: {is_paused}")
            return is_paused
    except Exception as e:
        logging.error(f"Error checking if replica is paused: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        if conn:
            conn.close()

def manage_replication(shell, config, action):
    """
    Manage replication for the delayed database (pause or resume).
   
    Args:
        config (dict): Database connection configuration.
        action (str): The action to perform, either 'pause' or 'resume'.
   
    Returns:
        dict: Status and result of the action.
    """
    try:
        logging.info(f"Managing replication with action: {action}")
        if action not in ["pause", "resume"]:
            logging.error("Invalid action received.")
            return {"status": "error", "error": "Invalid action. Use 'pause' or 'resume'."}
       
        is_paused = check_replica_paused(shell, config)
        if action == "pause" and is_paused:
            logging.info("Replica is already paused.")
            return {"status": "already paused"}
        if action == "resume" and not is_paused:
            logging.info("Replica is already resumed.")
            return {"status": "already resumed"}
       
        conn = connect_to_db(shell, config)
        with conn.cursor() as cursor:
            if action == "pause":
                logging.info("Pausing WAL replay.")
                cursor.execute("SELECT pg_wal_replay_pause();")
            elif action == "resume":
                logging.info("Resuming WAL replay.")
                cursor.execute("SELECT pg_wal_replay_resume();")
            conn.commit()
        conn.close()
       
        if action == "pause" and check_replica_paused(shell, config):
            logging.info("WAL replay successfully paused.")
            return {"status": "paused"}
        if action == "resume" and not check_replica_paused(shell, config):
            logging.info("WAL replay successfully resumed.")
            return {"status": "resumed"}
        logging.error(f"Failed to {action} replication.")
        return {"status": "error", "error": f"Failed to {action} replication."}
    except Exception as e:
        logging.error(f"Error managing replication: {e}")
        return {"status": "error", "error": str(e)}

def fetch_replica_status():
    """
    Fetch the replication statuses from the API and save to CSV.
    """
    while True:
        try:
            logging.info("Fetching replica status...")
            response = requests.get(API_URL, timeout=1000)
            if response.status_code == 200:
                data = response.json()
                save_to_csv(data)
                check_file_size()
            else:
                logging.warning(f"Failed to fetch data. Status code: {response.status_code}")
        except Exception as e:
            logging.error(f"Error during API call: {e}")
       
        logging.info(f"Sleeping for {INTERVAL_SECONDS} seconds...")
        time.sleep(INTERVAL_SECONDS)

def save_to_csv(data):
    """
    Save the data to a CSV file.
    """
    file_exists = os.path.exists(CSV_FILE)
    try:
        # Make sure the directory exists
        os.makedirs(os.path.dirname(CSV_FILE), exist_ok=True)

        with open(CSV_FILE, mode="a", newline="") as file:
            writer = csv.writer(file)
           
            # Write header only if the file is being created
            if not file_exists:
                writer.writerow(["name", "delay_name", "delay", "timestamp"])
           
            # Write rows of data
            for entry in data:
                writer.writerow([entry["name"], entry["delay_name"], entry.get("delay", "N/A"), time.strftime("%Y-%m-%d %H:%M:%S")])
       
        logging.info(f"Data saved to CSV at: {os.path.abspath(CSV_FILE)}")
    except Exception as e:
        logging.error(f"Error writing to CSV: {str(e)}")

def check_file_size():
    """
    Check if the CSV file exceeds the maximum size and delete if necessary.
    """
    try:
        if os.path.exists(CSV_FILE):
            file_size_mb = os.path.getsize(CSV_FILE) / (1024 * 1024)  # Convert bytes to MB
            if file_size_mb > MAX_FILE_SIZE_MB:
                logging.warning(f"File size exceeded {MAX_FILE_SIZE_MB}MB. Deleting {CSV_FILE}.")
                os.remove(CSV_FILE)
    except Exception as e:
        logging.error(f"Error checking/deleting file: {e}")