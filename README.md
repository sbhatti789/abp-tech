# CS 480 Group Project Phase 4 - abp-tech - Samad Bhatti, Ayush Patel

# 4.1
Source File: src/chunker.py

Execute Code: python3 src/chunker.py

Result Example: Processed 1_CriminalDamage.txt: 5 full-sentence chunks created.

Description: 
* Reads all .txt documents in data/documents
* Splits them into clean sentence-based chunks (about 3-4 sentences each)
* Saves the chunks into data/chunks

# 4.2
Source File: src/embedder.py

Execute Code: python3 src/embedder.py

Result Example: Encoding 25 chunks... Saved 25 vectors to data/vectors.npy

Description: 
* Loads all chunks from data/chunks
* Uses the model all-MiniLM-L6-v2 to create embeddings
* Saves all vectors into data/vectors.npy

# 4.3
Source File: src/vectordb.py

Execute Code: python3 -m src.vectordb.py

Result Example: Building FAISS index... Saved faiss.index

Description: 
* Creates a FAISS index (in-memory vector database)
* Adds all embeddings to the index
* Saves the index file to data/faiss.index

# 4.4
Source File: src/query.py

Execute Code: python3 -m src.query

Result Example: Enter your query: Which crimes involved arrests?

Description: 
* Lets the user ask any question
* Embeds the query
* Searches FAISS for the most similiar text chunks
* Prints the top result with similarity scores


