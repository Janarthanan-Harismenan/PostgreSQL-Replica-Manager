import psycopg2

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