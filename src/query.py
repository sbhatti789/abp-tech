import os
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from src.embedder import load_chunks

def query_faiss(query_text, index_path="data/faiss.index", vectors_path="data/vectors.npy", top_k=5):
    """
    Embeds a user query and retrieves the most relevant text chunks.
    """
    # Load model
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Load FAISS index
    index = faiss.read_index(index_path)

    # Load chunk metadata (so we can print text)
    chunks = load_chunks()
    texts = [text for _, text in chunks]

    # Embed the query
    query_vec = model.encode([query_text], convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(query_vec)

    # Search top-k similar chunks
    D, I = index.search(query_vec, top_k)
    print(f"\n🔍 Query: {query_text}")
    print(f"Top {top_k} most similar chunks:\n")

    for rank, (score, idx) in enumerate(zip(D[0], I[0]), start=1):
        print(f"--- Result {rank} | Similarity: {score:.4f} ---")
        print(texts[idx][:350], "\n")  # show first ~350 characters


if __name__ == "__main__":
    while True:
        query_text = input("\n🔍 Enter your query (or type 'exit' to quit): ")
        if query_text.lower() in ["exit", "quit"]:
            print("Exiting query interface.")
            break
        query_faiss(query_text, top_k=5)
