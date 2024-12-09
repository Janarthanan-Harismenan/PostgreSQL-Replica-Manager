import psycopg2
from psycopg2.extras import RealDictCursor


def connect_to_db(config):
    """
    Establish a connection to the PostgreSQL database.
    """
    return psycopg2.connect(
        host=config['host'],
        port=config['port'],
        dbname=config['dbname'],
        user=config['user'],
        password=config['password']
    )


# def get_last_update_time(conn):
#     """
#     Get the delay time from the database for the delayed replica.
#     """
#     with conn.cursor(cursor_factory=RealDictCursor) as cursor:
#         try:
#             cursor.execute("SELECT now() - pg_last_xact_replay_timestamp() AS delay_time;")
#             result = cursor.fetchone()
#             if result and result['delay_time']:
#                 return result['delay_time']
#         except Exception as e:
#             print("Error fetching delay time:", e)
#         return None
    
def get_last_update_time(conn):
    """
    Get the delay time from the database for the delayed replica.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        try:
            # Query for delay time
            cursor.execute("""
                SELECT now() AS current_time, 
                       pg_last_xact_replay_timestamp() AS replay_time,
                       now() - pg_last_xact_replay_timestamp() AS delay_time
                """)
            result = cursor.fetchone()
            if result and result['delay_time']:
                print("Current Time:", result['current_time'])
                print("Replay Time:", result['replay_time'])
                print("Delay Time:", result['delay_time'])
                return result['delay_time']
        except Exception as e:
            print("Error fetching delay time:", e)
        return None
    
def check_replica_status(config):
    """
    Check the replication status of the database.
    """
    try:
        conn = connect_to_db(config)
        delay_time = None
        if config.get("role") == "delayed":
            delay_time = get_last_update_time(conn)
 
        conn.close()
        if check_replica_paused(config):
            return {
                "status": "paused",
                "delay": str(delay_time) if delay_time else "N/A",
                "error": None
            }
        else:
            return {
                "status": "running",
                "delay": str(delay_time) if delay_time else "N/A",
                "error": None
        }
    except Exception as e:
        return {
            "status": "stopped",
            "delay": None,
            "error": str(e)
        }

def check_replica_paused(config):
    """
    Check if the replication for the delayed database is paused.
    """
    try:
        conn = connect_to_db(config)
        with conn.cursor() as cursor:
            # Query to check if WAL replay is paused
            cursor.execute("SELECT pg_is_wal_replay_paused();")
            result = cursor.fetchone()
            return result[0]
            # if result and result[0]:
            #     return True  # WAL replay is paused
            # else:
            #     return False  # WAL replay is not paused
           
    except Exception as e:
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
        if action not in ["pause", "resume"]:
            return {"status": "error", "error": "Invalid action. Use 'pause' or 'resume'."}
        
        # Determine the current state
        is_paused = check_replica_paused(config)
        
        if action == "pause" and is_paused:
            return {"status": "already paused"}
        if action == "resume" and not is_paused:
            return {"status": "already resumed"}
        
        # Perform the action
        conn = connect_to_db(config)
        with conn.cursor() as cursor:
            if action == "pause":
                cursor.execute("SELECT pg_wal_replay_pause();")  # Pauses WAL replay
            elif action == "resume":
                cursor.execute("SELECT pg_wal_replay_resume();")  # Resumes WAL replay
            conn.commit()
        conn.close()
        
        # Confirm the action
        if action == "pause" and check_replica_paused(config):
            return {"status": "paused"}
        if action == "resume" and not check_replica_paused(config):
            return {"status": "resumed"}
        return {"status": "error", "error": f"Failed to {action} replication."}
    except Exception as e:
        return {"status": "error", "error": str(e)}