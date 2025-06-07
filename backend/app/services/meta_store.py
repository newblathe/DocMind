from pymongo import MongoClient
import faiss
import numpy as np
from typing import List, Dict, Union
from sentence_transformers import SentenceTransformer

from backend.app.core.config import MONGO_URL

# MongoDB connection
client = MongoClient(MONGO_URL)
db = client["docmind_metadata"]
collection = db["sessions"]

# Load the embedding model used to convert text into vector representations
model = SentenceTransformer("all-MiniLM-L6-v2")
embedding_dim = 384

# Utility to safely store document IDs in MongoDB keys
def normalize_doc_id(doc_id: str) -> str:
    """
    Normalizes a document ID by replacing the last '.' with an underscore,
    avoiding MongoDB's nested key interpretation issues.

    Parameters:
        doc_id (str): The original document id
    
    Returns:
        str: Normalized document id
    """
    return doc_id.replace(".", "_")


# Add text chunks and their embeddings to the session-specific metadata
def add_to_metadata(session_id: str, doc_id: str, chunks: List[str]) -> None:
    """
    Stores text chunks and their vector embeddings into MongoDB
    under the corresponding session and document ID.

    Parameters:
        session_id (str): Session ID to isolate user data and results.
        doc_id: Unique ID of the document.
        chunks: List of text chunks extracted from the document.
    """
    
    # Generate vector embeddings for the chunks
    embeddings = model.encode(chunks).astype("float32").tolist()

    
    
    
    # Update or insert the document inside the session's "documents"
    normalized_doc_id = normalize_doc_id(doc_id)
    collection.update_one(
        {"session_id": session_id},
        {
            "$set": {
                f"documents.{normalized_doc_id}": {
                    "chunks": chunks,
                    "embeddings": embeddings
                }
            }
        },
        upsert=True
    )


# Delete all metadata associated with a specific document in a session
def remove_from_metadata(session_id: str, doc_id: str) -> None:
    """
    Deletes a document’s chunks and embeddings from the metadata store.

    Parameters:
    - session_id (str): Session ID to isolate user data and results.
    - doc_id (str): ID of the document to remove.
    """
    normalized_doc_id = normalize_doc_id(doc_id)
    
    collection.update_one(
        {"session_id": session_id},
        {"$unset": {f"documents.{normalized_doc_id}": ""}}
    )

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
    normalized_doc_id = normalize_doc_id(doc_id)
    
    doc = collection.find_one({"session_id": session_id})
    if not doc or normalized_doc_id not in doc.get("documents", {}):
        return []

    doc_data = doc["documents"][normalized_doc_id]
    chunks = doc_data["chunks"]
    embeddings = np.array(doc_data["embeddings"]).astype("float32")

    query_vec = model.encode([query]).astype("float32")
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    _, I = index.search(query_vec, k)

    return [
        {"chunk_index": int(i), "text": chunks[i]}
        for i in I[0] if i < len(chunks)
    ]

# Check whether a specific document has been stored in the metadata for the given session
def is_document_indexed(session_id:str, doc_id: str) -> bool:
    """
    Checks whether the document is already stored in the MongoDB metadata.

    This prevents redundant reprocessing by verifying if the documents chunks are already stored and searchable.

    Parameters:
    - session_id (str): Session ID to isolate user data and results.
    - doc_id (str): The document ID

    Returns:
        bool: True if document is already in the metadata , False otherwise
    """
    normalized_doc_id = normalize_doc_id(doc_id)

    return collection.find_one(
        {"session_id": session_id, f"documents.{normalized_doc_id}": {"$exists": True}}
    ) is not None
