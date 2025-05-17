import os
import fitz
from PIL import Image
import pytesseract
from docx import Document
import shutil
from typing import List, Dict


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
    Skips embedded images — use OCR for those instead.

    Parameters:
    - file_path: Path to the PDF file

    Returns:
    - Cleaned string containing all extracted text from all pages.
    """

    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text("text") + "\n"
    return text.strip()

def extract_text_from_image(file_path: str) -> str:
    """
    Uses Tesseract OCR to extract text from image files (.png, .jpg, .jpeg).

    Parameters:
    - file_path: Path to the image file

    Returns:
    - Raw text extracted from the image using OCR
    """
    image = Image.open(file_path)
    return pytesseract.image_to_string(image)

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

def preprocess_document(file_path: str, doc_id: str) -> Dict[str, str]:
    """
    Preprocesses a single document (PDF, image, docx or text) and returns a dictionary
    with its ID and structured text (paragraph-separated).

    Parameters:
    - file_path: Full path to the input document
    - doc_id: Assigned document ID (e.g., 'DOC001')

    Returns:
    - dict: { "doc_id": ..., "text": ... }
    """
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
        raise ValueError(f"Unsupported file type: {ext}")

    paragraphs = [p.strip() for p in raw_text.split("\n") if p.strip()]
    structured_text = "\n\n".join(paragraphs)

    return {
        "doc_id": doc_id,
        "text": structured_text
    }

def preprocess_batch(file_paths: List[str]) -> List[Dict[str, str]]:
    """
    Preprocesses a list of document file paths and returns them
    as a list of dictionaries containing doc_id and extracted text.

    Parameters:
    - file_paths: List of full file paths (PDFs or images)

    Returns:
    - List[Dict]: Each dict contains 'doc_id' and 'text'
    """
    processed = []
    for i, path in enumerate(file_paths, start=1):
        doc_id = f"DOC{str(i).zfill(3)}"
        try:
            result = preprocess_document(path, doc_id)
            processed.append(result)
        except Exception as e:
            print(f"Failed to process {path}: {e}")
    return processed