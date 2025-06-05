import os
import uuid
from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Body, Query

from backend.app.core.limiter import limiter


from backend.app.core.config import UPLOAD_DIR
from backend.app.models.models import DocumentUploadResponse, DocumentListResponse, DeleteResponse
from backend.app.services.vector_store import remove_doc_from_index
from backend.app.core.logger import logger

router = APIRouter()



@router.post("/upload", summary="Upload one or more documents", response_model=DocumentUploadResponse)
@limiter.shared_limit("100/minute", scope="global")  # Rate Limiting
async def upload_documents(request: Request, session_id: str = Query(...), files: List[UploadFile] = File(...)):
    """
    Upload one or more documents to the server.

    Supported formats include PDF, JPG, PNG, TXT AND DOCX. The files are saved into a local uploads directory inside the backend.   

    Parameters:
        request (Request): Request object used to access client IP for concurrency checks.
        session_id (str): Required session ID passed in the query to isolate user data and results.
        files (List[UploadFile]): List of Documents sent via multipart/form-data
    
    Returns:
       DocumentUploadResponse : Contains a list of successfully uploaded filenames.
    
    Raises:
        HTTPException: If an unsupported file extension is provided or no files are provided.
    """

    # Validate that at least one file was provided
    if not files:
        logger.warning("Upload failed: No files provided in request.")
        raise HTTPException(status_code=400, detail="No files provided for upload.")
    
    # Ensure a dedicated upload directory exists for this session
    session_path = UPLOAD_DIR / session_id
    session_path.mkdir(parents = True, exist_ok = True)

    logger.info(f"Received {len(files)} file(s) for upload.")

    saved_files = []
    for file in files:
        # Extract and normalize file extension
        file_ext = os.path.splitext(file.filename)[-1].lower()

        # Reject unsupported formats
        if file_ext not in [".pdf", ".png", ".jpg", ".jpeg", ".txt", ".docx"]:
            logger.warning(f"Rejected unsupported file type: {file.filename} ({file_ext})")
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_ext}")
        
        file_path = UPLOAD_DIR / file.filename

        # Resolve duplicate filenames
        base_name, ext = os.path.splitext(file.filename)
        counter = 1
        filename_final = file.filename
        file_path = session_path / filename_final

        # If the file already exists, incrementally add a numeric suffix (e.g., "filename 2.pdf", "filename 3.pdf")
        while file_path.exists():
            counter += 1
            filename_final = f"{base_name} {counter}{ext}"
            file_path = session_path / filename_final
                
        # Save uploaded file to disk
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
            saved_files.append(filename_final)
    
    logger.info(f"Upload complete. Files saved: {saved_files}")
    return DocumentUploadResponse(uploaded_files=saved_files)

@router.get("/list", summary = "List all uploaded documents", response_model=DocumentListResponse)
@limiter.shared_limit("100/minute", scope="global") # Rate Limiting
async def list_documents(request: Request, session_id: str = Query(...)):
    """
    List all the dcouments currently uploaded to the server for current session.

    Parameters:
        request (Request): Request object used to access client IP for concurrency checks.
        session_id (str): Required session ID passed in the query to isolate user data and results.

    Returns:
        DocumentListResponse: Contains a list of document filenames.
    """
    
    # Only list documents under the current session's upload folder
    session_path = UPLOAD_DIR / session_id
    if not session_path.exists():
        return DocumentListResponse(documents=[])
    
    # Read all filenames from the upload directory
    files = [f.name for f in session_path.iterdir() if f.is_file()]
    logger.info(f"Listed {len(files)} file(s) from upload directory.")
    return DocumentListResponse(documents=files)

@router.post("/delete", summary = "Delete a specific document", response_model=DeleteResponse)
@limiter.shared_limit("100/minute", scope="global") # Rate Limiting
async def delete_document(request: Request, session_id: str = Query(...), body: dict = Body(...)):
    """
    Delete a document from the upload directory by filename and from the vector database by doc_id.

    Parameters:
        request (Request): Request object used to access client IP for concurrency checks.
        session_id (str): Required session ID passed in the query to isolate user data and results.
        filename (str): The exact name of the file to delete.
    
    Returns:
        DeleteResponse: Contains name of the file deleted.
    
    Raises:
        HTTPException: If the file does not exist.
    """
    filename = body.get("filename")

    # Only allow deletion from this session's folder
    file_path = UPLOAD_DIR / session_id/ filename

    # Ensure file exists before deletion
    if not file_path.exists():
        logger.warning(f"Delete failed: File not found: {filename}")
        raise HTTPException(status_code = 404, detail = "File not found")
    
    # Delete the file
    file_path.unlink()

    # Delete the FAISS Index
    doc_id = f"{session_id}:{filename}"
    remove_doc_from_index(session_id, doc_id)
    
    logger.info(f"Deleted file and removed from index: {filename}")
    return DeleteResponse(deleted=filename)
