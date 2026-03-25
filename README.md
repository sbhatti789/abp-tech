# AI-Powered Document Search System (abp-tech)

A full-stack intelligent document search system that allows users to upload documents and perform semantic search using natural language queries. This application leverages vector embeddings and a FAISS-based vector database to retrieve the most relevant information from large text datasets.

## 🚀 Features

### 🔍 Semantic Search
- Users can enter natural language queries
- System converts queries into embeddings
- Retrieves the most relevant document chunks using FAISS
- Displays similarity scores for results

### 📄 Document Processing Pipeline
- Automatically reads uploaded `.txt` files
- Splits documents into clean sentence-based chunks
- Generates embeddings using `all-MiniLM-L6-v2`
- Stores vectors and builds a FAISS index for fast retrieval

### 🔐 User Authentication & Roles
- Secure login and signup system with hashed passwords
- Role-based access control:
  - **User** → search documents
  - **Curator** → upload documents
  - **Admin** → manage users, documents, and logs

### 📤 Document Upload System
- Upload new documents through the web interface
- Automatically processes files through the NLP pipeline
- Stores processed data for search

### 🗄️ Data & Query Management
- Stores user queries in a database
- Admin dashboard to view and manage:
  - users
  - documents
  - query logs

---

## 🧠 How It Works

1. **Chunking**
   - Splits documents into smaller readable segments (3–4 sentences)

2. **Embedding**
   - Converts text chunks into numerical vectors using a transformer model

3. **Vector Database (FAISS)**
   - Stores embeddings in an efficient similarity search index

4. **Query Processing**
   - Converts user query into embedding
   - Searches FAISS index for most similar content
   - Returns top matches with similarity scores

---

## 🛠️ Tech Stack

- Python
- Flask
- SQLite / SQL
- FAISS (vector database)
- SentenceTransformers (`all-MiniLM-L6-v2`)
- HTML/CSS

---

## ▶️ How to Run

### 1. Clone the repository
```bash
git clone https://github.com/YOUR-USERNAME/abp-tech.git
cd abp-tech
