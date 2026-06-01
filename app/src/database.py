import psycopg2
import psycopg2.pool
import os

host = os.environ.get('POSTGRES_HOST')
dbname = os.environ.get('POSTGRES_DB')
user = os.environ.get('POSTGRES_USER')
password = os.environ.get('POSTGRES_PASSWORD')

pool = None

def init_pool():
    global pool
    try:
        pool = psycopg2.pool.SimpleConnectionPool(1, 2, host=host, dbname=dbname, user=user, password=password)
    except psycopg2.OperationalError as e:
        print(f"Database connection failed: {e}")
        exit(1)

def get_connection():
    try:
        return pool.getconn()
    except psycopg2.OperationalError as e:
        print(f"Couldn't assign DB connection from pool: {e}")
        exit(1)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    create_statement = "CREATE TABLE IF NOT EXISTS images (image_id SERIAL PRIMARY KEY, filepath TEXT, filename TEXT, timestamp TIMESTAMP, lat DECIMAL(9,6), lng DECIMAL(9,6), tags TEXT[], file_exists BOOLEAN DEFAULT TRUE, favourite BOOLEAN DEFAULT FALSE)"
    try:
        cursor.execute(create_statement)
        conn.commit()
        print("Database initialised successfully")
    except psycopg2.Error as e:
        print(f"Database initialisation failed: {e}")
        conn.rollback()
        exit(1)
    finally:
        pool.putconn(conn)
