  FROM python:3.11-slim

  WORKDIR /app

  # Copy requirements first for layer caching
  COPY backend/requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt

  # Copy application code
  COPY backend/ .

  # Expose Flask port
  EXPOSE 5000

  # Run with gunicorn for production
  RUN pip install gunicorn
  CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]