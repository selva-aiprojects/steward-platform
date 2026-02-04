# StockSteward AI - Troubleshooting Guide

## Table of Contents
1. [Common Installation Issues](#common-installation-issues)
2. [TA-Lib Installation Problems](#ta-lib-installation-problems)
3. [Docker Build Issues](#docker-build-issues)
4. [Runtime Errors](#runtime-errors)
5. [Database Connection Issues](#database-connection-issues)
6. [API Integration Problems](#api-integration-problems)
7. [Performance Issues](#performance-issues)
8. [Security Issues](#security-issues)
9. [Monitoring & Debugging](#monitoring--debugging)

## Common Installation Issues

### 1. TA-Lib Installation Error
**Error Message**: `talib/_ta_lib.c:1082:10: fatal error: ta-lib/ta_defs.h: No such file or directory`

**Root Cause**: The TA-Lib Python package requires the TA-Lib C library to be installed on the system before it can be compiled.

**Solutions**:

#### For Linux/macOS:
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install build-essential wget
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install

# CentOS/RHEL/Fedora
sudo yum install gcc gcc-c++ wget
# or for newer versions
sudo dnf install gcc gcc-c++ wget

# Follow same steps as Ubuntu

# macOS
brew install ta-lib
```

#### For Windows:
1. Download the pre-compiled binaries from [Christoph Gohlke's site](https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib)
2. Install using pip: `pip install TA_Lib‑0.4.XX‑cpXX‑cpXX‑win_amd64.whl`

#### For Docker:
Update your Dockerfile to include TA-Lib installation:
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    wget \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Download and install TA-Lib C library
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
    && tar -xzf ta-lib-0.4.0-src.tar.gz \
    && cd ta-lib \
    && ./configure --prefix=/usr \
    && make \
    && make install \
    && cd .. \
    && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# Now install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```

### 2. Missing Dependencies
**Error Message**: Various compilation errors during pip install

**Solution**:
```bash
# Install build tools
sudo apt-get install build-essential

# Install Python development headers
sudo apt-get install python3-dev

# Install other common dependencies
sudo apt-get install libffi-dev libssl-dev
```

## Docker Build Issues

### 1. TA-Lib Compilation Failure in Docker
**Problem**: TA-Lib fails to compile in Docker container

**Solution**: Use the corrected Dockerfile approach shown above, or use a multi-stage build:

```dockerfile
# Multi-stage build for TA-Lib
FROM python:3.11-slim as builder

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    wget \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Build TA-Lib
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
    && tar -xzf ta-lib-0.4.0-src.tar.gz \
    && cd ta-lib \
    && ./configure --prefix=/usr/local \
    && make \
    && make install

# Install Python packages
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy compiled TA-Lib and Python packages
COPY --from=builder /usr/local /usr/local
COPY --from=builder /root/.local /root/.local

# Copy application
COPY . .

# Ensure PATH includes user packages
ENV PATH=/root/.local/bin:$PATH

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Permission Issues in Docker
**Problem**: Permission denied errors when running in Docker

**Solution**:
```dockerfile
# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser

# Change ownership of application directory
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser
```

## Runtime Errors

### 1. Import Errors
**Error**: `ModuleNotFoundError: No module named 'talib'`

**Solutions**:
1. Verify TA-Lib is installed: `pip list | grep TA`
2. Check Python path: `python -c "import sys; print(sys.path)"`
3. Reinstall TA-Lib: `pip uninstall TA-Lib && pip install TA-Lib`

### 2. Database Connection Errors
**Error**: `psycopg2.OperationalError: FATAL: password authentication failed`

**Solutions**:
1. Check DATABASE_URL in environment variables
2. Verify PostgreSQL service is running
3. Check credentials in docker-compose.yml
4. Ensure database migration has run

### 3. API Connection Issues
**Error**: `ConnectionError: Failed to connect to broker API`

**Solutions**:
1. Verify API keys are correct
2. Check internet connectivity
3. Verify broker API status
4. Check rate limiting

## Database Connection Issues

### 1. PostgreSQL Connection
**Problem**: Cannot connect to PostgreSQL database

**Debug Steps**:
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Test connection
docker exec -it <postgres_container> psql -U <username> -d <database>

# Check environment variables
echo $DATABASE_URL
```

### 2. Migration Issues
**Problem**: Database migrations failing

**Solutions**:
```bash
# Check current migration status
alembic current

# Run migrations
alembic upgrade head

# If stuck, check for locks
psql -d <database> -c "SELECT pid, query FROM pg_stat_activity WHERE state = 'active';"
```

## API Integration Problems

### 1. Kite/Zerodha API Issues
**Problem**: Kite API authentication failures

**Solutions**:
1. Verify API key and access token
2. Check if API key is enabled for trading
3. Verify API key permissions
4. Check if account is activated for trading

### 2. Rate Limiting
**Problem**: API calls being throttled

**Solutions**:
1. Implement proper rate limiting in code
2. Use caching for repeated requests
3. Batch requests where possible
4. Implement exponential backoff

## Performance Issues

### 1. Slow Backtesting
**Problem**: Backtesting taking too long

**Solutions**:
1. Optimize data loading
2. Use vectorized operations
3. Implement parallel processing
4. Cache historical data

### 2. High Memory Usage
**Problem**: Application consuming too much memory

**Solutions**:
1. Implement proper garbage collection
2. Use generators instead of lists where possible
3. Monitor memory usage with tools
4. Optimize data structures

## Security Issues

### 1. API Key Exposure
**Problem**: API keys in source code

**Solutions**:
1. Use environment variables
2. Implement proper .gitignore
3. Use secrets management
4. Regular security scans

### 2. SQL Injection Prevention
**Problem**: Potential SQL injection vulnerabilities

**Solutions**:
1. Use parameterized queries
2. Validate all inputs
3. Use ORM properly
4. Regular security audits

## Monitoring & Debugging

### 1. Log Analysis
```bash
# View application logs
docker logs <container_name>

# View logs with timestamps
docker logs -t <container_name>

# Follow logs in real-time
docker logs -f <container_name>
```

### 2. Health Checks
```bash
# Check application health
curl http://localhost:8000/health

# Check database connectivity
curl http://localhost:8000/api/v1/health/database

# Check external API connectivity
curl http://localhost:8000/api/v1/health/broker
```

### 3. Debugging Environment Variables
```bash
# Check all environment variables
docker exec <container_name> env

# Check specific variable
docker exec <container_name> printenv DATABASE_URL
```

## Quick Fixes

### 1. Clean Installation
```bash
# Remove all containers and volumes
docker-compose down -v

# Remove all images
docker system prune -a

# Rebuild everything
docker-compose up --build
```

### 2. Dependency Issues
```bash
# Clean pip cache
pip cache purge

# Reinstall requirements
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

### 3. Database Reset
```bash
# Reset database
docker-compose down
docker volume rm $(docker volume ls -q | grep stocksteward)
docker-compose up -d db
docker-compose run --rm backend alembic upgrade head
```

## Support Resources

### 1. Official Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [TA-Lib Python](https://github.com/mrjbq7/ta-lib)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### 2. Community Support
- [Stack Overflow](https://stackoverflow.com/questions/tagged/fastapi)
- [GitHub Issues](https://github.com/your-repo/issues)
- [Discord/Slack Channels](link-to-community)

### 3. Emergency Contacts
- Development Team: [contact-info]
- Infrastructure Team: [contact-info]
- Security Team: [contact-info]

---

## Appendix: Common Commands

### Docker Commands
```bash
# Build and run
docker-compose up --build

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Execute command in container
docker-compose exec backend bash

# Stop all services
docker-compose down
```

### Database Commands
```bash
# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "migration message"

# Check current version
alembic current
```

### Development Commands
```bash
# Run tests
pytest

# Run linter
flake8 .

# Format code
black .

# Check types
mypy .
```

This troubleshooting guide provides comprehensive solutions for common issues encountered when running the StockSteward AI platform, with special emphasis on the TA-Lib installation problem that was causing the Docker build to fail.