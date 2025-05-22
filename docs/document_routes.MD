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
- Files are saved into the `uploads/` directory
- Filename conflicts are resolved with automatic numbering (e.g., `report 2.pdf`)

### `GET /list`
Returns a list of all documents currently uploaded to the backend.

- Scans the upload directory
- Returns a clean list of file names

### `DELETE /delete/{filename}`
Deletes a document by filename and removes its related FAISS vector entries.

- Verifies existence before deletion
- Calls `remove_doc_from_index()` to ensure vector store stays clean

---

## Dependencies

- `UPLOAD_DIR` from `config.py`: defines where uploads are stored
- `remove_doc_from_index()` from `vector_store.py`: used during deletion
- `DocumentUploadResponse`, `DocumentListResponse`, `DeleteResponse` from `models.py`
- Uses `FastAPI`’s `APIRouter` for endpoint registration
- `logger` from `logger.py` for structured logging throughout execution

---

## Notes

- Each uploaded document is treated as a unique document identifier (`doc_id`) in the vector store.
- Uploaded files are assumed to be ready for preprocessing and indexing downstream in the pipeline.
- This module doesn't trigger analysis; it purely manages raw file lifecycle.
