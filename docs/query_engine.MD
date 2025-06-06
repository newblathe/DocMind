# `query_engine.py`

This module defines the core logic for extracting answers from documents using a **Retrieval-Augmented Generation (RAG)** pipeline powered by **Groq LLM**.

---

## Responsibilities

- Embed and semantically search chunks for each document via FAISS
- Generate answers from top-k retrieved chunks using Groq's LLM
- Return detailed, clause-preserving responses along with paragraph-level citations

---

## Core Function

### `extract_answers_from_docs(session_id: str, user_query: str, doc_ids: List[str]) -> List[Dict[str, str]]`

Given the session_id, a user question and a list of document IDs:

1. Retrieves top-k chunks per document using FAISS
2. Constructs a detailed system prompt including:
   - Chunk texts
   - Paragraph references
   - The user’s question
3. Sends the prompt to **Groq LLM**
4. Parses the LLM's response (JSON only)
5. Returns answers and citations for each document

---

## Prompt Design

The prompt sent to Groq instructs the LLM to:

- Extract **full, unmodified clauses, sections, and references**
- Avoid paraphrasing or summarizing legal/technical terms
- Return a strict JSON format:
  ```json
  {"answer":"...","citation":"Para X"}
Citation Extraction \
Each paragraph is referenced as [Para X] in the search prompt

The LLM is instructed to cite the specific paragraph(s)

Invalid responses or “no relevant information” are gracefully handled

## Dependencies
- `Groq – LLM client` (llama-3.3-70b-versatile used)

- `search_top_k_chunks()` from `vector_store.py` – for semantic chunk retrieval

- `config.GROQ_API_KEY` – pulled from .env

- `logger` from `logger.py` for structured logging

- `re`, `json`, `tabulate` – for response validation and formatting

## Notes
- Responses are forced into valid JSON with RegEx pre-checking

- Empty or badly formatted responses are skipped with warnings

- Errors are logged and do not crash the pipeline

## Related Modules
`vector_store.py` – Provides `search_top_k_chunks`

`pipeline_routes.py` – Calls this function during analysis

`theme_identifier.py` – Uses results from this module to extract themes
