from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.routes.document_routes import router as document_router
from backend.app.api.routes.pipeline_routes import router as pipeline_router
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI(title="Document Theme Identifier")

# Enable CORS for all origins (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend UI from /ui endpoint
app.mount("/ui", StaticFiles(directory=Path("demo"), html=True), name="static")

# Register API routers
app.include_router(document_router)
app.include_router(pipeline_router)