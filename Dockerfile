# Use Python 3.13 slim image (smaller than full Python image)
FROM python:3.13-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies (if needed for cryptography/bcrypt)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (Docker layer caching optimization)
# If requirements don't change, this layer is reused on rebuilds
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY api/ ./api/
COPY src/ ./src/

# Create directory for persistent database storage
RUN mkdir -p /data

# Expose port 8000 (FastAPI default)
EXPOSE 8000

# Set environment variable for production
ENV PYTHONUNBUFFERED=1

# Run uvicorn server
# 0.0.0.0 allows external connections (not just localhost)
# --host 0.0.0.0 --port 8000 binds to all network interfaces
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
