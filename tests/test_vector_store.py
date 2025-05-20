import sys
from pathlib import Path

# Add the project root to the Python path so local modules can be imported
sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.app.services.vector_store import add_chunks_to_index, remove_doc_from_index, search_top_k_chunks, is_document_indexed

# Step 1: Simulate adding a document
doc_id = "TESTDOC001"
chunks = [
    "Clause 1: This document outlines the financial strategy for 2024.",
    "Clause 2: The company will focus on cost reduction and hybrid work.",
    "Clause 3: Compliance with SEBI Clause 49 is required.",
    "Clause 4: We expect a 15% increase in efficiency through automation."
]

# Add chunks to FAISS and metadata
if not is_document_indexed(doc_id):
    remove_doc_from_index(doc_id)
    add_chunks_to_index(doc_id, chunks)
    print("preprocessing")

# Step 2: Query the index
query = "What is the strategy for 2024?"
top_results = search_top_k_chunks(doc_id, query, k=3)

# Step 3: Display results
print("\nTop-k relevant chunks:")
for i, result in enumerate(top_results):
    print(f"\nRank {i+1}:")
    print(f"Chunk Index: {result['chunk_index']}")
    print(f"Text: {result['text']}")