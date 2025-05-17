import pytest
import sys
from pathlib import Path

# Add the project root directory to the Python path to enable relative imports
sys.path.append(str(Path(__file__).resolve().parents[1]))

# Import the extract_answers_from_docs function from the services module
from backend.app.services.query_engine import extract_answers_from_docs




def test_query_engine():
    """
    Unit test for the `extract_answers_from_docs` function.

    This test ensures that Groq's LLM can process a batch of sample documents
    and return relevant answers and citations based on a strategic user query.

    The test does the following:
    - Provides a synthetic list of 10 document dicts with sample content.
    - Passes them along with a user query to the `extract_answers_from_docs` pipeline.
    - Prints document-wise answers and citations for visual inspection.
    """

    # Define the user query to ask about strategic direction
    user_question = "What strategic direction or change is proposed in the document?"

    # Sample preprocessed documents simulating actual inputs
    sample_documents = [
    {
        "doc_id": "DOC001",
        "text": "Section 2 of the department report outlines a major shift in strategy for Q2.\n\nThe company plans to transition from a service-based model to a hybrid model by the end of fiscal year 2021.\n\nThis change is expected to impact cross-functional workflows and client delivery cycles."
    },
    {
        "doc_id": "DOC002",
        "text": "Section 2 of the department report outlines a major shift in strategy for Q3.\n\nThe company plans to transition from a service-based model to a hybrid model by the end of fiscal year 2022.\n\nThis change is expected to impact cross-functional workflows and client delivery cycles."
    },
    {
        "doc_id": "DOC003",
        "text": "Section 2 of the department report outlines a major shift in strategy for Q4.\n\nThe company plans to transition from a service-based model to a hybrid model by the end of fiscal year 2023.\n\nThis change is expected to impact cross-functional workflows and client delivery cycles."
    },
    {
        "doc_id": "DOC004",
        "text": "Section 2 of the department report outlines a major shift in strategy for Q1.\n\nThe company plans to transition from a service-based model to a hybrid model by the end of fiscal year 2024.\n\nThis change is expected to impact cross-functional workflows and client delivery cycles."
    },
    {
        "doc_id": "DOC005",
        "text": "Section 2 of the department report outlines a major shift in strategy for Q2.\n\nThe company plans to transition from a service-based model to a hybrid model by the end of fiscal year 2020.\n\nThis change is expected to impact cross-functional workflows and client delivery cycles."
    },
    {
        "doc_id": "DOC006",
        "text": "Section 2 of the department report outlines a major shift in strategy for Q3.\n\nThe company plans to transition from a service-based model to a hybrid model by the end of fiscal year 2021.\n\nThis change is expected to impact cross-functional workflows and client delivery cycles."
    },
    {
        "doc_id": "DOC007",
        "text": "Section 2 of the department report outlines a major shift in strategy for Q4.\n\nThe company plans to transition from a service-based model to a hybrid model by the end of fiscal year 2022.\n\nThis change is expected to impact cross-functional workflows and client delivery cycles."
    },
    {
        "doc_id": "DOC008",
        "text": "Section 2 of the department report outlines a major shift in strategy for Q1.\n\nThe company plans to transition from a service-based model to a hybrid model by the end of fiscal year 2023.\n\nThis change is expected to impact cross-functional workflows and client delivery cycles."
    },
    {
        "doc_id": "DOC009",
        "text": "Section 2 of the department report outlines a major shift in strategy for Q2.\n\nThe company plans to transition from a service-based model to a hybrid model by the end of fiscal year 2024.\n\nThis change is expected to impact cross-functional workflows and client delivery cycles."
    },
    {
        "doc_id": "DOC010",
        "text": "Section 2 of the department report outlines a major shift in strategy for Q3.\n\nThe company plans to transition from a service-based model to a hybrid model by the end of fiscal year 2020.\n\nThis change is expected to impact cross-functional workflows and client delivery cycles."
    }
]


    # Extract answers for each of the documents
    results = extract_answers_from_docs(user_question, sample_documents)

    # Print results for manual verification
    for r in results:
        print(f"\n{r['doc_id']}\nAnswer: {r['answer']}\nCitation: {r['citation']}")
