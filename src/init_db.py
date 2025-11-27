import psycopg2


DB_NAME = "chicago_crimes_db"
DB_USER = "postgres"
DB_PASSWORD = "CS480!"
DB_HOST = "localhost"
DB_PORT = "5432"

schema_sql = """
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'curator', 'user')),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    original_text TEXT,
    uploader_user_id INT REFERENCES users(id) ON DELETE SET NULL,
    uploaded_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chunks (
    id SERIAL PRIMARY KEY,
    document_id INT REFERENCES documents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    embedding BYTEA NOT NULL
);

CREATE TABLE IF NOT EXISTS query_logs (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    query_text TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW()
);
"""

def initialize_database():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()

        cur.execute(schema_sql)
        conn.commit()

        print("✅ Database initialized successfully!")
        cur.close()
        conn.close()

    except Exception as e:
        print("❌ Error initializing database:", e)


if __name__ == "__main__":
    initialize_database()
