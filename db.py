import os
import psycopg


def get_connection():
    conn = psycopg.connect(
        dbname="task_manager",
        user="postgres",
        password=os.getenv("DB_PASSWORD"),
        host="localhost",
        port=5432,
    )
    return conn
