import os
import nltk
nltk.download("punkt", quiet=True)
from nltk.tokenize import sent_tokenize



def chunk_text(text, max_chars=300):
    sentences = sent_tokenize(text)
    chunks = []
    current = ""

    for sent in sentences:
        sent = sent.strip()

        # If adding this sentence stays under limit: add to chunk
        if len(current) + len(sent) <= max_chars:
            current += " " + sent if current else sent
        else:
            # push completed chunk
            if current:
                chunks.append(current)
            current = sent

    # push final chunk
    if current:
        chunks.append(current)

    return chunks


def process_documents(input_folder="data/documents",
                      output_folder="data/chunks",
                      max_chars=300):

    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if not filename.endswith(".txt"):
            continue

        with open(os.path.join(input_folder, filename), "r", encoding="utf-8") as file:
            text = file.read()

        chunks = chunk_text(text, max_chars=max_chars)

        out_path = os.path.join(
            output_folder, f"{filename.replace('.txt', '')}_chunks.txt"
        )

        with open(out_path, "w", encoding="utf-8") as out:
            for i, chunk in enumerate(chunks):
                out.write(f"--- Chunk {i+1} ---\n{chunk}\n\n")

        print(f"Processed {filename}: {len(chunks)} semantic chunks created.")


if __name__ == "__main__":
    process_documents()