# `document_routes.py`

This module defines API routes for managing uploaded documents in **DocMind**. It supports uploading, listing, and deleting files via HTTP endpoints, while also managing related indexing in the vector store.

---

## Responsibilities

- Handle **file uploads** to the server
- Validate file formats and resolve name conflicts
- **List** all uploaded documents stored on disk
- **Delete** uploaded files and remove their FAISS vector index entries

---

## API Endpoints

### `POST /upload`
Upload one or more documents via multipart/form-data.

- Supported formats: `.pdf`, `.png`, `.jpg`, `.jpeg`, `.txt`, `.docx`
- Files are saved into the `UPLOAD_DIR/{session_id}` directory
- Filename conflicts are resolved with automatic numbering (e.g., `report 2.pdf`)
- Requires a `session_id` (from client-side localStorage) to associate uploads with a user session

### `GET /list`
Returns a list of all documents uploaded **within the current session**.

- Scans the `UPLOAD_DIR/{session_id}/` directory
- Returns a clean list of file names for the current session.

### `DELETE /delete/{filename}`
Deletes a document from the current session and removes its associated FAISS vector entries.

- Verifies existence within the current `UPLOAD_DIR/{session_id}/` folder
- Calls `remove_from_metadata(session_id, doc_id)` to maintain vector store integrity

---

## Dependencies

- `UPLOAD_DIR` from `config.py`: base directory for storing uploaded documents; session-specific subdirectories `UPLOAD_DIR/{session_id}` are dynamically created in the route logic
- `remove_from_metadata(session_id, doc_id)` from `meta_store.py`: used during deletion
- `DocumentUploadResponse`, `DocumentListResponse`, `DeleteResponse` from `models.py`
- Uses `FastAPI`’s `APIRouter` for endpoint registration
- `logger` from `logger.py` for structured logging throughout execution

---

## Notes

- This route is protected with a global shared rate limiter. If you exceed the request threshold, you'll be redirected to a rate-limit warning page in-app JS handling.
- Each uploaded document is treated as a unique document identifier (`doc_id`) in the vector store.
- Uploaded files are assumed to be ready for preprocessing and indexing downstream in the pipeline.
- This module doesn't trigger analysis; it purely manages raw file lifecycle.
