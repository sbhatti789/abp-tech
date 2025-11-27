# src/faiss_indexer.py

import numpy as np
import faiss
from src.db import get_connection

def load_embeddings_from_db():
    """
    Loads all embeddings and chunk IDs from the database.
    Returns:
        embeddings (np.ndarray): shape (N, 384)
        chunk_ids (list[int])
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, embedding FROM chunks;")
    rows = cur.fetchall()

    chunk_ids = []
    vectors = []

    for chunk_id, emb_bytes in rows:
        emb = np.frombuffer(emb_bytes, dtype="float32")
        vectors.append(emb)
        chunk_ids.append(chunk_id)

    cur.close()
    conn.close()

    if not vectors:
        raise ValueError("❌ No embeddings found in database.")

    embeddings = np.vstack(vectors).astype("float32")
    return embeddings, chunk_ids


def build_faiss_index():
    """
    Builds a FAISS index from embeddings stored in PostgreSQL.
    Returns:
        index (faiss.IndexFlatIP)
        chunk_ids (list[int])
    """
    embeddings, chunk_ids = load_embeddings_from_db()

    dim = embeddings.shape[1]
    print(f"📦 Loaded {len(chunk_ids)} vectors (dim={dim}) from SQL")

    # Normalize for cosine similarity
    faiss.normalize_L2(embeddings)

    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    print(f"✅ FAISS index built with {index.ntotal} vectors")
    return index, chunk_ids


if __name__ == "__main__":
    build_faiss_index()
