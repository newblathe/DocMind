import os
import fitz
from PIL import Image
import pytesseract
from docx import Document
import shutil
from typing import List, Dict

from backend.app.services.vector_store import add_chunks_to_index, remove_doc_from_index
from backend.app.core.logger import logger

# Auto-detect the Tesseract binary from the system PATH
# If found, set it for pytesseract usage
_tess_path = shutil.which("tesseract")
if _tess_path:
    pytesseract.pytesseract.tesseract_cmd = _tess_path
else:
    print("Tesseract not found. Please install it and add to system PATH.")

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text content from a PDF file using PyMuPDF.

    Parameters:
    - file_path: Path to the PDF file

    Returns:
    - Cleaned string containing all extracted text from all pages.
    """

    blocks = []
    with fitz.open(file_path) as doc:
        for page in doc:
            for b in page.get_text("blocks"):
                text = b[4].strip().replace("\n", "")
                if text:
                    blocks.append(text)
    return "\n".join(blocks)


def extract_text_from_image(file_path: str) -> str:
    """
    Uses Tesseract OCR to extract text from image files (.png, .jpg, .jpeg).

    Parameters:
    - file_path: Path to the image file

    Returns:
    - Raw text extracted from the image using OCR
    """
    image = Image.open(file_path)
    extracted_text = pytesseract.image_to_string(image, lang="eng", config= "--psm 6") 
    return extracted_text.replace("\n", " ").replace("  ", "\n")

def extract_text_from_docx(file_path: str) -> str:
    """
    Extracts text content from a Microsoft Word (.docx) document.

    Parameters:
    - file_path: Path to the .docx file

    Returns:
    - Combined text from all non-empty paragraphs in the document
    """
    doc = Document(file_path)
    return "\n".join(para.text for para in doc.paragraphs if para.text.strip())

def extract_text_from_txt(file_path: str) -> str:
    """
    Reads and returns text from a plain text (.txt) file.

    Parameters:
    - file_path: Path to the .txt file

    Returns:
    - Full content of the text file as a string
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def preprocess_document(file_path: str, doc_id: str):
    """
    This function reads the contents of a supported document type (PDF, image, DOCX, or TXT),
    extracts the raw text, splits it into cleaned chunks, and stores them in a vector index 
    after removing any existing entries for the same document ID.

    Parameters:
    - file_path: Full path to the input document
    - doc_id: Assigned document ID (e.g., 'DOC001')

    """

    logger.info(f"Starting preprocessing: {file_path}")

    ext = os.path.splitext(file_path)[-1].lower()

    if ext in [".pdf"]:
        raw_text = extract_text_from_pdf(file_path)
    elif ext in [".png", ".jpg", ".jpeg"]:
        raw_text = extract_text_from_image(file_path)
    elif ext == ".docx":
        raw_text = extract_text_from_docx(file_path)
    elif ext == ".txt":
        raw_text = extract_text_from_txt(file_path)
    else:
        logger.error(f"Unsupported file type during preprocessing: {ext}")
        raise ValueError(f"Unsupported file type: {ext}")

    chunks = [p.strip() for p in raw_text.split("\n") if p.strip()]
    logger.info(f"Extracted {len(chunks)} chunk(s) from {doc_id}")

    remove_doc_from_index(doc_id)
    add_chunks_to_index(doc_id, chunks)



def preprocess_batch(file_paths: List[str]):
    """
    Preprocesses a list of document file paths and returns them
    as a list containing doc_ids

    Parameters:
    - file_paths: List of full file paths (PDFs or images)

    Returns:
    - List[str]: List of Document IDs
    """
    logger.info(f"Starting batch preprocessing of {len(file_paths)} file(s).")
    processed = []

    for path in (file_paths):
        doc_id = os.path.basename(path)
        try:
            preprocess_document(path, doc_id)
            processed.append(doc_id)
        except Exception as e:
            logger.error(f"Failed to process {path}: {e}", exc_info=True)
        
    logger.info(f"Batch preprocessing complete. Successfully processed: {processed}")
    return processed
