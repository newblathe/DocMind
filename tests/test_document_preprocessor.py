import os

import sys
from pathlib import Path

# Add the project root directory to the Python path to enable relative imports
sys.path.append(str(Path(__file__).resolve().parents[1]))

# Import the preprocess_batch function from the services module
from backend.app.services.document_preprocessor import preprocess_batch

def test_document_preprocessor():

    """
    Unit test for the `preprocess_batch` function.

    This test checks whether PDF and image documents are correctly preprocessed
    into structured text output for downstream analysis.

    It performs the following:
    - Loads sample PDF and image files from the `tests/test_docs` directory
    - Passes them to the preprocessing pipeline
    - Prints each preprocessed document's text for visual verification
    """

    # Define the path to the test documents
    test_dir = "tests/test_docs"

    # Define paths to individual test documents
    docx_path = os.path.join(test_dir, "hybrid_strategy.docx")
    img_path = os.path.join(test_dir, "announcement.jpg")
    pdf_path = os.path.join(test_dir, "work_model_plan.pdf")
    txt_path = os.path.join(test_dir, "strategy_note.txt")

    # Process the list of documents using the batch processor
    results = preprocess_batch([docx_path, pdf_path, img_path, txt_path])

    # Print the doc_id for the documents
    print(results)

test_document_preprocessor()