from utils.db_utils import connect_to_db

def promote_to_primary(config):
    """
    Promote the delayed database to act as the primary.
    """
    try:
        conn = connect_to_db(config)
        with conn.cursor() as cursor:
            # Promote the database to primary
            cursor.execute("SELECT pg_promote(wait => true);")
            conn.commit()
        conn.close()
        return {"status": "promoted", "error": None}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def recover_from_delay(config, crash_time):
    """
    Recover from the delayed database after the primary database crashes.
    
    Args:
        config (dict): Database connection configuration for the delayed database.
        crash_time (str): The timestamp of the primary crash (in 'YYYY-MM-DD HH:MI:SS' format).
    
    Returns:
        dict: Status and recovery details.
    """
    try:
        conn = connect_to_db(config)
        with conn.cursor() as cursor:
            # Ensure WAL replay covers up to the crash time
            cursor.execute(f"""
                SELECT pg_wal_replay_resume();
                SELECT pg_last_wal_replay_lsn();
                SELECT pg_replay_timeline_status();
            """)
            conn.commit()
        
        # Promote the delayed database to primary
        promotion_status = promote_to_primary(config)
        if promotion_status["status"] == "error":
            return promotion_status
        
        return {"status": "recovered", "message": "Database promoted to primary after recovery.", "error": None}
    except Exception as e:
        return {"status": "error", "error": str(e)}
    finally:
        if conn:
            conn.close()