FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies needed for Python packages
RUN apt-get update && apt-get install -y \
    --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies separately for better caching
COPY requirements-railway.txt requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel && \
    python -m pip install -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run the application
CMD ["sh", "-c", "uvicorn app.main:socket_app --host 0.0.0.0 --port ${PORT:-8000}"]
