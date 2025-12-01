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

# 3.1 
User Authentication and Roles

Source File: app.py, templates/login.html, templates/signup.html

Execute Code: python3 app.py

Description: 
* Allows user to signup and log in
* Passwords are hashed
* User: searches
* Curator: search and uploads documents
* Admin: users, documents, logs

# 3.2
Document Upload

Source File: app.py

Execute Code: python3 app.py

Description: 
* Saves uploaded file
* Runs Phase 3 Pipeline
* Uses SQL for data storage

# 3.3
Semantic Search

Source File: app.py

Execute Code: python3 app.py, open browser, enter a question

Description: 
* User asks a question about topic
* Embeds the query
* Uses FAISS
* Displays information about question

# 3.4
Query

Source File: app.py

Execute Code: python3 app.py

Description: 
* Search query saved to SQL
* Admin can view all the tables

# 3.5
Document

Source File: app.py

Execute Code: python3 app.py


Description: 
* Shows all documents
* Displays document information
* Admin can delete a document

# 3.6
User Management

Source File: app.py

Execute Code: python3 app.py


Description: 
* Admin can view all users
* Edit/delete a user