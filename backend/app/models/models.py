from pydantic import BaseModel
from typing import List

# Response when uploading files
class DocumentUploadResponse(BaseModel):
    uploaded_files: List[str]

# Response for listing uploaded files
class DocumentListResponse(BaseModel):
    documents: List[str]

# Response after deleting a file
class DeleteResponse(BaseModel):
    deleted: str

# Structure for an answer from a document
class AnswerItem(BaseModel):
    doc_id: str
    answer: str
    citation: str

# Request model for the pipeline
class PipelineInput(BaseModel):
    question: str

# Full response model for the pipeline
class PipelineResponse(BaseModel):
    answers: List[AnswerItem]
    themes: str