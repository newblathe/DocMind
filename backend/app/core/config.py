import os
from pathlib import Path
from dotenv import load_dotenv

# Load from .env file
load_dotenv()

# File/Directory Constants
UPLOAD_DIR = Path("backend/data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

INDEX_PATH = Path("backend/data/vector_store")
INDEX_PATH.mkdir(parents=True, exist_ok=True)

META_PATH = Path("backend/data/vector_store")
META_PATH.mkdir(parents=True, exist_ok=True)

INDEX_FILE = INDEX_PATH / "vector_index.faiss"
META_FILE = META_PATH / "vector_metadata.npy"


# Environment Variables
def get_env_variable(key: str) -> str:
    value = os.getenv(key)
    if value is None:
        raise EnvironmentError(f"Environment variable '{key}' is required but not set.")
    return value

GROQ_API_KEY = get_env_variable("GROQ_API_KEY")
