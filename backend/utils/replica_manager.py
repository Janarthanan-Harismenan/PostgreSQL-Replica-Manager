from utils.db_utils import connect_to_db
from psycopg2.extras import RealDictCursor

def get_last_update_time(conn):
    """
    Get the delay time from the database for the delayed replica.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        try:
            print("(replica_manager.py) Executing query to fetch delay time.")
            cursor.execute("""
                SELECT now() AS current_time, 
                       pg_last_xact_replay_timestamp() AS replay_time,
                       now() - pg_last_xact_replay_timestamp() AS delay_time
                """)
            result = cursor.fetchone()
            if result and result['delay_time']:
                print(f"(replica_manager.py) Current Time: {result['current_time']}")
                print(f"(replica_manager.py) Replay Time: {result['replay_time']}")
                print(f"(replica_manager.py) Delay Time: {result['delay_time']}")
                return result['delay_time']
        except Exception as e:
            print(f"(replica_manager.py) Error fetching delay time: {e}")
        return None
    
def check_replica_status(config):
    """
    Check the replication status of the database and return the host address.
    """
    try:
        print("(replica_manager.py) Checking replica status.")
        conn = connect_to_db(config)
        
        # Fetch the host address of the database
        with conn.cursor() as cursor:
            cursor.execute("SELECT current_setting('server_version');")
            result = cursor.fetchone()
            pg_host = conn.info.host  # Extracting the host address
        
        delay_time = get_last_update_time(conn)
        conn.close()
        
        if check_replica_paused(config):
            print(f"(replica_manager.py) Replica is paused at host {pg_host}.")
            return {
                "status": "paused",
                "delay": str(delay_time) if delay_time else "N/A",
                "pg_host": pg_host,
                "error": None
            }
        else:
            print(f"(replica_manager.py) Replica is running at host {pg_host}.")
            return {
                "status": "running",
                "delay": str(delay_time) if delay_time else "N/A",
                "pg_host": pg_host,
                "error": None
            }
    except Exception as e:
        print(f"(replica_manager.py) Error checking replica status: {e}")
        return {
            "status": "stopped",
            "delay": None,
            "error": str(e),
            "pg_host": None
        }

def check_replica_paused(config):
    """
    Check if the replication for the delayed database is paused.
    """
    try:
        print("(replica_manager.py) Checking if replica is paused.")
        conn = connect_to_db(config)
        with conn.cursor() as cursor:
            cursor.execute("SELECT pg_is_wal_replay_paused();")
            result = cursor.fetchone()
            is_paused = result[0] if result else False
            print(f"(replica_manager.py) WAL replay paused: {is_paused}")
            return is_paused
    except Exception as e:
        print(f"(replica_manager.py) Error checking if replica is paused: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        if conn:
            conn.close()

def manage_replication(config, action):
    """
    Manage replication for the delayed database (pause or resume).
    
    Args:
        config (dict): Database connection configuration.
        action (str): The action to perform, either 'pause' or 'resume'.
    
    Returns:
        dict: Status and result of the action.
    """
    try:
        print(f"(replica_manager.py) Managing replication with action: {action}")
        if action not in ["pause", "resume"]:
            print("(replica_manager.py) Invalid action received.")
            return {"status": "error", "error": "Invalid action. Use 'pause' or 'resume'."}
        
        is_paused = check_replica_paused(config)
        if action == "pause" and is_paused:
            print("(replica_manager.py) Replica is already paused.")
            return {"status": "already paused"}
        if action == "resume" and not is_paused:
            print("(replica_manager.py) Replica is already resumed.")
            return {"status": "already resumed"}
        
        conn = connect_to_db(config)
        with conn.cursor() as cursor:
            if action == "pause":
                print("(replica_manager.py) Pausing WAL replay.")
                cursor.execute("SELECT pg_wal_replay_pause();")
            elif action == "resume":
                print("(replica_manager.py) Resuming WAL replay.")
                cursor.execute("SELECT pg_wal_replay_resume();")
            conn.commit()
        conn.close()
        
        if action == "pause" and check_replica_paused(config):
            print("(replica_manager.py) WAL replay successfully paused.")
            return {"status": "paused"}
        if action == "resume" and not check_replica_paused(config):
            print("(replica_manager.py) WAL replay successfully resumed.")
            return {"status": "resumed"}
        print(f"(replica_manager.py) Failed to {action} replication.")
        return {"status": "error", "error": f"Failed to {action} replication."}
    except Exception as e:
        print(f"(replica_manager.py) Error managing replication: {e}")
        return {"status": "error", "error": str(e)}
