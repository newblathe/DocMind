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

# Set working directory to /backend
WORKDIR /myapp

# Copy the backend code into the container
COPY backend/ backend/

# Copy the frontend demo folder
COPY demo/ demo/

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Expose FastAPI's port
EXPOSE 8000

# Run the FastAPI app
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "${PORT}"]
