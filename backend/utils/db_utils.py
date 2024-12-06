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


def get_last_update_time(conn):
    """
    Get the delay time from the database for the delayed replica.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        try:
            cursor.execute("SELECT now() - pg_last_xact_replay_timestamp() AS delay_time;")
            result = cursor.fetchone()
            if result and result['delay_time']:
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


def pause_replication(config):
    """
    Pause replication for the delayed database.
    """
    try:
        conn = connect_to_db(config)
        with conn.cursor() as cursor:
            cursor.execute("SELECT pg_wal_replay_pause();")  # Pauses WAL replay
            conn.commit()
        conn.close()
        return {"status": "paused"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def resume_replication(config):
    """
    Resume replication for the delayed database.
    """
    try:
        conn = connect_to_db(config)
        with conn.cursor() as cursor:
            cursor.execute("SELECT pg_wal_replay_resume();")  # Resumes WAL replay
            conn.commit()
        conn.close()
        return {"status": "resumed"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
