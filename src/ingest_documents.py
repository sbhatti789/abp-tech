# src/ingest_documents.py

import os
import numpy as np
from psycopg2 import Binary
from sentence_transformers import SentenceTransformer

from src.db import get_connection
from src.chunker import chunk_text


def ingest_document_file(file_path, uploader_user_id=None, max_chunk_size=600):
    #Ingests a single .txt file:
    filename = os.path.basename(file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_text(text, max_chunk_size=max_chunk_size)
    if not chunks:
        print(f"No chunks produced for {filename}, skipping.")
        return

    print(f"Ingesting {filename} with {len(chunks)} chunks...")

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO documents (filename, original_text, uploader_user_id)
            VALUES (%s, %s, %s)
            RETURNING id;
            """,
            (filename, text, uploader_user_id),
        )
        document_id = cur.fetchone()[0]
        print(f"   → document_id = {document_id}")

        model = SentenceTransformer("all-MiniLM-L6-v2")
        embeddings = model.encode(chunks, convert_to_numpy=True, show_progress_bar=True)

        for chunk_text_value, emb in zip(chunks, embeddings):
            emb = emb.astype("float32")
            emb_bytes = emb.tobytes()

            cur.execute(
                """
                INSERT INTO chunks (document_id, chunk_text, embedding)
                VALUES (%s, %s, %s)
                RETURNING id;
                """,
                (document_id, chunk_text_value, Binary(emb_bytes)),
            )
            cur.fetchone()

        conn.commit()
        print(f"Finished ingesting {filename}")

    except Exception as e:
        conn.rollback()
        print(f"Error ingesting {filename}:", e)

    finally:
        cur.close()
        conn.close()


def ingest_all_documents(folder_path="data/documents", uploader_user_id=None):
    #Ingests all .txt files in the folder into the database.
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            full_path = os.path.join(folder_path, filename)
            ingest_document_file(full_path, uploader_user_id=uploader_user_id)


if __name__ == "__main__":
    ingest_all_documents()
