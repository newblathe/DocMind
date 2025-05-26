from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from pathlib import Path


from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from backend.app.core.limiter import limiter

from backend.app.api.routes.document_routes import router as document_router
from backend.app.api.routes.pipeline_routes import router as pipeline_router

app = FastAPI(title="DocMind")



# Handle rate limit exceeded
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return RedirectResponse(
        url="/static/rate_limit.html",
        status_code=303
    )

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(document_router)
app.include_router(pipeline_router)

# Serve the HTML file
@app.get("/", include_in_schema=False)
@limiter.shared_limit("100/minute", scope = "global")
async def serve_html(request: Request):
    """
    Serves the main frontend HTML page.
    """
    return FileResponse("demo/index.html")

# Serve the JS and CSS files
app.mount("/static", StaticFiles(directory=Path("demo/static")), name="static")