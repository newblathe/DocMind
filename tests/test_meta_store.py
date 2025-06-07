import sys
from pathlib import Path

# Ensure the backend modules are importable by adding the project root to sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import numpy as np
from backend.app.services.meta_store import add_to_metadata, search_top_k_chunks, remove_from_metadata, is_document_indexed


def test_meta_store():
    """
    Tests the vector indexing pipeline:
    1. Adds text chunks to the test session-specific metadata
    2. Verifies if the document is indexed
    3. Queries top matching chunks
    4. Removes the document and confirms cleanup
    """
    # Use a test-specific session and document ID
    session_id = "test_vector_store"
    doc_id = "test_doc"

    # Example chunks to embed and index
    chunks = [
        "Machine learning enables systems to improve their performance over time without being explicitly reprogrammed. By leveraging large datasets and statistical techniques, these systems can identify patterns and make decisions with minimal human intervention.",

        "Neural networks are computational models inspired by the human brain. They consist of layers of interconnected nodes and are capable of learning complex functions by adjusting the weights of connections through backpropagation and gradient descent.",

        "Natural language processing allows machines to interpret and generate human language. It powers applications like language translation, voice assistants, and intelligent text summarization tools that are widely used in everyday applications.",

        "The history of classical music includes composers like Bach, Beethoven, and Mozart, who each contributed to different stylistic periods. Their compositions continue to influence modern orchestral works and are frequently performed around the world.",

        "Urban gardening has grown in popularity as people seek to grow vegetables and herbs in small spaces. Techniques such as vertical planting and hydroponics make it possible to maintain gardens even in densely populated areas."
    ]

    # Step 1: Add chunks to the metadata
    add_to_metadata(session_id, doc_id, chunks)

    # Step 2: Confirm that the document was indexed
    assert is_document_indexed(session_id, doc_id), f"Document {doc_id} was not found in the session metadata after insertion."

    # Step 3: Run a semantic search query on the document
    query = "What is machine learning?"
    results = search_top_k_chunks(session_id, doc_id, query, k=2)

    print("\nRetrieved Chunks:")
    for idx, r in enumerate(results):
        print(f"{idx+1} Chunk Text: {r['text']}\n")

    # Ensure relevant chunks are returned
    assert len(results) == 2, f"Expected 2 top results from search, but got {len(results)}."
    assert any("machine learning" in r["text"].lower() for r in results), "Search results do not contain any chunk related to 'machine learning'. Semantic relevance may be broken."

    # Step 4: Remove document from the metadata
    remove_from_metadata(session_id, doc_id)

    # Verify that the document is no longer indexed
    assert not is_document_indexed(session_id, doc_id), f"Document {doc_id} should have been removed from the metadata, but it's still present."
