FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed for Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    libpq-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies separately for better caching
COPY requirements-production.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir TA-Lib==0.6.8 && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "startup.py"]
