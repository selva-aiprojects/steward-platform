# StockSteward AI - Complete Setup Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Backend Configuration](#backend-configuration)
4. [Frontend Configuration](#frontend-configuration)
5. [Database Setup](#database-setup)
6. [API Integration](#api-integration)
7. [Running the Application](#running-the-application)
8. [Verification](#verification)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **Operating System**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 20.04+ recommended)
- **RAM**: Minimum 4GB (8GB+ recommended)
- **Storage**: 2GB free space
- **Python**: 3.11.x
- **Node.js**: 18.x or higher
- **Docker**: Version 20.x or higher (recommended)
- **Git**: Latest version

### Required Accounts & APIs
- Zerodha Kite Connect API credentials (for live trading)
- Groq API key (for AI features)
- PostgreSQL database (local or cloud)

## Environment Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/stocksteward-ai.git
cd stocksteward-ai
```

### 2. Install System Dependencies

#### For Ubuntu/Debian:
```bash
# Update package list
sudo apt-get update

# Install build essentials and dependencies
sudo apt-get install -y \
    build-essential \
    gcc \
    g++ \
    wget \
    curl \
    git \
    python3-dev \
    python3-venv \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    postgresql-client

# Install Node.js (if not using Docker)
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### For CentOS/RHEL/Fedora:
```bash
# Install build tools
sudo yum groupinstall -y "Development Tools"
sudo yum install -y \
    gcc \
    gcc-c++ \
    wget \
    curl \
    git \
    python3-devel \
    postgresql-devel \
    libffi-devel \
    openssl-devel

# Install Node.js (if not using Docker)
curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo bash -
sudo yum install -y nodejs
```

#### For macOS:
```bash
# Install Xcode command line tools
xcode-select --install

# Install dependencies via Homebrew
brew install \
    python@3.11 \
    node \
    postgresql \
    ta-lib \
    redis

# Install Docker Desktop for Mac
# Download from: https://www.docker.com/products/docker-desktop
```

#### For Windows:
1. Install Python 3.11 from [python.org](https://www.python.org/downloads/)
2. Install Node.js LTS from [nodejs.org](https://nodejs.org/)
3. Install Docker Desktop for Windows
4. Install Git for Windows
5. Install Microsoft C++ Build Tools (for TA-Lib compilation)

## Backend Configuration

### 1. Install TA-Lib C Library (CRITICAL - This fixes the build error!)
```bash
# For Linux/macOS, run these commands:
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
cd ..

# For Windows, download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
# Then install: pip install TA_Lib‑0.4.XX‑cpXX‑cpXX‑win_amd64.whl
```

### 2. Backend Setup
```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Backend Environment Variables
Create a `.env` file in the `backend` directory:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/stocksteward_ai
TEST_DATABASE_URL=postgresql://username:password@localhost:5432/stocksteward_ai_test

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Broker API Configuration
KITE_API_KEY=your_kite_api_key
KITE_API_SECRET=your_kite_api_secret
KITE_ACCESS_TOKEN=your_kite_access_token

# AI/ML Configuration
GROQ_API_KEY=your_groq_api_key
LLM_MODEL_NAME=llama3-groq-70b-8192-tool-use-preview

# Risk Management
MAX_POSITION_SIZE_PERCENT=0.10
MAX_DAILY_LOSS_PERCENT=0.02
MAX_TOTAL_EXPOSURE=0.80
COMMISSION_RATE=0.001
SLIPPAGE_RATE=0.0005

# Application Settings
EXECUTION_MODE=SIMULATION  # SIMULATION or LIVE_TRADING
DEBUG=true
LOG_LEVEL=INFO
```

## Frontend Configuration

### 1. Frontend Setup
```bash
cd frontend

# Install Node.js dependencies
npm install

# Create environment file
touch .env
```

### 2. Frontend Environment Variables
Add to `frontend/.env`:

```env
# API Configuration
REACT_APP_API_URL=http://localhost:8100

# Security
REACT_APP_JWT_SECRET=your-jwt-secret

# Feature Flags
REACT_APP_ENABLE_LIVE_TRADING=false
REACT_APP_ENABLE_AI_ANALYSIS=true
REACT_APP_ENABLE_BACKTESTING=true

# UI Configuration
REACT_APP_THEME=dark
REACT_APP_DEFAULT_EXCHANGE=NSE
```

## Database Setup

### 1. PostgreSQL Installation (if not using Docker)

#### Option A: Local PostgreSQL
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql

# Windows
# Download from: https://www.postgresql.org/download/windows/
```

#### Option B: Docker PostgreSQL
```bash
# Start PostgreSQL in Docker
docker run --name stocksteward-postgres \
  -e POSTGRES_DB=stocksteward_ai \
  -e POSTGRES_USER=username \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  -d postgres:15
```

### 2. Database Initialization
```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run database migrations
alembic upgrade head

# Seed initial data (optional)
python -c "
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

db = SessionLocal()
user = User(
    email='admin@stocksteward.ai',
    full_name='Admin User',
    hashed_password=get_password_hash('admin123'),
    is_active=True,
    is_superuser=True
)
db.add(user)
db.commit()
db.close()
"
```

## API Integration Setup

### 1. Zerodha Kite Connect API

#### Get API Credentials
1. Visit [Kite Connect Developer Portal](https://developers.kite.trade/)
2. Register your application
3. Get your API key and secret
4. Note: For live trading, you'll need a Zerodha trading account

#### Configure API Keys
In your backend `.env` file:
```env
KITE_API_KEY=your_actual_api_key
KITE_API_SECRET=your_actual_api_secret
```

### 2. Groq API for AI Features

#### Get API Key
1. Visit [Groq Cloud](https://console.groq.com/)
2. Sign up for an account
3. Generate an API key
4. Add to your environment variables

## Running the Application

### Option 1: Development Mode (Separate Services)

#### Backend
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python -u -m uvicorn app.main:socket_app --host 0.0.0.0 --port 8100 --log-level info
```

#### Frontend
```bash
cd frontend
npm start
```

### Option 2: Docker Compose (Recommended)
```bash
# From the project root
docker-compose up --build

# Or in detached mode
docker-compose up -d --build
```

### Option 3: Production Mode
```bash
# Backend with Gunicorn
cd backend
gunicorn app.main:app --workers 4 --bind 0.0.0.0:8000 --timeout 120

# Frontend build
cd frontend
npm run build
```

## Verification Steps

### 1. Check Backend Health
```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy"}
```

### 2. Check Frontend
Visit `http://localhost:3000` in your browser
- You should see the StockSteward AI dashboard
- Login with test credentials

### 3. Test API Endpoints
```bash
# Test authentication
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpassword"

# Test market data
curl http://localhost:8000/api/v1/market/tickers

# Test strategy listing
curl http://localhost:8000/api/v1/strategies/list
```

### 4. Verify TA-Lib Installation
```bash
cd backend
source venv/bin/activate
python -c "import talib; print('TA-Lib version:', talib.__version__)"
# Should print the TA-Lib version without errors
```

## Troubleshooting

### 1. TA-Lib Installation Issues

#### Problem: `fatal error: ta-lib/ta_defs.h: No such file or directory`
**Solution**: Install the TA-Lib C library first:
```bash
# Ubuntu/Debian
sudo apt-get install build-essential wget
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install

# Then reinstall Python package
pip uninstall TA-Lib
pip install TA-Lib
```

#### Problem: `Microsoft Visual C++ 14.0 is required` (Windows)
**Solution**: Install Microsoft C++ Build Tools:
1. Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Install with C++ build tools selected
3. Restart your terminal
4. Reinstall TA-Lib: `pip install TA-Lib`

### 2. Database Connection Issues

#### Problem: `FATAL: password authentication failed`
**Solution**: 
1. Verify your database credentials in `.env`
2. Check if PostgreSQL is running
3. Ensure the database exists: `CREATE DATABASE stocksteward_ai;`

#### Problem: `could not connect to server`
**Solution**:
1. Check if PostgreSQL is running: `sudo systemctl status postgresql`
2. Verify the connection string format
3. Check firewall settings

### 3. Docker Build Issues

#### Problem: Docker build fails with TA-Lib error
**Solution**: Use the corrected Dockerfile that installs TA-Lib C library first:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    wget \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install TA-Lib C library
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
    && tar -xzf ta-lib-0.4.0-src.tar.gz \
    && cd ta-lib \
    && ./configure --prefix=/usr \
    && make \
    && make install \
    && cd .. \
    && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4. API Integration Issues

#### Problem: Kite API authentication fails
**Solution**:
1. Verify API key and secret are correct
2. Check if API key is enabled for trading
3. Ensure your Zerodha account is activated
4. Verify internet connectivity

#### Problem: Groq API key invalid
**Solution**:
1. Verify the API key is correct
2. Check if the account has sufficient credits
3. Ensure the API key hasn't expired

### 5. Performance Issues

#### Problem: Application is slow
**Solutions**:
1. Check system resources (CPU, RAM, disk)
2. Verify database connection performance
3. Check network connectivity
4. Enable caching in production

## Production Deployment

### 1. Environment Variables for Production
```env
# Security
SECRET_KEY=super-long-random-string-only-in-production
DEBUG=false
LOG_LEVEL=WARNING

# Database (use connection pooling)
DATABASE_URL=postgresql://user:password@host:5432/dbname?pool_pre_ping=true&pool_recycle=300

# Redis
REDIS_URL=redis://host:6379

# API Keys (use secrets management)
KITE_API_KEY=production_api_key
GROQ_API_KEY=production_groq_key

# Performance
WORKERS=4
TIMEOUT=120
MAX_REQUESTS=1000
MAX_REQUESTS_JITTER=100
```

### 2. Docker Compose for Production
```yaml
version: '3.8'

services:
  backend:
    build: .
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=false
    ports:
      - "8000:8000"
    restart: unless-stopped
    depends_on:
      - db
      - redis

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: stocksteward_ai
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

volumes:
  postgres_data:
```

## Security Best Practices

### 1. API Security
- Use HTTPS in production
- Implement rate limiting
- Validate all inputs
- Use JWT tokens with short expiration
- Implement proper authentication

### 2. Data Security
- Encrypt sensitive data at rest
- Use parameterized queries to prevent SQL injection
- Implement proper access controls
- Regular security audits

### 3. Infrastructure Security
- Use non-root users in containers
- Implement network segmentation
- Regular updates and patches
- Monitor for suspicious activities

## Monitoring & Maintenance

### 1. Application Logs
```bash
# Docker logs
docker-compose logs -f

# Backend logs
tail -f backend/logs/app.log

# Frontend logs
tail -f frontend/logs/build.log
```

### 2. Performance Monitoring
- CPU and memory usage
- Database query performance
- API response times
- Error rates

### 3. Regular Maintenance
- Database backups
- Security updates
- Performance optimization
- Code reviews

---

This comprehensive setup guide provides all the necessary steps to successfully install, configure, and run the StockSteward AI platform, with special attention to resolving the TA-Lib installation issues that were causing Docker build failures.
