import faiss
from pathlib import Path
import numpy as np
from typing import List, Dict, Union
from sentence_transformers import SentenceTransformer

from backend.app.core.config import META_PATH

# # Load the embedding model used to convert text into vector representations
model = SentenceTransformer("all-MiniLM-L6-v2")
embedding_dim = 384

# Path Setup
def _session_dir(session_id: str) -> Path:
    """
    Returns the path to the session-specific directory, creating it if needed.

    Parameters:
        session_id (str): Session ID to isolate user data and results.

    Returns:
        Path object for the session directory.
    """
    path = META_PATH / session_id
    path.mkdir(parents=True, exist_ok=True)
    return path

def _meta_path(session_id: str) -> Path:
    """
    Constructs the path to the metadata file for a given session.
    """
    return _session_dir(session_id) / "meta.npy"


# Load existing metadata for a session or initializes a new empty dictionary
def init_or_load_metadata(session_id: str) -> Dict[str, Dict[str, List]]:
    """
    Initializes or loads metadata for a given session.

    Parameters:
        session_id (str): Session ID to isolate user data and results.

    Returns:
        A dictionary containng the metada for each session specific document
    """
    meta_file = _meta_path(session_id)
    if meta_file.exists():
        return np.load(str(meta_file), allow_pickle=True).item()
    return {}



# Persist metadata to disk for the current session
def save_metadata(session_id: str, metadata: Dict[str, Dict[str, List]]) -> None:
    """
    Saves the FAISS index and metadata to disk for the specified session.

    Parameters:
        session_id (str): Session ID to isolate user data and results.
        index: FAISS index object.
        metadata: List of metadata dictionaries.
    """
    # Persist the updated metadata to disk
    np.save(str(_meta_path(session_id)), metadata)


# Add text chunks and their embeddings to the session-specific metadata
def add_to_metadata(session_id: str, doc_id: str, chunks: List[str]) -> None:
    """
    Add document chunks and their embeddings to session metadata.

    Parameters:
        session_id (str): Session ID to isolate user data and results.
        doc_id: Unique ID of the document.
        chunks: List of text chunks extracted from the document.
    """
    metadata = init_or_load_metadata(session_id)
    
    # Generate vector embeddings for the chunks
    embeddings = model.encode(chunks).astype("float32")

    # Save both chunks and embeddings under the document's ID
    metadata[doc_id] = {
        "chunks": chunks,
        "embeddings": embeddings
    }

    save_metadata(session_id, metadata)
    metadata = init_or_load_metadata(session_id)
    print(metadata.keys())


# Delete all metadata associated with a specific document in a session
def remove_from_metadata(session_id: str, doc_id: str) -> None:
    """
    Remove document chunks and thier embeddings from the session metadata

    Parameters:
    - session_id (str): Session ID to isolate user data and results.
    - doc_id (str): ID of the document to remove.
    """
    metadata = init_or_load_metadata(session_id)
    

    if doc_id in metadata:
        # Delete entry for the document
        del metadata[doc_id]
        save_metadata(session_id, metadata)
    metadata = init_or_load_metadata(session_id)
    print(metadata.keys())

# Searche the most relevant chunks in a document using semantic similarity
def search_top_k_chunks(session_id: str, doc_id: str, query: str, k: int = 3) -> List[Dict[str, Union[str, int]]]:
    """
    Returns the top-k relevant chunks from a specific document using FAISS similarity search.

    Parameters:
    - session_id (str): Session ID to isolate user data and results.    
    - doc_id (str): The document ID to search within.
    - query (str): The user query.
    - k (int): Number of top matching chunks to return.

    Returns:
    - List of dictionaries with chunk_index and text of the matching chunks
    """
    metadata = init_or_load_metadata(session_id)
    
    # Prepare data for temporary FAISS search
    chunks = metadata[doc_id]["chunks"]
    embeddings = np.array(metadata[doc_id]["embeddings"]).astype("float32")

    # Encode the query
    query_vec = model.encode([query]).astype("float32")

    # Perform temporary in-memory FAISS search
    temp_index = faiss.IndexFlatL2(embedding_dim)
    temp_index.add(embeddings)
    _, I = temp_index.search(query_vec, k)

    # Return the top matching chunks with their indices
    return [
        {
            "chunk_index": int(i),
            "text": chunks[i]
        }
        for i in I[0] if i < len(chunks)
    ]

# Check whether a specific document has been stored in the metadata for the given session
def is_document_indexed(session_id:str, doc_id: str) -> bool:
    """
    Checks whether a document'chunks and embeddings are already in the metadata.

    This prevents redundant reprocessing by verifying if the documents chunks are already stored and searchable.

    Parameters:
    - session_id (str): Session ID to isolate user data and results.
    - doc_id (str): The document ID

    Returns:
        bool: True if document is already in the metadata , False otherwise
    """
    metadata = init_or_load_metadata(session_id)
    return doc_id in metadata
