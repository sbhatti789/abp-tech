# src/db.py
import psycopg2

# ⚠️ Must match your working database config
DB_NAME = "chicago_crimes_db"
DB_USER = "postgres"
DB_PASSWORD = "CS480!"
DB_HOST = "localhost"
DB_PORT = "5432"


def get_connection():
    """
    Returns a new psycopg2 connection to the database.
    Caller is responsible for closing it.
    """
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )
