# `models.py`

This module defines all **Pydantic models** used for request and response validation in the DocMind API. It ensures that all endpoints exchange data in a well-structured and type-safe format.

---

## Responsibilities

- Define response models for:
  - Uploading documents
  - Listing available files
  - Deleting a file
  - Running the document analysis pipeline

- Define the input structure for the pipeline API


## Related Modules
- `document_routes.py`: uses document-related responses

- `pipeline_routes.py`: uses `PipelineInput` and `PipelineResponse`

---