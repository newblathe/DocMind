from fastapi import Request, APIRouter, HTTPException

from backend.app.core.limiter import limiter

from backend.app.core.config import UPLOAD_DIR
from backend.app.services.document_preprocessor import preprocess_batch
from backend.app.services.query_engine import extract_answers_from_docs
from backend.app.services.theme_identifier import extract_themes
from backend.app.services.vector_store import is_document_indexed
from backend.app.models.models import PipelineResponse, PipelineInput
from backend.app.core.logger import logger

import os
from pathlib import Path

router = APIRouter()

@router.post("/run-pipeline", summary="Run analysis on uploaded documents", response_model=PipelineResponse)
@limiter.shared_limit("100/minute", scope="global")
def run_pipeline(request: Request, payload: PipelineInput):
    """
    Runs the end-to-end pipeline:
    - Preprocesses the newly uploaded docuemnts.
    - Extracts answers and citations per document
    - Generates theme-based summary of answers

    Parameters:
        question (str): The user-provided question to extract answers from the documents

    Raises:
        HTTPException: If no questions or documents are provided.

    Returns:
        PipelineResponse: Contains answers per document and a thematic summary
    """
    # Collect valid document file paths from the upload directory
    file_paths = [
        str(UPLOAD_DIR / f)
        for f in os.listdir(UPLOAD_DIR)
        if f.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg', '.txt', '.docx'))
    ]

    # Handle no files
    if not file_paths:
        logger.warning("Pipeline triggered, but no documents were found.")
        raise HTTPException(status_code=400, detail="No documents provided for analysis.")
    
    # Handle no question
    if not payload.question.strip() or not payload.question:
        logger.warning("Pipeline triggered without a question.")
        raise HTTPException(status_code=400, detail="No question provided for analysis.")

    logger.info(f"Pipeline started for question: {payload.question}")
    logger.info(f"Total files in upload directory: {len(file_paths)}")


    try:
        # Preprocess
        doc_ids = []
        # Filter and preprocess only new documents
        docs_to_preprocess = []
        for path in file_paths:
            doc_id = os.path.basename(path)
            doc_ids.append(doc_id)

            if not is_document_indexed(doc_id):
                docs_to_preprocess.append(path)
        
        logger.info(f"{len(docs_to_preprocess)} document(s) need preprocessing.")

        if docs_to_preprocess:
            logger.info(f"Preprocessing files: {docs_to_preprocess}")
            preprocess_batch(docs_to_preprocess)

        # Extract answers
        logger.info("Extracting answers from documents...")
        answers = extract_answers_from_docs(payload.question, doc_ids)
        logger.info(f"Extraction complete. {len(answers)} answers returned.")

        # Generate themes
        logger.info("Generating thematic summary...")
        themes = extract_themes(answers)
        logger.info("Theme extraction complete.")

        return PipelineResponse(answers = answers, themes=themes)
    except Exception as e:
        logger.error(f"Pipeline failed with exception: {e}", exc_info=True)
        return PipelineResponse(answers=[], themes=f"Pipeline failed: {str(e)}")
