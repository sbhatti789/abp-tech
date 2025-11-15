import numpy as np
import faiss
import os
from src.embedder import load_chunks

def build_faiss_index(vectors_path="data/vectors.npy", index_path="data/faiss.index"):
    """
    Loads embeddings from file and builds a FAISS index for similarity search.
    Saves the index to disk for later use.
    """
    if not os.path.exists(vectors_path):
        raise FileNotFoundError(f"Embeddings not found at {vectors_path}. Run embedder.py first.")

    # Load vector data
    vectors = np.load(vectors_path).astype("float32")

    # Get vector dimensions
    dim = vectors.shape[1]
    print(f"Building FAISS index for {len(vectors)} vectors (dimension={dim})...")

    # Create a FAISS index (cosine similarity via inner product)
    index = faiss.IndexFlatIP(dim)

    # Normalize vectors for cosine similarity
    faiss.normalize_L2(vectors)

    # Add vectors to index
    index.add(vectors)
    print(f"Added {index.ntotal} vectors to FAISS index.")

    # Save the index
    faiss.write_index(index, index_path)
    print(f"Saved FAISS index to {index_path}")

    return index


def search_faiss_index(query_vector, index_path="data/faiss.index", top_k=5):
    """
    Loads the FAISS index and searches for the top_k nearest neighbors to the query_vector.
    """
    if not os.path.exists(index_path):
        raise FileNotFoundError("FAISS index not found. Build it first with build_faiss_index().")

    index = faiss.read_index(index_path)
    faiss.normalize_L2(query_vector)
    D, I = index.search(query_vector, top_k)
    return D, I


if __name__ == "__main__":
    # Build FAISS index for existing vectors
    build_faiss_index()
