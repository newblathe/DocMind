# Tests Documentation


## Prerequisites

Make sure `pytest` is installed before running tests:

```bash
pip install pytest
```

---

## Running Tests

To execute all tests:

```bash
pytest tests/
```

To run a specific test file:

```bash
pytest tests/test_meta_store.py
```
or

```bash
pytest tests/test_full_doc_pipeline.py
```

---

## Test Directory Structure

<pre><code>root_dir/
├── tests/
    ├── test_docs/                  # Sample test documents (PDF, TXT, etc.)
    ├── test_full_doc_pipeline.py   # End-to-end test of the complete document analysis pipeline
    ├── test_meta_store.py          # Isolated test for vector store logic (FAISS indexing)
    └── backend/                    # (Auto-created during test execution)
        └── data/
            ├── upload/             # Not used during tests
            └── vector_store/       # Test-specific vector indexes</code></pre>

---

## Test files Overview

`test_full_doc_pipeline.py`

**Purpose**: Performs an end-to-end test of the document analysis pipeline.

**Flow**:

- Loads documents from tests/test_docs.

- Runs preprocess_batch to extract and index document chunks.

- Sends a query to the extract_answers_from_docs pipeline.

- Extracts themes from the answers using extract_themes.

**Assertions**: Checks that document IDs are returned, answers are generated, and themes are non-empty.

**Note**: Uses print statements to show intermediate results for debugging and visibility.

`test_meta_store.py`

**Purpose**: Tests the session-scoped metadata functionality in isolation.

**Flow**:

- Adds a list of 5 sample paragraph chunks to the metadata.

- Verifies that the document was successfully indexed.

- Performs a semantic query and validates the relevance of the returned results.

- Deletes the simulated document and confirms that it is removed from the metadata.

**Assertions**: Ensures the correct number of chunks are returned and validates their content.

---

## Session Isolation
- Both tests use unique session_ids (`test_meta_store`, `test_full_doc_pipeline`).

- FAISS index files and metadata are saved in `tests/backend/data/meta_store/{session_id}` during tests.

- These paths are automatically created and do not affect the production data or real application state.

---

## Upload Directory Usage
The backend/data/upload/ directory is not used or populated during test execution.

All document paths are directly loaded from the tests/test_docs/ folder for full control and consistency.

## Clean-Up
No automatic cleanup of metadata is implemented in the tests. You can periodically clear `tests/backend/data/meta_store/` to reset test state if needed.