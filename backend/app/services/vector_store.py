import faiss
from pathlib import Path
import numpy as np
from typing import List, Dict
from sentence_transformers import SentenceTransformer
from collections import defaultdict
import hashlib

from backend.app.core.config import INDEX_PATH

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
    path = INDEX_PATH / session_id
    path.mkdir(parents=True, exist_ok=True)
    return path

def _index_path(session_id: str) -> Path:
    """
    Constructs the path to the FAISS index file for a given session.
    """
    return _session_dir(session_id) / "vector_index.faiss"

def _meta_path(session_id: str) -> Path:
    """
    Constructs the path to the metadata file for a given session.
    """
    return _session_dir(session_id) / "meta.npy"


def init_or_load_index(session_id: str):
    """
    Initializes or loads the FAISS index and metadata for a given session.

    Parameters:
        session_id (str): Session ID to isolate user data and results.

    Returns:
        Tuple of (FAISS index, metadata list, doc_id to faiss_id map).
    """
    index_file = _index_path(session_id)
    meta_file = _meta_path(session_id)

    # Load or initialize index
    if index_file.exists():
        index = faiss.read_index(str(index_file))
    else:
        base_index = faiss.IndexFlatL2(embedding_dim)
        index = faiss.IndexIDMap(base_index)

    # Load or initialize metadata
    if meta_file.exists():
        metadata = list(np.load(str(meta_file), allow_pickle=True))
    else:
        metadata = []

    # Mapping from doc_id to chunk FAISS IDs
    doc_chunk_faiss_ids: Dict[str, List[int]] = defaultdict(list)

    # Rebuild reverse mapping from doc_id to FAISS chunk IDs
    for meta in metadata:
        doc_chunk_faiss_ids[meta["doc_id"]].append(meta["faiss_id"])

    return index, metadata, doc_chunk_faiss_ids


def _generate_faiss_id(doc_id: str, chunk_index: int) -> int:
    """
    Generates a unique and consistent FAISS ID for a chunk.

    Parameters:
        doc_id: The document ID the chunk belongs to.
        chunk_index: The index of the chunk within the document.

    Returns:
        Integer FAISS ID.
    """
    hash_input = f"{doc_id}_chunk_{chunk_index}"
    return int(hashlib.md5(hash_input.encode()).hexdigest()[:12], 16) % (10**9)

def save_index(session_id: str, index, metadata):
    """
    Saves the FAISS index and metadata to disk for the specified session.

    Parameters:
        session_id (str): Session ID to isolate user data and results.
        index: FAISS index object.
        metadata: List of metadata dictionaries.
    """
    faiss.write_index(index, str(_index_path(session_id)))
    np.save(str(_meta_path(session_id)), metadata)

def add_chunks_to_index(session_id: str, doc_id: str, chunks: List[str]) -> None:
    """
    Embeds and adds chunks of a document to the FAISS index and updates metadata.

    Parameters:
        session_id (str): Session ID to isolate user data and results.
        doc_id: Unique ID of the document.
        chunks: List of text chunks extracted from the document.
    """
    index, metadata, doc_chunk_faiss_ids = init_or_load_index(session_id)
    embeddings = model.encode(chunks).astype("float32")
    faiss_ids = [_generate_faiss_id(doc_id, i) for i in range(len(chunks))]

    index.add_with_ids(embeddings, np.array(faiss_ids))

    for i, text in enumerate(chunks):
        metadata.append({
            "session_id": session_id,
            "doc_id": doc_id,
            "chunk_index": i,
            "faiss_id": faiss_ids[i],
            "text": text,
            "embedding": embeddings[i]
        })
        doc_chunk_faiss_ids[doc_id].append(faiss_ids[i])

    save_index(session_id, index, metadata)

def remove_doc_from_index(session_id: str, doc_id: str) -> None:
    """
    Remove all chunks associated with a document from the index.

    Parameters:
    - session_id (str): Session ID to isolate user data and results.
    - doc_id (str): ID of the document to remove.
    """
    index, metadata, doc_chunk_faiss_ids = init_or_load_index(session_id)

    if doc_id not in doc_chunk_faiss_ids:
        return

    ids_to_remove = np.array(doc_chunk_faiss_ids[doc_id])
    index.remove_ids(ids_to_remove)
    metadata[:] = [m for m in metadata if m["faiss_id"] not in ids_to_remove]

    save_index(session_id, index, metadata)


def search_top_k_chunks(session_id: str, doc_id: str, query: str, k: int = 3) -> List[Dict[str, str]]:
    """
    Returns the top-k relevant chunks from a specific document using FAISS similarity search.

    Parameters:
    - session_id (str): Session ID to isolate user data and results.    
    - doc_id (str): The document ID to search within.
    - query (str): The user query.
    - k (int): Number of top matching chunks to return.

    Returns:
    - List of chunk metadata dictionaries.
    """
    _, metadata, _ = init_or_load_index(session_id)
    doc_meta = [m for m in metadata if m["doc_id"] == doc_id]
    if not doc_meta:
        return []

    query_vec = model.encode([query]).astype("float32")
    vectors = np.array([m["embedding"] for m in doc_meta]).astype("float32")

    temp_index = faiss.IndexFlatL2(embedding_dim)
    temp_index.add(vectors)
    _, I = temp_index.search(query_vec, k)

    return [doc_meta[i] for i in I[0] if i < len(doc_meta)]

def is_document_indexed(session_id:str, doc_id: str) -> bool:
    """
    Checks whether a document has already been indexed in FAISS vector store.

    This prevents redundant reprocessing by verifying if the documents chunks are already stored and searchable.

    Parameters:
    - session_id (str): Session ID to isolate user data and results.
    - doc_id (str): The document ID

    Returns:
        bool: True if document is already indexed , False otherwise
    """
    _, _, doc_chunk_faiss_ids = init_or_load_index(session_id)
    return doc_id in doc_chunk_faiss_ids
