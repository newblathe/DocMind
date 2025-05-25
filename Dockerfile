# Use a Python base image
FROM python:3.10

# Install system dependencies for Tesseract and image processing
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /myapp

# Copy backend and frontend
COPY backend/ backend/
COPY demo/ demo/

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Start FastAPI
CMD uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
