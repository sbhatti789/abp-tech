# src/log_query.py

from src.db import get_connection

def log_query(query_text, user_id=None):
    """
    Inserts a query into the query_logs table.
    For now, user_id can be None until authentication is added.
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO query_logs (user_id, query_text)
            VALUES (%s, %s);
            """,
            (user_id, query_text),
        )
        conn.commit()
        print("Query logged.")
    except Exception as e:
        conn.rollback()
        print("Failed to log query:", e)
    finally:
        cur.close()
        conn.close()
