from fastapi import APIRouter, Query
from backend.app.core.config import UPLOAD_DIR
from backend.app.services.document_preprocessor import preprocess_batch
from backend.app.services.query_engine import extract_answers_from_docs
from backend.app.services.theme_identifier import extract_themes
from backend.app.models.models import PipelineResponse, PipelineInput

import os
from pathlib import Path

router = APIRouter()

@router.post("/run-pipeline", summary="Run analysis on uploaded documents", response_model=PipelineResponse)
def run_pipeline(payload: PipelineInput):
    """
    Runs the end-to-end pipeline:
    - Loads uploaded documents from the server's upload directory
    - Extracts answers and citations per document
    - Generates theme-based summary of answers

    Parameters:
    - question (str): The user-provided question to extract answers from the documents

    Returns:
    - PipelineResponse: Contains answers per document and a thematic summary
    """
    # Collect valid document file paths from the upload directory
    file_paths = [
        str(UPLOAD_DIR / f)
        for f in os.listdir(UPLOAD_DIR)
        if f.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg', '.txt', '.docx'))
    ]

    # Handle empty document case
    if not file_paths:
        return PipelineResponse(answers=[], themes="No documents found for processing.")

    try:
        # Preprocess
        preprocessed_docs = preprocess_batch(file_paths)

        # Extract answers
        answers = extract_answers_from_docs(payload.question, preprocessed_docs)

        # Generate themes
        themes = extract_themes(answers)

        return PipelineResponse(answers = answers, themes=themes)
    except Exception as e:
        return PipelineResponse(answers=[], themes=f"Pipeline failed: {str(e)}")