import os

def chunk_text(text, chunk_size=500, overlap=100):
    """
    Splits text into overlapping chunks.
    Example: if chunk_size=500 and overlap=100,
    each chunk shares 100 characters with the previous one.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start += chunk_size - overlap
    return chunks

def process_documents(input_folder="data/documents", output_folder="data/chunks", chunk_size=500, overlap=100):
    """
    Reads all .txt files from input_folder, chunks them, and saves chunks into output_folder.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            with open(os.path.join(input_folder, filename), "r", encoding="utf-8") as f:
                text = f.read()
            
            chunks = chunk_text(text, chunk_size, overlap)

            # Save chunks into a new file
            out_file = os.path.join(output_folder, f"{filename.replace('.txt', '')}_chunks.txt")
            with open(out_file, "w", encoding="utf-8") as f:
                for i, chunk in enumerate(chunks):
                    f.write(f"--- Chunk {i+1} ---\n{chunk}\n\n")

            print(f"Processed {filename}: {len(chunks)} chunks created.")


if __name__ == "__main__":
    process_documents()
