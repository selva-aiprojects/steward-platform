# StockSteward AI - Architecture & Workflow Documentation

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Component Architecture](#component-architecture)
4. [Data Flow Architecture](#data-flow-architecture)
5. [Workflow Diagrams](#workflow-diagrams)
6. [Deployment Architecture](#deployment-architecture)
7. [Security Architecture](#security-architecture)
8. [Monitoring & Observability](#monitoring--observability)
9. [Troubleshooting Guide](#troubleshooting-guide)
10. [References](#references)

## Executive Summary

StockSteward AI is an advanced algorithmic trading platform that combines artificial intelligence with sophisticated trading strategies to provide automated investment stewardship. The platform enables users to implement, backtest, and execute trading strategies with comprehensive risk management and real-time market analysis.

### Key Features
- **Advanced Backtesting Engine**: Realistic market simulation with slippage and commission modeling
- **Comprehensive Risk Management**: Position limits, VaR calculations, concentration risk monitoring
- **Multiple Trading Strategies**: SMA crossover, RSI mean reversion, MACD, Bollinger Bands, etc.
- **Real-time Market Data**: Live feeds from multiple exchanges (NSE, BSE, MCX)
- **AI-Powered Insights**: Machine learning-driven market analysis and predictions
- **Execution Engine**: Advanced order types and algorithmic execution

## System Architecture

### High-Level Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │◄──►│   Backend API    │◄──►│  External APIs  │
│   (React)       │    │   (FastAPI)      │    │ (Kite, etc.)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │   Message Queue   │
                    │   (RabbitMQ)      │
                    └─────────┬─────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌────────▼────────┐   ┌───────▼────────┐
│  ML Service    │   │  Risk Manager   │   │  Execution     │
│  (TensorFlow)  │   │                 │   │  Engine        │
└────────────────┘   └─────────────────┘   └────────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   Database        │
                    │   (PostgreSQL)    │
                    └───────────────────┘
```

### Technology Stack
- **Frontend**: React 18+, TypeScript, Tailwind CSS, Socket.io
- **Backend**: Python 3.11, FastAPI, SQLAlchemy, PostgreSQL
- **ML/AI**: Python, TensorFlow/PyTorch, scikit-learn, TA-Lib
- **Database**: PostgreSQL, Redis (caching), InfluxDB (time-series)
- **Infrastructure**: Docker, Kubernetes, AWS/GCP
- **Message Queue**: RabbitMQ/Redis
- **Monitoring**: Prometheus, Grafana, ELK Stack

## Component Architecture

### Backend Components

#### 1. Core Services
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   ├── core/                   # Core functionality
│   │   ├── config.py           # Configuration management
│   │   ├── database.py         # Database connection
│   │   ├── security.py         # Authentication/authorization
│   │   └── middleware.py       # Custom middleware
│   ├── api/                    # API endpoints
│   │   └── v1/
│   │       ├── api.py          # API router
│   │       └── endpoints/      # Individual endpoints
│   │           ├── trades.py
│   │           ├── portfolios.py
│   │           ├── strategies.py
│   │           ├── backtesting.py
│   │           └── ...
│   ├── models/                 # Database models
│   │   ├── user.py
│   │   ├── portfolio.py
│   │   ├── trade.py
│   │   ├── strategy.py
│   │   └── ...
│   ├── schemas/                # Pydantic schemas
│   │   ├── user.py
│   │   ├── trade.py
│   │   ├── strategy.py
│   │   ├── backtesting.py
│   │   └── ...
│   ├── services/               # Business logic
│   │   ├── trade_service.py
│   │   ├── portfolio_service.py
│   │   ├── strategy_service.py
│   │   ├── backtesting_service.py
│   │   └── ...
│   ├── utils/                  # Utility functions
│   │   ├── technical_analysis.py
│   │   ├── risk_calculations.py
│   │   └── ...
│   ├── agents/                 # AI/ML agents
│   │   ├── market_analyst.py
│   │   ├── risk_manager.py
│   │   └── ...
│   └── backtesting/            # Backtesting engine
│       └── engine.py
├── tests/                      # Unit and integration tests
├── requirements.txt            # Dependencies
└── Dockerfile                  # Container configuration
```

#### 2. Frontend Components
```
frontend/
├── public/
├── src/
│   ├── components/           # Reusable UI components
│   │   ├── ui/              # Base UI components
│   │   ├── layout/          # Layout components
│   │   ├── charts/          # Chart components
│   │   └── trading/         # Trading-specific components
│   ├── pages/               # Page components
│   │   ├── Dashboard.jsx
│   │   ├── TradingHub.jsx
│   │   ├── Portfolio.jsx
│   │   ├── Backtesting.jsx
│   │   └── ...
│   ├── services/            # API services
│   │   ├── api.js
│   │   ├── socket.js
│   │   └── ...
│   ├── context/             # React contexts
│   │   ├── UserContext.jsx
│   │   ├── AppDataContext.jsx
│   │   └── ...
│   ├── hooks/               # Custom React hooks
│   │   ├── useApi.js
│   │   ├── useSocket.js
│   │   └── ...
│   ├── utils/               # Utility functions
│   │   ├── helpers.js
│   │   ├── validators.js
│   │   └── ...
│   ├── styles/              # CSS styles
│   │   └── globals.css
│   ├── App.jsx              # Main application component
│   └── index.jsx            # Entry point
├── package.json
└── vite.config.js
```

## Data Flow Architecture

### 1. Trading Data Flow
```
User Action → Frontend → Backend API → Risk Manager → Execution Engine → Broker API → Exchange
     ↓              ↓           ↓            ↓              ↓            ↓         ↓
  Validation   Processing   Validation   Execution    Confirmation   Order    Fill
     ↑              ↑           ↑            ↑              ↑            ↑         ↑
  Response ← Result ← Risk ← Execution ← Risk ← Execution ← Broker ← Exchange ← Fill
```

### 2. Backtesting Data Flow
```
Strategy Request → Historical Data → Indicator Calculation → Signal Generation → Order Execution → Performance Calculation → Results
      ↓                ↓                   ↓                      ↓                   ↓                 ↓              ↓
   Validate       Load Data         Calculate TA        Generate Signals    Execute Orders    Calculate Metrics   Return
      ↑                ↑                   ↑                      ↑                   ↑                 ↑              ↑
   Response ← Results ← Processed ← Indicators ← Signals ← Orders ← Metrics ← Results ← Process
```

### 3. Real-time Market Data Flow
```
Exchange → Market Data Feed → Data Processing → Database Storage → API Service → Frontend → WebSocket → UI Update
    ↓            ↓                  ↓                ↓              ↓           ↓          ↓         ↓
 Raw Data   Normalize Data    Validate Data    Store Data    Serve Data   Format Data  Broadcast  Render
```

## Workflow Diagrams

### 1. Trading Workflow
```
┌─────────────────┐
│   User Action   │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Order Creation │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Risk Validation│
└─────────┬───────┘
          │
    ┌─────▼─────┐
    │  Approved │─────┐
    └───────────┘     │
          │           │
          ▼           ▼
┌─────────────────┐ ┌─────────────────┐
│  Order Routing  │ │  Reject Order   │
└─────────┬───────┘ └─────────────────┘
          │
          ▼
┌─────────────────┐
│  Execution      │
│  Engine         │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Broker API     │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Exchange       │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Confirmation   │
└─────────────────┘
```

### 2. Backtesting Workflow
```
┌─────────────────┐
│  Strategy       │
│  Configuration  │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Data Loading   │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Indicator      │
│  Calculation    │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Signal         │
│  Generation     │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Order          │
│  Simulation     │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Performance    │
│  Calculation    │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Results        │
│  Generation     │
└─────────────────┘
```

### 3. Risk Management Workflow
```
┌─────────────────┐
│  Trade Request  │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Position Size  │
│  Validation     │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Concentration  │
│  Risk Check     │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  VaR Calculation│
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Correlation    │
│  Analysis       │
└─────────┬───────┘
          │
    ┌─────▼─────┐
    │  Approved │─────┐
    └───────────┘     │
          │           │
          ▼           ▼
┌─────────────────┐ ┌─────────────────┐
│  Execute Trade  │ │  Reject Trade   │
└─────────────────┘ └─────────────────┘
```

## Deployment Architecture

### Docker Configuration

#### Backend Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including TA-Lib
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
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend Dockerfile
```dockerfile
FROM node:18-alpine AS build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### Docker Compose
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/stocksteward
      - REDIS_URL=redis://redis:6379
      - KITE_API_KEY=${KITE_API_KEY}
      - KITE_ACCESS_TOKEN=${KITE_ACCESS_TOKEN}
    depends_on:
      - db
      - redis
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: stocksteward
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"

volumes:
  postgres_data:
```

## Security Architecture

### 1. Authentication & Authorization
- JWT-based authentication with refresh tokens
- OAuth2 with password flow
- Role-based access control (RBAC)
- Multi-factor authentication (MFA)
- Session management

### 2. Data Protection
- AES-256 encryption for sensitive data
- SSL/TLS for all communications
- Input validation and sanitization
- SQL injection prevention
- XSS protection

### 3. API Security
- Rate limiting per IP/user
- API key management
- Request validation
- CORS configuration
- CSRF protection

### 4. Infrastructure Security
- Network segmentation
- Firewall rules
- VPN access for admin
- Regular security audits
- Vulnerability scanning

## Monitoring & Observability

### 1. Logging
- Structured logging with correlation IDs
- Different log levels for different environments
- Centralized log aggregation
- Log retention policies

### 2. Metrics
- Application performance metrics
- Business metrics (trades, users, revenue)
- System resource metrics
- Custom business KPIs

### 3. Alerting
- Real-time alerting for critical issues
- Threshold-based alerts
- Escalation policies
- Integration with monitoring tools

### 4. Health Checks
- Application health endpoints
- Database connectivity checks
- External service availability
- Performance monitoring

## Troubleshooting Guide

### Common Issues & Solutions

#### 1. TA-Lib Installation Error
**Problem**: `ta-lib/ta_defs.h: No such file or directory`
**Solution**: Install TA-Lib C library before Python package
```bash
# On Ubuntu/Debian
sudo apt-get update
sudo apt-get install build-essential wget
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install

# On macOS
brew install ta-lib

# On Windows
Download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
```

#### 2. Database Connection Issues
**Problem**: Cannot connect to PostgreSQL
**Solution**: 
- Check database URL configuration
- Verify database service is running
- Ensure proper network connectivity
- Check credentials and permissions

#### 3. API Rate Limiting
**Problem**: Too many requests to broker API
**Solution**:
- Implement proper rate limiting
- Use caching for repeated requests
- Batch requests where possible
- Implement exponential backoff

#### 4. Memory Leaks
**Problem**: High memory usage over time
**Solution**:
- Implement proper garbage collection
- Monitor memory usage regularly
- Use memory profiling tools
- Optimize data structures

#### 5. Performance Issues
**Problem**: Slow response times
**Solution**:
- Optimize database queries
- Implement caching strategies
- Use CDN for static assets
- Optimize algorithms

## References

### 1. Technical Standards
- [PEP 8](https://peps.python.org/pep-0008/) - Python Style Guide
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

### 2. Trading Standards
- [FIX Protocol](https://www.fixtrading.org/)
- [Financial Industry Standards](https://www.finra.org/)
- [SEBI Guidelines](https://www.sebi.gov.in/)
- [NISM Certification](https://www.nism.ac.in/)

### 3. Security Standards
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CIS Controls](https://www.cisecurity.org/critical-controls/)
- [ISO 27001](https://www.iso.org/isoiec-27001-information-security.html)
- [PCI DSS](https://www.pcisecuritystandards.org/)

### 4. Libraries Used
- [TA-Lib](https://ta-lib.org/)
- [Pandas](https://pandas.pydata.org/)
- [NumPy](https://numpy.org/)
- [Scikit-learn](https://scikit-learn.org/)
- [TensorFlow](https://www.tensorflow.org/)

### 5. Architecture Patterns
- [Microservices Architecture](https://microservices.io/)
- [Event-Driven Architecture](https://www.eventdriven.io/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design](https://dddcommunity.org/)

---

## Appendices

### Appendix A: API Endpoints
```
GET    /api/v1/users/me                    - Get current user
POST   /api/v1/trades/place                - Place a trade
GET    /api/v1/portfolio/holdings          - Get portfolio holdings
POST   /api/v1/backtesting/run             - Run backtest
GET    /api/v1/strategies/list             - Get available strategies
POST   /api/v1/strategies/launch           - Launch a strategy
GET    /api/v1/market/tickers              - Get market tickers
GET    /api/v1/market/history              - Get historical data
```

### Appendix B: Database Schema
- User table: id, email, full_name, risk_tolerance, trading_mode
- Trade table: id, user_id, symbol, side, quantity, price, status
- Strategy table: id, user_id, name, parameters, status, performance
- Portfolio table: id, user_id, total_value, cash_balance, invested_amount

### Appendix C: Configuration Variables
- DATABASE_URL: PostgreSQL connection string
- REDIS_URL: Redis connection string
- KITE_API_KEY: Zerodha Kite API key
- KITE_ACCESS_TOKEN: Zerodha Kite access token
- GROQ_API_KEY: Groq API key for AI services
- SECRET_KEY: JWT secret key
- ALGORITHM: JWT algorithm (HS256)

This comprehensive architecture documentation provides a complete reference for the StockSteward AI platform, covering all aspects from high-level architecture to detailed implementation guidelines.