import os
import numpy as np
from sentence_transformers import SentenceTransformer

def load_chunks(folder_path="data/chunks"):
    """
    Reads all chunked text files and returns a list of (chunk_id, text) tuples.
    """
    chunks = []
    for filename in os.listdir(folder_path):
        if filename.endswith("_chunks.txt"):
            with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                content = f.read()
                # Split each chunk by header pattern
                parts = content.split("--- Chunk ")
                for part in parts:
                    if part.strip() and not part.startswith("1 ---"):
                        try:
                            number, text = part.split("---", 1)
                            chunks.append((f"{filename}_chunk{number.strip()}", text.strip()))
                        except ValueError:
                            continue
    return chunks

def embed_chunks(chunks, model_name="all-MiniLM-L6-v2", output_file="data/vectors.npy"):
    """
    Converts chunks to vector embeddings and saves them.
    """
    model = SentenceTransformer(model_name)
    texts = [text for _, text in chunks]
    print(f"Encoding {len(texts)} chunks...")

    # Generate embeddings
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)

    np.save(output_file, embeddings)
    print(f"✅ Saved {len(embeddings)} vectors to {output_file}")
    return embeddings

if __name__ == "__main__":
    chunks = load_chunks()
    embed_chunks(chunks)
