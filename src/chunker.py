import os
import nltk

# Ensure sentence tokenizer is ready
nltk.download("punkt_tab", quiet=True)
from nltk.tokenize import sent_tokenize

def chunk_text(text, max_chunk_size=600):
    """
    Splits text into chunks of complete sentences without exceeding max_chunk_size characters.
    """
    sentences = sent_tokenize(text)
    chunks, current_chunk = [], ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_chunk_size:
            current_chunk += " " + sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def process_documents(input_folder="data/documents", output_folder="data/chunks", max_chunk_size=600):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            with open(os.path.join(input_folder, filename), "r", encoding="utf-8") as f:
                text = f.read()

            chunks = chunk_text(text, max_chunk_size)
            out_file = os.path.join(output_folder, f"{filename.replace('.txt', '')}_chunks.txt")

            with open(out_file, "w", encoding="utf-8") as f:
                for i, chunk in enumerate(chunks):
                    f.write(f"--- Chunk {i+1} ---\n{chunk}\n\n")

            print(f"Processed {filename}: {len(chunks)} full-sentence chunks created.")

if __name__ == "__main__":
    process_documents()
