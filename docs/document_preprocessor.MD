# `document_preprocessor.py`

This module handles document parsing and text extraction for all supported file types in DocMind. It transforms raw documents into structured text chunks that are embedded and indexed for later retrieval.

---

## Responsibilities

- Extract text from PDFs, images (via OCR), DOCX, and TXT files
- Normalize and split text into clean paragraph-level chunks
- Add these chunks to the FAISS vector index
- Remove any old indexed data for the same document ID
- Provide both single-document and batch preprocessing functions

---

## Supported File Types

| Extension   | Handler Function            | Method           |
|-------------|-----------------------------|------------------|
| `.pdf`      | `extract_text_from_pdf()`   | PyMuPDF blocks   |
| `.png`, `.jpg`, `.jpeg` | `extract_text_from_image()` | Tesseract OCR     |
| `.docx`     | `extract_text_from_docx()`  | python-docx      |
| `.txt`      | `extract_text_from_txt()`   | Basic file read  |

---

## Key Functions

### `preprocess_document(file_path, doc_id)`
- Detects file type and delegates to the correct extractor
- Splits the extracted text into cleaned chunks (`\n` delimited)
- Calls `remove_doc_from_index(doc_id)` and then `add_chunks_to_index()`, both function are related to `vector_store.py`

### `preprocess_batch(file_paths)`
- Processes multiple files in sequence
- Skips failed documents but logs the error
- Returns a list of successfully processed `doc_id`s

---

## 🔍 Extraction Behavior

- **PDFs:** Extracted block by block using `page.get_text("blocks")`, with newlines stripped for paragraph cohesion.
- **Images:** Processed using `pytesseract.image_to_string()` with `--psm 6` for better structure; double-spaced lines inferred as paragraphs.
- **DOCX:** All non-empty paragraphs concatenated.
- **TXT:** Raw text read from file, no transformation.

---

## 🔗 Dependencies

- `PyMuPDF`, `pytesseract`, `Pillow`, `docx`, `shutil`, `os`, `typing`
- `add_chunks_to_index()` and `remove_doc_from_index()` from `vector_store.py`
- `logger` from `core/logger.py` for structured logs

---

## Notes

- Document ID (`doc_id`) is in the format `session_id:filename`:
  - `session_id` is the unique identifier for the user's current session, which is stored in the browser's `localStorage`
  - `filename` is the original name of the uploaded file (including its extension)
  - This format ensures that:
      - Each document is uniquely identifiable even if users upload files with the same name
      - It prevents collisions across sessions in both storage and vector index references
- Chunks are stripped and filtered to remove empty lines.
- Designed to avoid reprocessing by clearing old FAISS entries first.

---

## Related Modules
`vector_store.py` – adds/removes embeddings based on chunked text

`pipeline_routes.py` – calls `preprocess_batch()` during analysis

