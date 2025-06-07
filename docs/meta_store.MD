# `meta_store.py`

This module manages the core **FAISS-based vector search engine** for DocMind. It handles embedding, indexing, searching, and cleanup of chunked document data.

---

## Responsibilities

- Encode and store chunk embeddings using `sentence-transformers`
- Store chunk texts and embeddings in structured per-document metadata
- Support document addition, deletion, and re-checking
- Perform top-k semantic chunk retrieval using a temporary FAISS index
- Persist metadata in session-scoped directories

---

## Key Functions

### `init_or_load_metadata(session_id: str)`
- Loads metadata from `backend/data/meta_store/{session_id}/meta.npy`

- Initializes a new metadata dictionary if none exists

- All metadata is isolated per session

---

### `save_metadata(session_id: str, metadata: Dict[str, Dict[str, List]])`
- Persists the session-specific metadata dictionary to disk

- Used after any addition or deletion of chunks

- Ensures session-level isolation by storing metadata in `backend/data/meta_store/{session_id}/meta.npy`

---

### `add_to_metadata(session_id: str, doc_id: str, chunks: List[str])`
- Embeds each chunk using a sentence transformer
- Stores each chunk's text and corresponding embedding under its associated `doc_id` within the metadata
- Safely persists the updated metadata to disk

---

### `remove_from_metadata(session_id: str, doc_id: str)`
- Deletes the given `doc_id`'s chunks and embeddings from metadata
- Safely persists the updated metadata to disk

---

### `search_top_k_chunks(session_id: doc_id: str, query: str, k: int = 3)`
- Embeds the user query
- Uses a temporary in-memory FAISS index to compute similarity with stored chunks
- Returns top-k chunk indices and texts ranked by semantic similarity from the specified document


---

### `is_document_indexed(session_id: str, doc_id: str) -> bool`
- Checks whether the document has already been embedded and stored
- Helps avoid redundant processing in the document pipeline

---

## Metadata Structure

Each document is stored with metadata:

```json
{
  "report.pdf": {
    "chunks": ["paragraph 1 text", "paragraph 2 text", ...],
    "embeddings": [[0.12, 0.53, ...], [0.47, 0.22, ...], ...]
  }
}
```


## PERSISTENCE
- Each session has its own metadata file named meta.npy, stored in `backend/data/meta_store/{session_id}`

- Updated every time new documents are added or removed

## Dependencies
- `faiss` – FAISS indexing and searching

- `sentence-transformers` – Dense embeddings for chunks/queries

- `pathlib` - OS-agnostic file path handling

- `numpy` – Storage of metadata

- `config.py` – Paths to metadata files

## Related Modules
- `document_preprocessor.py` – Calls add_chunks_to_index() after chunking

- `query_engine.py` – Uses search_top_k_chunks() to retrieve similar content

- `pipeline_routes.py` – Checks is_document_indexed() to skip reprocessing
