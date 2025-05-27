# `pipeline_routes.py`

This module defines the core pipeline endpoint in DocMind:  
**`POST /run-pipeline`** — which orchestrates document processing, question answering, and theme extraction.

---

## Responsibilities

- Handle `/run-pipeline` API call
- Collect all uploaded documents
- Preprocess new documents (extract, chunk, embed), skip documents that are already indexed
- Embed the user’s question and retrieve top-k chunks
- Use Groq LLM to:
  - Generate per-document answers
  - Extract cross-document themes

---

## Endpoint: `POST /run-pipeline`

**Summary:** Runs the full document analysis pipeline based on user question input.

**Request Body:**  
```json
{
  "question": "string"
}
```

**Response:**
```json
{
  "answers": [...],
  "themes": "thematic insights"
}
```

## Pipeline Flow
1. Load all valid documents from `UPLOAD_DIR/{session_id}/`

2. If no documents → return early with warning

3. If no question → return early with warning

4. For each document:

    - If not indexed → preprocess and index

    - If already indexed → skip preprocessing

5. Embed the question and retrieve top-k relevant chunks

6. Call Groq LLM to:

    - Generate answers from chunks

    - Extract themes from those answers

7. Return combined results

## Dependencies

- `UPLOAD_DIR` from `config.py`, base directory for uploaded files; the pipeline scans only the session-specific subfolder `UPLOAD_DIR/{session_id}/` to retrieve files.
- `is_document_indexed()` from `vector_store.py`, checks FAISS to avoid redundant embedding
- `preprocess_batch()` from `document_preprocessor.py`, extracts and chunks documents
- `extract_answers_from_docs()` from `query_engine.py`, calls LLM to generate answers
- `extract_themes()` from `theme_identifier.py`, summarizes themes from answers
- `PipelineInput`, `PipelineResponse` from `models.py`
- `logger` from `logger.py` for structured logging throughout execution

## Notes
- This route is protected with a global shared rate limiter. If a user exceeds the request threshold, the user will be redirected to a rate-limit warning page.
- Prevents concurrent analysis requests from the same client IP.
- Only documents with extensions: .pdf, .png, .jpg, .jpeg, .txt, .docx are processed.
- Handles empty document sets and missing questions gracefully.
- Catches and logs all exceptions with full trace.
