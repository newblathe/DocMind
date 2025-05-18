import os
import sys
from pathlib import Path
import argparse

# Add the project root directory to the Python path to enable relative imports
sys.path.append(str(Path(__file__).resolve().parents[1]))

# Local module imports from the services layer of the app
from backend.app.services.document_preprocessor import preprocess_batch
from backend.app.services.query_engine import extract_answers_from_docs
from backend.app.services.theme_identifier import extract_themes
from tabulate import tabulate


# Create a CLI parser for executing the pipeline with custom inputs
parser = argparse.ArgumentParser(description="Run end-to-end document analysis pipeline.")

# Add required arguments: folder path and user query
parser.add_argument("--folder", type=str, required=True, help="Path to folder containing PDFs/images")
parser.add_argument("--question", type=str, required=True, help="User question to extract answers for")

# Parse the command-line arguments
args = parser.parse_args()

# Extract arguments for use in the pipeline
folder = args.folder
user_question = args.question

# Collect file paths to all supported documents in the given folder
file_paths = [
    str(Path(folder) / f)
    for f in os.listdir(folder)
    if f.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg', '.docx', '.txt'))
]

# If no valid files found, exit early
if not file_paths:
    print("No supported documents found in folder.")
    sys.exit(1)

print(f"Found {len(file_paths)} files. Starting preprocessing...")

# Use the preprocess_batch function to extract text content from PDF/image files using OCR and text extraction
preprocessed_docs = preprocess_batch(file_paths)

# Use the extract_answers_from_docs function to answer the user-provided question per document, including citations
print("\nExtracting answers from documents...")
answers = extract_answers_from_docs(user_question, preprocessed_docs)

# Print tabular results
print("\nDocument-level Answers:")
print(tabulate(
    [[a['doc_id'], a['answer'], a['citation']] for a in answers],
    headers=["Document", "Answer", "Citation"],
    tablefmt="grid"
))

# Use the extract_themes function to synthesize a high-level summary of themes across all documents
print("\nExtracting Themes:")
common_themes = extract_themes(answers)

print("\nThemes:")
print(common_themes)

print("\nPipeline completed.")
