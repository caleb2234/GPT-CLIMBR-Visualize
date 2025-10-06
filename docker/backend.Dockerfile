FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for PyTorch and ML libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY backend/requirements.txt .

# Install Python dependencies (torch is large, this layer will be cached)
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application code and data files
COPY backend/ .

# Expose Flask port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:5000/api/pathways', timeout=5)"

# Run with gunicorn for production (1 worker due to ML model memory requirements)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--timeout", "120", "app:app"]
