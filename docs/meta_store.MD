# `meta_store.py`

This module manages the MongoDB-powered metadata store for DocMind. It handles document chunk storage, embedding, semantic search with FAISS, and metadata manipulation on a per-session basis.

---

## Responsibilities

- Embed document chunks using `SentenceTransformer`

- Store chunk data and vector embeddings in MongoDB, structured under session and document identifiers

- Normalize document IDs to avoid MongoDB key conflicts

- Support addition, deletion, and search operations on document metadata

- Perform top-k semantic chunk retrieval using an in-memory FAISS index

---

## Key Functions

`normalize_doc_id(doc_id: str) -> str`

- Replaces the last . in a document ID with _ to ensure compatibility with MongoDB field naming

- Prevents issues with nested keys during updates

---

### `add_to_metadata(session_id: str, doc_id: str, chunks: List[str])`
- Embeds each chunk using `SentenceTransformer`
- Stores both chunk texts and their embeddings under the normalized `doc_id` within the `documents` field of the session's MongoDB record
- Uses `upsert=True` to insert or update metadata without overwriting other documents

---

### `remove_from_metadata(session_id: str, doc_id: str)`
- Deletes the specified doc_id's metadata from the session
- Uses $unset to surgically remove only the relevant document field

---

### `search_top_k_chunks(session_id: doc_id: str, query: str, k: int = 3)`
- Embeds the user query
- Uses a temporary in-memory FAISS index to compute similarity with stored chunks
- Returns top-k chunk indices and texts ranked by semantic similarity from the specified document


---

### `is_document_indexed(session_id: str, doc_id: str) -> bool`
- Checks if the document is already present in the MongoDB metadata for the session
- Useful to avoid redundant indexing

---

## Metadata Structure

Each document is stored with metadata:

```json
{
  "session_id": "abc123",
  "documents": {
    "report_pdf": {
      "chunks": ["text1", "text2", ...],
      "embeddings": [[0.12, 0.53, ...], [0.47, 0.22, ...], ...]
    },
    ...
  }
}
```
- The key report_pdf is normalized from report.pdf using normalize_doc_id.


## PERSISTENCE
- Metadata is stored in MongoDB under the `docmind_metadata.sessions` collection

- Each document within a session is namespaced under the documents field

- All metadata is session-scoped and can be retrieved, updated, or deleted independently

## Dependencies

- `pymongo` – MongoDB client for Python

- `faiss` – FAISS indexing and searching

- `sentence-transformers` – Dense embeddings for chunks/queries

- `numpy` – Storage of metadata

- `config.py` – Provides MONGO_URL for MongoDB connection

## Related Modules
- `document_preprocessor.py` – Calls `add_to_metadata(session_id, doc_id, chunks)` after chunking

- `query_engine.py` – Uses `search_top_k_chunks(session_id, doc_id, query, k)` to retrieve similar content

- `pipeline_routes.py` – Checks `is_document_indexed(session_id, doc_id)` to skip reprocessing
