# `config.py`

This module handles all static path configuration and environment variable loading for the DocMind backend. It ensures required folders exist and critical secrets are loaded securely.

---

## Responsibilities

- Load environment variables from `.env` using `python-dotenv`
- Define persistent directories:
  - `uploads/` for raw uploaded files
  - `vector_store/` for FAISS index and metadata
- Create missing folders automatically on startup
- Provide a safe way to retrieve sensitive config like `GROQ_API_KEY`

---

## Constants Defined

| Constant       | Description                            |
|----------------|----------------------------------------|
| `UPLOAD_DIR`   | Folder path for uploaded documents      |
| `INDEX_PATH`   | Folder path for FAISS index             |
| `META_PATH`    | Folder path for chunk metadata storage  |
| `INDEX_FILE`   | File path for saved FAISS index         |
| `META_FILE`    | File path for saved chunk metadata      |

---

## Environment Loading

- Uses `load_dotenv()` to pull values from a `.env` file
- Provides `get_env_variable(key: str)` helper:
  - Raises an error if the key is missing
  - Used for secure loading of the Groq API key

```python
GROQ_API_KEY = get_env_variable("GROQ_API_KEY")
```