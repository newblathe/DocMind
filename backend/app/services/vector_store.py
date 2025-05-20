import faiss
import numpy as np
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import os
from collections import defaultdict
import hashlib

from backend.app.core.config import INDEX_FILE, META_FILE

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")
embedding_dim = 384

# Initialize FAISS index with ID support
if os.path.exists(INDEX_FILE):
    index = faiss.read_index(str(INDEX_FILE))
else:
    base_index = faiss.IndexFlatL2(embedding_dim)
    index = faiss.IndexIDMap(base_index)

# Load or initialize metadata
if os.path.exists(META_FILE):
    metadata = list(np.load(str(META_FILE), allow_pickle=True))
else:
    metadata = []

# Mapping from doc_id to chunk FAISS IDs
doc_chunk_faiss_ids: Dict[str, List[int]] = defaultdict(list)

# Rebuild reverse mapping from doc_id to FAISS chunk IDs
for meta in metadata:
    doc_chunk_faiss_ids[meta["doc_id"].split("_chunk_")[0]].append(meta["faiss_id"])

def _generate_faiss_id(doc_id: str, chunk_index: int) -> int:
    """Generate a consistent integer ID for a given doc and chunk."""
    hash_input = f"{doc_id}_chunk_{chunk_index}"
    return int(hashlib.md5(hash_input.encode()).hexdigest()[:12], 16) % (10**9)

def add_chunks_to_index(doc_id: str, chunks: List[str]) -> None:
    """
    Adds embedded chunks to the FAISS index and stores metadata.

    Parameters:
    - doc_id (str): Unique identifier for the document.
    - chunks (List[str]): List of paragraph/sentence chunks.
    """

    embeddings = model.encode(chunks).astype("float32")
    faiss_ids = [_generate_faiss_id(doc_id, i) for i in range(len(chunks))]

    index.add_with_ids(embeddings, np.array(faiss_ids))

    for i, text in enumerate(chunks):
        meta = {
            "doc_id": doc_id,
            "chunk_index": i,
            "faiss_id": faiss_ids[i],
            "text": text,
            "embedding": embeddings[i]
        }
        metadata.append(meta)
        doc_chunk_faiss_ids[doc_id].append(faiss_ids[i])

    faiss.write_index(index, str(INDEX_FILE))
    np.save(str(META_FILE), metadata)

def remove_doc_from_index(doc_id: str) -> None:
    """
    Remove all chunks associated with a document from the index.

    Parameters:
    - doc_id (str): ID of the document to remove.
    """
    if doc_id not in doc_chunk_faiss_ids:
        return

    ids_to_remove = np.array(doc_chunk_faiss_ids[doc_id])
    index.remove_ids(ids_to_remove)

    # Remove from metadata
    global metadata
    metadata = [m for m in metadata if m["faiss_id"] not in ids_to_remove]
    del doc_chunk_faiss_ids[doc_id]

    faiss.write_index(index, str(INDEX_FILE))
    np.save(str(META_FILE), metadata)

def search_top_k_chunks(doc_id: str, query: str, k: int = 3) -> List[Dict[str, str]]:
    """
    Returns the top-k relevant chunks from a specific document using FAISS similarity search.

    Parameters:
    - doc_id (str): The document ID to search within.
    - query (str): The user query.
    - k (int): Number of top matching chunks to return.

    Returns:
    - List of chunk metadata dictionaries.
    """
    if doc_id not in doc_chunk_faiss_ids:
        return []

    query_vec = model.encode([query]).astype("float32")
    
    # Filter metadata for this doc and get their vectors
    doc_meta = [m for m in metadata if m["doc_id"] == doc_id]
    vectors = np.array([m["embedding"] for m in doc_meta]).astype("float32")
    local_index = faiss.IndexFlatL2(embedding_dim)
    local_index.add(vectors)

    D, I = local_index.search(query_vec, k)
    top_k = [doc_meta[i] for i in I[0] if i < len(doc_meta)]
    return top_k

def is_document_indexed(doc_id: str) -> bool:
    """
    Checks whether a document has already been indexed in FAISS vector store.

    This prevents redundant reprocessing by verifying if the documents chunks are already stored and searchable.

    Args:
        doc_id (str): The document ID

    Returns:
        bool: True if document is already indexed , False otherwise
    """
    return doc_id in doc_chunk_faiss_ids
