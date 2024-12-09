import psycopg2
from time import sleep
from datetime import datetime

# Configuration for the primary database
primary_config = {
    "host": "172.20.224.175",
    "port": 5444,
    "dbname": "edb",
    "user": "mubasher_oms",
    "password": "password"
}

# Function to insert dummy data into the primary database
def insert_dummy_data(config, interval=5):
    """
    Inserts dummy data into the primary database at regular intervals.
    
    Args:
        config (dict): Database connection configuration.
        interval (int): Delay in seconds between each insertion.
    """
    try:
        conn = psycopg2.connect(**config)
        with conn.cursor() as cursor:
            # Ensure the dummy_data table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dummy_data (
                    id SERIAL PRIMARY KEY,
                    value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            print("Dummy table ensured in the primary database.")

            # Insert data in a loop
            while True:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute(
                    "INSERT INTO dummy_data (name) VALUES (%s) RETURNING id;",
                    (f"Dummy data inserted at {current_time}",)
                )
                inserted_id = cursor.fetchone()[0]
                conn.commit()
                print(f"Inserted dummy data with ID {inserted_id} at {current_time}")
                sleep(interval)  # Delay between insertions

    except Exception as e:
        print("Error inserting dummy data:", e)
    finally:
        if conn:
            conn.close()

# Run the script
if __name__ == "__main__":
    try:
        delay_interval = 5  # Set the delay interval in seconds
        print(f"Starting to insert dummy data every {delay_interval} seconds...")
        insert_dummy_data(primary_config, interval=delay_interval)
    except KeyboardInterrupt:
        print("\nScript stopped by user.")