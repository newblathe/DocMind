import os
import uuid
from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException


from backend.app.core.config import UPLOAD_DIR
from backend.app.models.models import DocumentUploadResponse, DocumentListResponse, DeleteResponse
from backend.app.services.vector_store import remove_doc_from_index
from backend.app.core.logger import logger

router = APIRouter()



@router.post("/upload", summary="Upload onr or more documents", response_model=DocumentUploadResponse)
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Upload one or more documents to the server.

    Supported formats include PDF, JPG, PNG, TXT AND DOCX. The files are saved into a local uploads directory inside the backend.   

    Parameters:
        files (List[UploadFile]): List of Documents sent via multipart/form-data
    
    Returns:
        dict: A dictionary containing list of successfully uploaded filenames.
    
    Raises:
        HTTPException: If an unsupported file extension is provided.
    """

    # Validate that at least one file was provided
    if not files:
        logger.warning("Upload failed: No files provided in request.")
        raise HTTPException(status_code=400, detail="No files provided for upload.")

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
        file_path = UPLOAD_DIR / filename_final

        # If the file already exists, incrementally add a numeric suffix (e.g., "filename 2.pdf", "filename 3.pdf")
        while file_path.exists():
            counter += 1
            filename_final = f"{base_name} {counter}{ext}"
            file_path = UPLOAD_DIR / filename_final
                
        # Save uploaded file to disk
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
            saved_files.append(filename_final)
    
    logger.info(f"Upload complete. Files saved: {saved_files}")
    return DocumentUploadResponse(uploaded_files=saved_files)

@router.get("/list", summary = "List all uploaded documents", response_model=DocumentListResponse)
async def list_documents():
    """
    List all the dcouments currently uploaded to the server.

    Scans the upload directory and returns a list of all file names stored there

    Returns:
        dict: A dictionary containing the list of document filenames.
    """

    # Read all filenames from the upload directory
    files = [f.name for f in UPLOAD_DIR.iterdir() if f.is_file()]
    logger.info(f"Listed {len(files)} file(s) from upload directory.")
    return DocumentListResponse(documents=files)

@router.delete("/delete/{filename}", summary = "Delete a specific document", response_model=DeleteResponse)
async def delete_document(filename: str):
    """
    Delete a document from the upload directory by filename.

    Args:
        filename (str): The exact name of the file to delete.
    
    Returns:
        dict: A dictionary confirming which file was deleted.
    
    Raises:
        HTTPException: If the file does not exist.
    """
    file_path = UPLOAD_DIR / filename

    # Ensure file exists before deletion
    if not file_path.exists():
        logger.warning(f"Delete failed: File not found: {filename}")
        raise HTTPException(status_code = 404, detail = "File not found")
    
    # Delete the file
    file_path.unlink()

    # Delete the FAISS Index
    doc_id = filename
    remove_doc_from_index(doc_id)
    
    logger.info(f"Deleted file and removed from index: {filename}")
    return DeleteResponse(deleted=filename)
