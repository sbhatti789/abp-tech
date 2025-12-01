# src/query_sql.py

import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

from src.faiss_indexer import build_faiss_index
from src.db import get_connection




CRIME_KEYWORDS = {
    "drugs": ["drug", "narcotic", "controlled substance", "possession", "distribution"],
    "burglary": ["burglary", "break-in", "forced entry", "home invasion"],
    "theft": ["theft", "stolen", "steal", "shoplifting"],
    "vehicle": ["vehicle", "car", "auto theft", "motor", "stolen car"],
    "deception": ["fraud", "deception", "forgery", "scam"],
    "children": ["child", "minor", "children", "juvenile"],
    "damage": ["damage", "property damage", "criminal damage"],
    "battery": ["battery", "assault", "violence"],
    "weapons": ["weapon", "firearm", "gun", "armed"],
}

BOOST_AMOUNT = 0.40  


# --------------------------------------------
# Fetch Chunk Texts
# --------------------------------------------

def fetch_chunk_texts(chunk_ids):
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


# --------------------------------------------
# Main Query System 
# --------------------------------------------

def query_system(query_text, top_k=10):
    # Build FAISS index
    index, chunk_ids = build_faiss_index()

    # Embed query
    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_vec = model.encode([query_text], convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(query_vec)

    # Search many chunks 
    D, I = index.search(query_vec, 100)

    # Convert FAISS IDs: chunk IDs
    matched_chunk_ids = [chunk_ids[idx] for idx in I[0]]

    # Fetch chunk text & filenames
    rows = fetch_chunk_texts(matched_chunk_ids)

    # Deduplicate by document
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


    query_lower = query_text.lower()

    for doc in best_by_doc.values():
        fname = doc["filename"].lower()
        text = doc["chunk"].lower()

        for crime, words in CRIME_KEYWORDS.items():
            if any(word in query_lower for word in words):
                if any(word in fname or word in text for word in words):
                    doc["score"] += BOOST_AMOUNT  # Boost matching files

    results = list(best_by_doc.values())
    results.sort(key=lambda x: x["score"], reverse=True)

    return results[:top_k]


# --------------------------------------------
# Command-Line Test
# --------------------------------------------

if __name__ == "__main__":
    while True:
        user_query = input("\nEnter your query (or 'exit' to quit): ")
        if user_query.lower() in ["exit", "quit"]:
            print("Exiting.")
            break

        res = query_system(user_query)
        for r in res:
            print(r)