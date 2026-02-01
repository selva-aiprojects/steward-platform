FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
# gcc and libpq-dev are often needed for python packages
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run the application
# Using generic uvicorn command, but entrypoint can be overridden
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
