# src/chunker.py

import os
import nltk

# Make sure the Punkt tokenizer is available
nltk.download("punkt_tab", quiet=True)
from nltk.tokenize import sent_tokenize


def chunk_text(text, max_chunk_size=600, overlap=0, *args, **kwargs):
    """
    Split text into reasonably sized chunks (by sentences).

    Parameters
    ----------
    text : str
        The full document text.
    max_chunk_size : int
        Approximate maximum number of characters per chunk.
    overlap : int
        Optional character overlap between consecutive chunks.
        (If you don't need it, just leave it at 0.)
    *args, **kwargs :
        Extra positional/keyword arguments are ignored to keep this
        function compatible with older calls.
    """

    sentences = sent_tokenize(text)
    chunks = []
    current = ""

    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue

        # If adding this sentence stays under the limit, append to current chunk
        if len(current) + len(sent) + 1 <= max_chunk_size:
            if current:
                current += " " + sent
            else:
                current = sent
        else:
            # Close current chunk and start a new one
            if current:
                chunks.append(current)
            current = sent

    if current:
        chunks.append(current)

    if overlap > 0 and len(chunks) > 1:
        overlapped = []
        for i, ch in enumerate(chunks):
            if i == 0:
                overlapped.append(ch)
            else:
                prev = overlapped[-1]
                tail = prev[-overlap:]
                combined = (tail + " " + ch).strip()
                overlapped.append(combined[:max_chunk_size])
        chunks = overlapped

    return chunks


def process_documents(input_folder="data/documents",
                      output_folder="data/chunks",
                      max_chunk_size=600):

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if not filename.endswith(".txt"):
            continue

        in_path = os.path.join(input_folder, filename)
        with open(in_path, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = chunk_text(text, max_chunk_size=max_chunk_size)
        out_name = filename.replace(".txt", "") + "_chunks.txt"
        out_path = os.path.join(output_folder, out_name)

        with open(out_path, "w", encoding="utf-8") as f:
            for i, ch in enumerate(chunks, start=1):
                f.write(f"--- Chunk {i} ---\n{ch}\n\n")

        print(f"Processed {filename}: {len(chunks)} chunks.")


if __name__ == "__main__":
    process_documents()