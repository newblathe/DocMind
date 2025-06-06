import sys
from pathlib import Path

# Ensure the backend modules are importable by adding the project root to sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import os
from backend.app.services.document_preprocessor import preprocess_batch
from backend.app.services.query_engine import extract_answers_from_docs
from backend.app.services.theme_identifier import extract_themes



def test_full_document_pipeline():
    """
    Full pipeline test: Preprocessing → Query Answering → Theme Extraction.
    Uses documents from `tests/test_docs` and prints all intermediate results.
    """
    print("Running full document analysis pipeline...")


    # Use a test-specific session_id
    session_id = "test_full_doc_pipleine"

    # Step 1: Preprocessing
    test_dir = "test_docs"
    file_paths = [
        os.path.join(test_dir, f)
        for f in os.listdir(test_dir)
        if f.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg', '.txt', '.docx'))
    ]

    processed_doc_ids = preprocess_batch(session_id, file_paths)
    print(f"\nProcessed Document IDs:\n{processed_doc_ids}")
    assert processed_doc_ids, "No documents were successfully preprocessed. Check file paths or preprocessing logic."

    # Step 2: Answer Extraction
    question = "What strategic direction or change is proposed in the document?"
    answers = extract_answers_from_docs(session_id, question, processed_doc_ids)

    print("\nExtracted Answers:")
    for ans in answers:
        print(f"- {ans['doc_id']}: {ans['answer']} (Citation: {ans['citation']})\n")
    assert answers, "No answers were generated for the query. LLM or retrieval pipeline may have failed."

    # Step 3: Theme Extraction
    themes = extract_themes(answers)
    print(f"\nExtracted Themes:\n{themes}")
    assert isinstance(themes, str) and len(themes.strip()) > 0, "Theme extraction returned an empty or invalid result. Expected a non-empty string."