from dotenv import load_dotenv
import json
import os
import psycopg
from psycopg import OperationalError
from psycopg_pool import ConnectionPool

load_dotenv(override=True)

conn_string = (
    f"host={os.getenv('DB_HOST')} "
    f"port={os.getenv('DB_PORT')} "
    f"dbname={os.getenv('DB_NAME')} "
    f"user={os.getenv('DB_USER')} "
    f"password={os.getenv('DB_PASSWORD')}"
)

pool = ConnectionPool(
    conninfo=conn_string,
    open=True,
    min_size=3
    )

def create_connection() -> psycopg.connection:
    try:
        conn = psycopg.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )
        print("Connection to PostgreSQL DB successful")
        return conn
    except OperationalError as e:
        print(f"The error '{e}' occurred")
        raise e
    
def get_exercises(username: str) -> list[str]:
    with pool.connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT DISTINCT exercise FROM weightlifting
            WHERE user_id = %s
            """, (username,)               
        )
        exercises = cur.fetchall()

    return exercises

