# `vector_store.py`

This module manages the core **FAISS-based vector search engine** for DocMind. It handles embedding, indexing, searching, and cleanup of chunked document data.

---

## Responsibilities

- Encode and store chunk embeddings using `sentence-transformers`
- Assign unique FAISS IDs to chunks via hashing
- Maintain metadata for each embedded chunk
- Enable semantic search for top-k chunks within a specific document
- Support document reindexing and deletion
- Persist vector index and metadata between sessions

---

## Key Functions

### `init_or_load_index(session_id: str)`
- Loads or creates a FAISS index from `backend/data/vector_store/{session_id}/vector_index.faiss`

- Loads or initializes corresponding metadata from `backend/data/vector_store/{session_id}/meta.npy`

- Ensures vector index and metadata are session-scoped and kept separate per user/session

### `save_index(session_id: str, index, metadata)`
- Serializes and writes the FAISS index to disk in the session's directory

- Saves metadata to a .npy file alongside the index

- Guarantees session-level persistence without affecting other users or sessions



### `add_chunks_to_index(session_id: str, doc_id: str, chunks: List[str])`
- Embeds each chunk using a sentence transformer
- Assigns stable, unique FAISS IDs to avoid duplication
- Stores each chunk in both FAISS and a local metadata array
- Writes FAISS index and metadata to disk
- Ensures session-level isolation by storing vectors and metadata in `backend/data/vector_store/{session_id}`

---

### `remove_doc_from_index(session_id: str, doc_id: str)`
- Looks up all FAISS IDs associated with the `doc_id`
- Removes them from both the FAISS index and metadata list
- Updates persistent storage on disk
- Maintains session-level isolation by deleting only the target document's data in `backend/data/vector_store/{session_id}`
---

### `search_top_k_chunks(session_id: doc_id: str, query: str, k: int = 3)`
- Embeds the user query
- Filters relevant metadata for the given doc
- Creates a temporary FAISS index to run similarity search
- Returns top-k chunk metadata from that specific document

---

### `is_document_indexed(session_id: str, doc_id: str) -> bool`
- Checks whether the document has been previously embedded
- Avoids redundant reprocessing in the pipeline

---

## Data Structure

Each chunk is stored with metadata:

```json
{
  "doc_id": "report.pdf",
  "chunk_index": 2,
  "faiss_id": 372929387,
  "text": "This is a paragraph...",
  "embedding": [0.01, 0.03, ...]
}
```
## ID Generation

Each chunk gets a reproducible FAISS ID:

```python
hash_input = f"{doc_id}_chunk_{chunk_index}"
faiss_id = int(md5(hash_input).hexdigest()[:12], 16) % (10**9)
```
This ensures document re-ingestion doesn't produce duplicates.
## PERSISTENCE
- Each session has its own FAISS index and metadata file named vector_index.faiss and meta.npy, stored in `backend/data/vector_store/{session_id}`

- Both are updated every time new chunks are added or removed

Dependencies
- `faiss` – FAISS indexing and searching

- `sentence-transformers` – Dense embeddings for chunks/queries

- `hashlib` – FAISS ID hashing

- `numpy` – Vector and metadata storage

- `config.py` – Paths to index and metadata files

## Related Modules
- `document_preprocessor.py` – Calls add_chunks_to_index() after chunking

- `query_engine.py` – Uses search_top_k_chunks() to retrieve similar content

- `pipeline_routes.py` – Checks is_document_indexed() to skip reprocessing
