from fastapi import Request, APIRouter, HTTPException, Query

from backend.app.core.limiter import limiter

from backend.app.core.config import UPLOAD_DIR
from backend.app.services.document_preprocessor import preprocess_batch
from backend.app.services.query_engine import extract_answers_from_docs
from backend.app.services.theme_identifier import extract_themes
from backend.app.services.vector_store import is_document_indexed
from backend.app.models.models import PipelineResponse, PipelineInput
from backend.app.core.logger import logger

import os
import time

router = APIRouter()



@router.post("/run-pipeline", summary="Run analysis on uploaded documents", response_model=PipelineResponse)
@limiter.shared_limit("100/minute", scope="global")
async def run_pipeline(request: Request, *, session_id: str = Query(...), payload: PipelineInput):
    """
    Runs the end-to-end pipeline:
    - Preprocesses the newly uploaded docuemnts.
    - Extracts answers and citations per document
    - Generates theme-based summary of answers

    Parameters:
        request (Request): Request object used to access client IP for concurrency checks.
        session_id (str): Required session ID passed in the query to isolate user data and results.
        payload (PipelineInput): The input data containing the user question.

    Raises:
        HTTPException:
            - If no documents exists for the current session.
            - If no questions or documents are provided.
            - If no documents are selected for analysis

    Returns:
        PipelineResponse: Contains answers per document and a thematic summary.

    """
    # Handle no no files uploaded for the current session
    session_path = UPLOAD_DIR / session_id
    if not session_path.exists():
        logger.warning(f"No upload folder found for session {session_id}.")
        raise HTTPException(status_code=400, detail="No documents found for this session.")
    
    # Collect valid document file paths for this session only
    file_paths = [
        str(session_path / f)
        for f in (payload.selected_files or [])
        if f.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg', '.txt', '.docx'))
    ]

    # Handle no files selcted
    if not file_paths:
        logger.warning("No valid documents selected for analysis.")
        raise HTTPException(status_code=400, detail="No valid documents selected for analysis.")
    
    # Handle no question
    if not payload.question.strip() or not payload.question:
        logger.warning("Pipeline triggered without a question.")
        raise HTTPException(status_code=400, detail="No question provided for analysis.")


    logger.info(f"Pipeline started for question: {payload.question}")
    logger.info(f"Total uploaded files in session '{session_id}': {len(os.listdir(session_path))}")


    try:
        # Preprocess
        doc_ids = []
        # Filter and preprocess only new documents
        docs_to_preprocess = []
        for path in file_paths:
            filename = os.path.basename(path)

            # Generate session-prefixed doc_ids
            doc_id = f"{session_id}:{filename}"
            doc_ids.append(doc_id)

            if not is_document_indexed(session_id, doc_id):
                docs_to_preprocess.append(path)
        
        logger.info(f"{len(docs_to_preprocess)} document(s) need preprocessing.")

        if docs_to_preprocess:
            logger.info(f"Preprocessing files: {docs_to_preprocess}")
            preprocess_batch(session_id, docs_to_preprocess)

        # Extract answers
        logger.info("Extracting answers from documents...")
        answers = extract_answers_from_docs(session_id, payload.question, doc_ids)
        logger.info(f"Extraction complete. {len(answers)} answers returned.")

        # Generate themes
        logger.info("Generating thematic summary...")
        themes = extract_themes(answers)
        logger.info("Theme extraction complete.")

        return PipelineResponse(answers = answers, themes=themes)
    except Exception as e:
        logger.error(f"Pipeline failed with exception: {e}", exc_info=True)
        return PipelineResponse(answers=[], themes=f"Pipeline failed: {str(e)}")
