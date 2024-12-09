import psycopg2
from time import sleep

primary_config = {
    "host": "172.20.224.175",
    "port": 5444,
    "dbname": "edb",
    "user": "mubasher_oms",
    "password": "password"
}

delayed_config = {
    "host": "172.20.224.149",
    "port": 5444,
    "dbname": "edb",
    "user": "mubasher_oms",
    "password": "password"
}

def fetch_data(config):
    try:
        conn = psycopg2.connect(**config)
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM dummy_data ORDER BY id DESC LIMIT 1;")
            return cursor.fetchone()
    except Exception as e:
        print(f"Error connecting to {config['host']}:", e)
    finally:
        if conn:
            conn.close()

while True:
    print("Fetching data...")
    primary_data = fetch_data(primary_config)
    delayed_data = fetch_data(delayed_config)
    print("Primary:", primary_data)
    print("Delayed:", delayed_data)
    sleep(5)  # Wait 5 seconds before polling again
