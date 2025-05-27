# DocMind

**DocMind** is an intelligent document analysis platform that allows users to upload files, ask questions, and receive precise per document answers and citations along with theme-based insights. It supports PDFs, images, Word documents, and text files, and is powered by OCR, vector search, and Groq LLM.

> Upload → Ask → Analyze → Understand

---
## Table of Contents

- [Architecture](#architecture)
- [Core Modules](#core-modules)
- [Features](#features)
- [Live Demo](#live-demo)
- [Local Setup](#local-setup)
  - [Option 1: Run with Docker](#option-1-run-with-docker-recommended)
  - [Option 2: Run with Uvicorn](#option-2-run-with-uvicorn-local-python)
- [Folder Structure](#folder-structure)
- [Tech Stack](#tech-stack)

## Architecture

                     ┌────────────────────────┐
                     │      Frontend UI       │
                     │     (Upload files)     │◄─────────────────────────┐
                     └────────────┬───────────┘                          │
                                  │                                      │
                                  ▼                                      │
                          ┌───────────────┐                              │
                          │  /upload API  │                              │
                          └──────┬────────┘                              │ 
                                 ▼                                       │
                     ┌─────────────────────┐                             │
                     │Store file in uploads│                             │
                     │ folder on backend   │                             │
                     └─────────┬───────────┘                             │
                               │                                         │
                               ▼                                         │
                     ┌────────────────────────┐                          │
                     │      Frontend UI       │◄─────────────────────────│
                     │     (Asks question)    │                          │
                     └──────────┬─────────────┘                          │
                                │                                        │
                                ▼                                        │
                      ┌────────────────────┐                             │
                      │  /run-pipeline API │                             │
                      └────────┬───────────┘                             │
                               │                                         │ 
                               ▼                                         │
             ┌────────────────────────────────────────────┐              │ 
             │ For each uploaded document:                │              │
             │ Check if already indexed in FAISS          │              │
             └─────────────┬──────────────┬───────────────┘              │
                           │              │                              │
                       Yes ▼           No ▼                              │
       ┌────────────────────────┐  ┌────────────────────────────┐        │
       │ Skip preprocessing and │  │ Preprocess document:       │        │
       │ embedding (already in  │  │  - OCR/text extraction     │        │
       │ vector store)          │  │  - Chunking + Embedding    │        │
       └────────────┬───────────┘  │  - Store in FAISS index    │        │
                    │              └─────────────┬──────────────┘        │
                    │                            │                       │
                    │                            │                       │
                    ▼                            ▼                       │
                ┌────────────────────────────────────┐                   │
                │ Embed the user's question          │                   │
                │ using sentence-transformers        │                   │
                └─────────────┬──────────────────────┘                   │
                              ▼                                          │
                ┌────────────────────────────────────────────────┐       │
                │ Semantic search using FAISS                    │       │
                │ (find top-k chunks per doc based on Question)  │       │
                └─────────────┬──────────────────────────────────┘       │
                              ▼                                          │
                ┌─────────────────────────────────────┐                  │
                │  Groq LLM: Answer Generator         │                  │
                │  (answers using retrieved chunks)   │                  │
                └─────────────┬───────────────────────┘                  │
                              ▼                                          │
                ┌─────────────────────────────────────┐                  │
                │  Groq LLM: Theme Identifier         │                  │
                │  (extracts themes from all answers) │                  │
                └──────────────┬──────────────────────┘                  │
                               ▼                                         │
              ┌────────────────────────────────────────────────────┐     │
              │ Response to frontend: answers + citations + themes │─────│
              └─────────────────────┬──────────────────────────────┘     │
                                    │                                    │ 
                                    ▼                                    │
                      ┌────────────────────────┐                         │
                      │      Frontend UI       │                         │
                      │     (Delete files)     │                         │  
                      └────────────┬───────────┘                         │
                                   ▼                                     │
                           ┌──────────────┐                              │
                           │ /delete API  │                              │
                           └──────┬───────┘                              │
                                  ▼                                      │
                        ┌───────────────────┐                            │
                        │ Remove file and   │                            │
                        │ its FAISS chunks  │────────────────────────────┘
                        └───────────────────┘
   
---

## Core Modules
| File                     | Responsibility                                                                 | Link |
|--------------------------|---------------------------------------------------------------------------------|------|
| `document_routes.py` | **Backend route** for uploading, listing, and deleting documents from storage| [View Docs](docs/document_routes.MD) |
| `pipeline_routes.py` | **Backend route** that triggers the full QA + theme extraction pipeline| [View Docs](docs/pipeline_routes.MD) |
| `document_preprocessor.py` | Extracts text from PDFs, images, DOCX, and TXT|[View Docs](docs/document_preprocessor.MD) |
| `vector_store.py` | Manages FAISS-based semantic indexing, chunk-level retrieval|[View Docs](docs/vector_store.MD) |
| `query_engine.py` | Uses Groq LLM to extract detailed answers and citations per document|[View Docs](docs/query_engine.MD) |
| `theme_identifier.py` | Clusters answers into themes using Groq LLM|[View Docs](docs/theme_identifier.MD) |
| `models.py` | Defines Pydantic models for API requests and responses|[View Docs](docs/models.MD) |
| `main.py` | Initializes the FastAPI app, registers routes, sets up static file serving| [View Docs](docs/main.MD) |
| `config.py` | Centralizes environment and file path configs; loads variables via `.env` |[View Docs](docs/config.MD) |
| `logger.py` | Sets up structured application-wide logging  |[View Docs](docs/logger.MD) |
| `limiter.py`| Defines and applies a global shared rate limiter for all API routes using SlowAPI. |[View Docs](docs/logger.MD)|

---

## Features
- **Document Uploading**

    - Upload multiple file types: .pdf, .docx, .txt, .jpg, .png

    - Files stored persistently for reuse across sessions

- **Smart Text Extraction**

    - OCR-based parsing using Tesseract for images and scanned PDFs

    - Text-based parsing for PDF, Word, and TXT documents

    - Paragraph-aware formatting for clean chunking

- **Retrieval-Augmented Generation (RAG)**

    - Embeds document chunks with sentence-transformers

    - Stores and searches chunks using FAISS for semantic retrieval

    - Prevents duplicate processing via indexed document tracking


- **LLM-Powered QA and Insights**

    - Uses Groq (OpenAI-compatible) to answer a question per document and provide citations

    - Identifies themes across all documents via prompt-engineered summarization

- **Paragraph-Level Citations**

    - Each answer is linked back to the exact paragraph(s) that supported it

    - Enhances traceability and transparency of AI-generated responses

- **Modular & Extensible Backend**

    - Clear separation of API routes

    - Built with FastAPI and fully containerized with Docker

    - Config-driven paths, logging, and API schema

- **Rate Limiting & Abuse Protection**
    - Shared global request limit across all routes (e.g., 100 requests/minute per IP)

    - Automatic redirect to `/rate_limit.html` if rate limit is exceeded

- **Session-Based Isolation**

    - Each user session is uniquely tracked using localStorage and a generated session ID

    - Uploaded files are stored in per-session directories for logical separation


---

## Live Demo

Access the app at:  
[https://docmind-production-6f75.up.railway.app/](https://docmind-production-6f75.up.railway.app/)

Upload your documents, ask a question, and view:
- Per Document answers
- Paragraph-Level Citations
- Theme-based insights across documents

## Local Setup

You can run DocMind either via **Docker** (recommended) or directly using **Uvicorn** with a local Python environment.

### Option 1: Run with Docker (Recommended)

#### 1. Clone the repository

```bash
git clone https://github.com/newblathe/DocMind.git
cd docmind
```

#### 2. Create a .env file

Set `GROQ_API_KEY=your_groq_key_here` in your `.env` file.

#### 3. Build and run the Docker container

```bash
docker build -t docmind .
docker run -p 8000:8000 --env-file .env docmind
```

#### 4. Open the app

Visit http://localhost:8000/ in your browser.

### Option 2: Run with Uvicorn (Local Python)

#### 1. Create and activate Conda environment

```bash
conda create -n docmind python=3.10
conda activate docmind
```

#### 2. Install dependencies

```bash
pip install -r requirements.txt
```

#### 3. Create a .env file

Set `GROQ_API_KEY=your_groq_key_here` in your `.env` file.

#### 4. Run the FastAPI app

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 5. Open the app
Visit http://localhost:8000/


## Folder Structure
<pre><code>root_dir/
├── backend/
│ ├── app/
│ │ ├── main.py # Initializes FastAPI app and routes
│ │ ├── api/
│ │ │ └── routes/
│ │ │   ├── document_routes.py # Document-related API endpoints
│ │ │   └── pipeline_routes.py # Pipeline trigger API
│ │ ├── core/
│ │ │ ├── config.py # Configuration and constants
│ │ │ └── logger.py # Application-wide logging
│ │ ├── models/
│ │ │ └── models.py # Pydantic request/response models
│ │ ├── services/
│ │ │ ├── document_preprocessor.py # OCR and document parsing
│ │ │ ├── query_engine.py # Groq-based per document answer generation
│ │ │ ├── theme_identifier.py # Extracts themes from answers
│ │ │ └── vector_store.py # FAISS vector store operations
│ ├── data/
│   ├── uploads/ # Uploaded user files
│   └── vector_store/ # FAISS index and metadata
│
├── demo/
│ ├── index.html # Frontend UI (HTML)
│ ├── style.css # Custom styles
│ └── script.js # JS for API interaction
│
├── docs/ # Module-level documentation
├── tests/ # Manual test files
├── .dockerignore # Ignore files for Docker builds
├── .env # Environment variables (not tracked)
├── .gitignore # Git ignore file
├── Dockerfile #  Dockerfile for building docker image
├── README.MD # Project documentation
└── requirements.txt # Python dependencies
</code></pre>

---

## Tech Stack



### Document Processing
- **PyMuPDF** – Text extraction from PDFs
- **Tesseract OCR** – Open-source OCR engine for scanned documents
- **pytesseract** – OCR for scanned documents and images
- **python-docx** – Reading text from DOCX files

### Semantic Search (RAG)
- **sentence-transformers** – Embeds document chunks into dense vectors
- **FAISS** – Efficient vector similarity search for top-k chunk retrieval
- **RAG Architecture** – Retrieval-Augmented Generation: retrieve relevant content, generate answers

### LLM Integration
- **Groq API (OpenAI-compatible)** – Answer generation and theme extraction based on retrieved context

### Deployment
- **Docker** – Containerization for consistent deployment

### Backend
- **FastAPI** – Web framework for building APIs
- **Pydantic** – Data validation and schema modeling
- **Uvicorn** – ASGI server for running FastAPI
- **Slowapi** – For Rate Limiting

### Frontend
- **HTML + CSS + Vanilla JS** – Lightweight frontend for uploading documents, triggering analysis, and displaying results with built-in rate-limit handling.

### Utilities
- **Logging (Python logging module)** – Structured log output across modules
- **dotenv** – Environment variable loading
- **Pathlib / os** – File path management and directory handling

## Future Improvements

- **Per-User Authentication & Encrypted Storage**

    - Implement OAuth2/JWT-based login for secure user access

    - Enable encrypted, user-isolated file storage and query history

- **Redis-Based Rate Limiting (Per-User/IP)**

    - Integrate Redis for scalable, distributed rate limiting across API endpoints

    - Enforce request quotas per session or user to prevent abuse

- **Redis-Based Session Locks & Query Control**

    - Prevent overlapping executions from the same session using Redis locks

    - Enable queued or rejected requests if a session is already processing

    - Manage parallel execution across multiple sessions while preserving per-session consistency

- **Concurrent Session Management**

    - Improve execution tracking to safely support simultaneous queries from multiple sessions


- **Parallel Query Execution**

    - Scale backend to support concurrent document analysis for multiple users using multi-worker setups
