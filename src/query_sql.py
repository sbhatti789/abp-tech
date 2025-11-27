# src/query_sql.py

import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

from src.faiss_indexer import build_faiss_index
from src.db import get_connection


def fetch_chunk_texts(chunk_ids):
    """
    Given a list of chunk IDs, fetch their text and document filenames.
    Returns a list of tuples: (chunk_text, filename)
    """
    conn = get_connection()
    cur = conn.cursor()

    id_tuple = tuple(chunk_ids)

    cur.execute(
        """
        SELECT chunks.chunk_text, documents.filename
        FROM chunks
        JOIN documents ON chunks.document_id = documents.id
        WHERE chunks.id IN %s;
        """,
        (id_tuple,)
    )

    results = cur.fetchall()

    cur.close()
    conn.close()

    return results


def query_system(query_text, top_k=10):
    """
    Vector search over chunk embeddings using FAISS,
    then return ONLY the best match per document.
    """
    # 1. Build FAISS index + get mapping of FAISS IDs -> chunk IDs
    index, chunk_ids = build_faiss_index()

    # 2. Embed query
    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_vec = model.encode([query_text], convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(query_vec)

    # 3. Search top 100 chunks (we’ll dedupe documents afterward)
    D, I = index.search(query_vec, 100)

    # 4. Map FAISS result indices -> actual chunk IDs
    matched_chunk_ids = [chunk_ids[idx] for idx in I[0]]

    # 5. Fetch chunk text + filenames
    rows = fetch_chunk_texts(matched_chunk_ids)

    # 6. Deduplicate by filename (keep BEST score per document)
    best_by_doc = {}

    for (chunk_text, filename), score in zip(rows, D[0]):
        score = float(score)

        if filename not in best_by_doc:
            best_by_doc[filename] = {
                "filename": filename,
                "chunk": chunk_text,
                "preview": chunk_text[:200] + "...",
                "score": score
            }

    # Convert dict -> list
    results = list(best_by_doc.values())

    # 7. Sort by score (ascending = more similar)
    results.sort(key=lambda x: x["score"], reverse=True)

    # 8. Return top K documents
    return results[:top_k]


if __name__ == "__main__":
    while True:
        user_query = input("\n🔍 Enter your query (or 'exit' to quit): ")
        if user_query.lower() in ["exit", "quit"]:
            print("👋 Exiting.")
            break

        res = query_system(user_query)
        for r in res:
            print(r)
