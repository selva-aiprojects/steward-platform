# StockSteward AI - Technical Design Document (LLD)

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Component Design](#component-design)
3. [Database Design](#database-design)
4. [API Design](#api-design)
5. [Security Architecture](#security-architecture)
6. [Workflow Design](#workflow-design)
7. [Performance Considerations](#performance-considerations)
8. [Scalability Design](#scalability-design)
9. [Monitoring and Logging](#monitoring-and-logging)
10. [Recent Pilot-Oriented LLD Updates](#recent-pilot-oriented-lld-updates)

## Recent Pilot-Oriented LLD Updates

This section reflects production-aligned behavior implemented for pilot users.

### A) Runtime entrypoint and websocket transport
- Backend runtime entrypoint for local/prod socket support:
  - `app.main:socket_app` (Socket.IO ASGI wrapper over FastAPI app)
- Frontend consumes:
  - REST APIs for snapshots and cards
  - Socket streams (`market_movers`, `ticker_batch`, `market_update`, `steward_prediction`)

### B) Market data reliability and metadata contract
- All primary market endpoints now expose operational metadata fields:
  - `source` (provider id)
  - `status` (`LIVE` | `STALE` | `UNAVAILABLE`)
  - `as_of` (ISO timestamp)
- Added health endpoint for provider observability:
  - `GET /api/v1/market/health`
  - includes provider call/failure/latency stats

### C) Market provider layering
- Primary feed chain is designed with fallback/cooldown behavior:
  1. Yahoo quote/chart paths
  2. yfinance fallback
  3. TrueData fallback (when key configured)
- No mock values are injected into live market cards on failure; payloads are marked `UNAVAILABLE` or `STALE`.

### D) Order book depth behavior
- `GET /api/v1/market/depth` now derives bid/ask ladder from current live anchor price (`ltp`) instead of static constants.
- Response includes `symbol`, `ltp`, `source`, `status`, `as_of`, `bids`, `asks`.

### E) Strategy and pilot progress bootstrap
- Strategy create path:
  - `POST /api/v1/strategies/`
  - creates strategy in `PAPER_TRADING` mode for pilot flow
- Added pilot seeding endpoint for existing users:
  - `POST /api/v1/strategies/pilot/bootstrap`
  - role-gated: `SUPERADMIN` / `BUSINESS_OWNER`
  - ensures first-time users can see strategy/portfolio progress

### F) Manual paper-order seeding for dashboard/report validation
- Added:
  - `POST /api/v1/trades/paper/seed-all?orders_per_user=<n>`
  - role-gated: `SUPERADMIN` / `BUSINESS_OWNER`
  - creates executed paper trades across active trader-type users
  - intended for dashboard, portfolio, reports, and investment-reports verification

### G) Frontend flow alignment
- Dashboard CTA `Launch Strategy` routes to `/strategies`.
- Strategy confirmation includes direct navigation to:
  - Dashboard (`/`)
  - Portfolio (`/portfolio`)
- Top Movers rendered in two explicit sections:
  - Gainers (5)
  - Losers (5)
- Vertical tickers (currencies, commodities, metals) patch prices from socket `ticker_batch`.

### H) Dependency constraints (deployment)
- Current compatible pins for market stack:
  - `yfinance==1.1.0`
  - `websockets==13.1` (required by yfinance>=1.1.0)

## System Architecture

### High-Level Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │────│   Load Balancer  │────│   Backend API   │
│   (React)       │    │   (Nginx)        │    │   (FastAPI)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                      │
                                                      ▼
                                            ┌─────────────────┐
                                            │   Database      │
                                            │   (PostgreSQL)  │
                                            └─────────────────┘
                                                      │
                                                      ▼
                                            ┌─────────────────┐
                                            │   Message Queue │
                                            │   (Redis/RQ)    │
                                            └─────────────────┘
                                                      │
                                                      ▼
                                            ┌─────────────────┐
                                            │   External APIs │
                                            │   (Kite, LLMs)  │
                                            └─────────────────┘
```

### Technology Stack
- **Frontend**: React.js, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python 3.11
- **Database**: PostgreSQL
- **Message Queue**: Redis, RQ (Redis Queue)
- **Authentication**: JWT Tokens
- **WebSockets**: Socket.IO
- **Containerization**: Docker, Docker Compose
- **Deployment**: Kubernetes/Docker Swarm

### Microservices Approach
The system follows a microservices architecture with the following services:
- **Authentication Service**: User authentication and authorization
- **Trading Service**: Trade execution and management
- **Portfolio Service**: Portfolio management and analytics
- **Market Data Service**: Market data ingestion and processing
- **Risk Management Service**: Risk calculation and monitoring
- **Reporting Service**: Report generation and analytics
- **Notification Service**: User notifications and alerts

## Component Design

### Core Components

#### 1. User Management Component
- **Purpose**: Handle user registration, authentication, and role management
- **Classes**: User, Role, Permission
- **Services**: UserService, AuthService, RBACService
- **Interfaces**: IUserService, IAuthService

#### 2. Trading Engine Component
- **Purpose**: Execute trades and manage trading workflows
- **Classes**: Trade, Order, Execution
- **Services**: TradeService, OrderService, ExecutionService
- **Interfaces**: ITradeService, IOrderService

#### 3. Portfolio Management Component
- **Purpose**: Manage user portfolios and holdings
- **Classes**: Portfolio, Holding, Asset
- **Services**: PortfolioService, HoldingService
- **Interfaces**: IPortfolioService

#### 4. Risk Management Component
- **Purpose**: Calculate and monitor risk metrics
- **Classes**: RiskMetric, RiskProfile, RiskAssessment
- **Services**: RiskService, RiskCalculator
- **Interfaces**: IRiskService

#### 5. Market Data Component
- **Purpose**: Ingest and process market data
- **Classes**: MarketData, Quote, Indicator
- **Services**: MarketDataService, DataProvider
- **Interfaces**: IMarketDataService

### Component Interactions
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  User Mgmt      │────│  Auth Service    │────│  Trading Eng    │
│  Component      │    │  Component       │    │  Component      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                        │
         └───────────────────────┼────────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Portfolio Mgmt │
                    │  Component      │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Risk Mgmt      │
                    │  Component      │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Market Data    │
                    │  Component      │
                    └─────────────────┘
```

## Database Design

### Entity Relationship Diagram (ERD)

```
Users (1) ─────── (M) UserSessions
   │
   │ (1)
   ├────────────── Portfolios (M)
   │                   │
   │                   │ (M)
   │                   ├────────────── Holdings (M)
   │
   │ (M)
   ├────────────── Trades (M)
   │                   │
   │                   │ (1)
   └────────────────── TradeApprovals (M)
   
Portfolios (1) ─────── (M) Holdings
Portfolios (1) ─────── (M) Trades

AuditLogs (M) ─────── Users (1)
WatchlistItems (M) ─── Users (1), Securities (1)
```

### Core Tables

#### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    risk_tolerance VARCHAR(20) DEFAULT 'MODERATE',
    trading_mode VARCHAR(20) DEFAULT 'AUTO',
    role VARCHAR(50) DEFAULT 'TRADER',
    allowed_sectors TEXT DEFAULT 'ALL',
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    trading_suspended BOOLEAN DEFAULT FALSE,
    approval_threshold DECIMAL(10,2),
    confidence_threshold DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### Portfolios Table
```sql
CREATE TABLE portfolios (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    cash_balance DECIMAL(15,2) DEFAULT 0.00,
    invested_amount DECIMAL(15,2) DEFAULT 0.00,
    win_rate DECIMAL(5,2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### Holdings Table
```sql
CREATE TABLE holdings (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER REFERENCES portfolios(id),
    symbol VARCHAR(20) NOT NULL,
    quantity INTEGER DEFAULT 0,
    avg_price DECIMAL(10,2) DEFAULT 0.00,
    current_price DECIMAL(10,2) DEFAULT 0.00,
    pnl DECIMAL(10,2) DEFAULT 0.00,
    pnl_pct DECIMAL(5,2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### Trades Table
```sql
CREATE TABLE trades (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    portfolio_id INTEGER REFERENCES portfolios(id),
    symbol VARCHAR(20) NOT NULL,
    action VARCHAR(10) NOT NULL, -- BUY, SELL
    quantity INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING', -- PENDING, EXECUTED, REJECTED, FAILED
    execution_mode VARCHAR(20) DEFAULT 'PAPER_TRADING', -- PAPER_TRADING, LIVE_TRADING
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    risk_score DECIMAL(5,2),
    rejection_reason TEXT,
    pnl VARCHAR(20), -- e.g. "+2.41%"
    decision_logic TEXT,
    market_behavior TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### Audit Logs Table
```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    admin_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes for Performance
```sql
-- Users table indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_active ON users(is_active);

-- Trades table indexes
CREATE INDEX idx_trades_user_id ON trades(user_id);
CREATE INDEX idx_trades_portfolio_id ON trades(portfolio_id);
CREATE INDEX idx_trades_symbol ON trades(symbol);
CREATE INDEX idx_trades_status ON trades(status);
CREATE INDEX idx_trades_timestamp ON trades(timestamp);

-- Portfolios table indexes
CREATE INDEX idx_portfolios_user_id ON portfolios(user_id);

-- Holdings table indexes
CREATE INDEX idx_holdings_portfolio_id ON holdings(portfolio_id);
CREATE INDEX idx_holdings_symbol ON holdings(symbol);

-- Composite indexes
CREATE INDEX idx_trades_user_status ON trades(user_id, status);
CREATE INDEX idx_trades_symbol_timestamp ON trades(symbol, timestamp DESC);
CREATE INDEX idx_holdings_portfolio_symbol ON holdings(portfolio_id, symbol);
```

## API Design

### REST API Endpoints

#### Authentication Endpoints
```
POST /auth/login          - User login
POST /auth/register       - User registration
POST /auth/refresh        - Token refresh
POST /auth/logout         - User logout
GET  /auth/me             - Get current user info
PUT  /auth/me             - Update current user info
```

#### User Management Endpoints
```
GET    /users/            - Get all users (admin only)
GET    /users/{id}        - Get user by ID
PUT    /users/{id}        - Update user
DELETE /users/{id}        - Deactivate user
GET    /users/{id}/trades - Get user's trades
GET    /users/{id}/portfolio - Get user's portfolio
```

#### Trading Endpoints
```
POST   /trades/           - Create new trade
GET    /trades/           - Get all trades (filtered)
GET    /trades/{id}       - Get specific trade
PUT    /trades/{id}       - Update trade (admin only)
GET    /trades/user/{user_id} - Get trades for specific user
POST   /trades/cancel/{id} - Cancel pending trade
```

#### Portfolio Endpoints
```
GET    /portfolio/        - Get all portfolios (filtered)
GET    /portfolio/{id}    - Get specific portfolio
PUT    /portfolio/{id}    - Update portfolio
POST   /portfolio/        - Create new portfolio
GET    /portfolio/{id}/holdings - Get portfolio holdings
GET    /portfolio/{id}/performance - Get portfolio performance
```

#### Market Data Endpoints
```
GET    /market/movers      - Top gainers/losers with source/status/as_of
GET    /market/currencies  - Live currency movers
GET    /market/metals      - Live metals movers
GET    /market/commodities - Live commodity movers
GET    /market/macro       - Macro indicators (USDINR, gold, crude)
GET    /market/depth       - Live anchored order book ladder
GET    /market/health      - Provider latency/failure stats
GET    /market/status      - Exchange session status
```

#### Risk Management Endpoints
```
GET    /risk/portfolio/{portfolio_id} - Get portfolio risk metrics
GET    /risk/user/{user_id} - Get user risk profile
POST   /risk/assess       - Assess risk for trade
GET    /risk/limits       - Get risk limits
PUT    /risk/limits       - Update risk limits
```

### API Request/Response Examples

#### Trade Creation Request
```json
{
  "symbol": "RELIANCE",
  "action": "BUY",
  "quantity": 10,
  "price": 2450.00,
  "type": "MARKET",
  "decision_logic": "AI recommendation based on technical analysis"
}
```

#### Trade Creation Response
```json
{
  "id": 123,
  "user_id": 1,
  "portfolio_id": 1,
  "symbol": "RELIANCE",
  "action": "BUY",
  "quantity": 10,
  "price": 2450.00,
  "status": "EXECUTED",
  "execution_mode": "PAPER_TRADING",
  "timestamp": "2023-06-15T10:30:00Z",
  "risk_score": 0.3,
  "pnl": "+2.41%",
  "decision_logic": "AI recommendation based on technical analysis"
}
```

## Security Architecture

### Authentication Flow
```
1. User enters credentials
2. Credentials verified against database
3. JWT token generated with user claims
4. Token returned to client
5. Client includes token in Authorization header
6. API validates token on each request
7. User identity extracted from token
8. RBAC checks performed
9. Request processed
```

### Authorization Model (RBAC)
- **Roles**: SUPERADMIN, BUSINESS_OWNER, TRADER, AUDITOR
- **Permissions**: Granular permissions based on role
- **Resource Access**: Fine-grained access control

#### Role Permissions Matrix
| Feature | SUPERADMIN | BUSINESS_OWNER | TRADER | AUDITOR |
|---------|------------|----------------|--------|---------|
| View Users | ✓ | ✓ | | ✓ |
| Edit Users | ✓ | | | |
| Create Trades | ✓ | ✓ | ✓ | |
| View Trades | ✓ | ✓ | ✓ | ✓ |
| Cancel Trades | ✓ | ✓ | ✓ | |
| Portfolio Management | ✓ | ✓ | ✓ | |
| Risk Management | ✓ | ✓ | | |
| System Configuration | ✓ | | | |
| Audit Logs | ✓ | | | ✓ |
| Compliance Reports | ✓ | | | ✓ |

### Security Measures
- **JWT Tokens**: Stateless authentication with expiration
- **Password Hashing**: PBKDF2-SHA256 with salt
- **Rate Limiting**: Prevent brute force attacks
- **Input Validation**: Sanitize all inputs
- **SQL Injection Prevention**: Parameterized queries
- **XSS Prevention**: Content Security Policy
- **CSRF Protection**: Token-based protection

## Workflow Design

### Core Business Workflows

#### 1. Trade Execution Workflow
```
┌─────────────────┐
│   User Request  │
│   (Buy/Sell)    │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Authentication │
│  & Authorization│
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  User Profile   │
│  Agent          │
│  - Fetch user   │
│  - Check limits │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Market Data    │
│  Agent          │
│  - Get quotes   │
│  - Calculate    │
│  - indicators   │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Strategy Agent │
│  - Analyze data │
│  - Generate     │
│  - signal       │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Trade Decision │
│  Agent          │
│  - Calculate    │
│  - position     │
│  - size         │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Risk Management│
│  Agent          │
│  - Validate     │
│  - compliance   │
│  - Check limits │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Execution      │
│  Agent          │
│  - Execute      │
│  - trade        │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Reporting      │
│  Agent          │
│  - Log trade    │
│  - Update       │
│  - portfolio    │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│   Response      │
│   to User       │
└─────────────────┘
```

#### 2. User Registration Workflow
```
┌─────────────────┐
│  User Submits   │
│  Registration   │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Input         │
│  Validation    │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Email         │
│  Verification  │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Password      │
│  Hashing       │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  User Profile  │
│  Creation      │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Portfolio     │
│  Initialization│
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Welcome       │
│  Notification  │
└─────────────────┘
```

#### 3. Risk Assessment Workflow
```
┌─────────────────┐
│  Trade Request │
│  or Portfolio  │
│  Change        │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Risk Factors  │
│  Identification│
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Quantitative  │
│  Risk Analysis │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Qualitative   │
│  Risk Analysis │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Risk Score    │
│  Calculation   │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Threshold     │
│  Comparison    │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Decision      │
│  Making        │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Action        │
│  Execution     │
└─────────────────┘
```

### State Management

#### Trade States
```
PENDING → EXECUTED
   │           │
   │           ▼
   └→ REJECTED ←┘
   │
   └→ FAILED
```

#### User States
```
INACTIVE → ACTIVE → SUSPENDED
     │         │         │
     └─────────┼─────────┘
               │
         DEACTIVATED
```

## Performance Considerations

### Caching Strategy
- **Redis Cache**: Cache frequently accessed data
- **CDN**: Serve static assets from CDN
- **Browser Cache**: Leverage browser caching
- **Database Cache**: Optimize database query caching

### Database Optimization
- **Connection Pooling**: Use SQLAlchemy connection pooling
- **Query Optimization**: Optimize queries with proper indexing
- **Read Replicas**: Use read replicas for reporting
- **Partitioning**: Partition large tables by date

### API Performance
- **Pagination**: Implement pagination for large datasets
- **Batch Operations**: Support batch operations
- **Async Processing**: Use async/await for I/O operations
- **Rate Limiting**: Implement rate limiting to prevent abuse

### Frontend Performance
- **Code Splitting**: Split code into chunks
- **Lazy Loading**: Load components on demand
- **Image Optimization**: Optimize images and media
- **Bundle Size**: Minimize bundle size

## Scalability Design

### Horizontal Scaling
- **Load Balancer**: Distribute traffic across multiple instances
- **Stateless Services**: Design services to be stateless
- **Database Sharding**: Shard database when needed
- **Microservices**: Scale individual services independently

### Vertical Scaling
- **Resource Allocation**: Increase resources for critical services
- **Database Tuning**: Optimize database configuration
- **Caching**: Increase cache capacity
- **CDN**: Expand CDN capacity

### Auto-scaling
- **Kubernetes**: Use Kubernetes for auto-scaling
- **Cloud Services**: Leverage cloud auto-scaling features
- **Monitoring**: Monitor metrics for scaling decisions
- **Load Testing**: Regular load testing to determine scaling needs

## Monitoring and Logging

### Application Monitoring
- **Metrics Collection**: Collect performance metrics
- **Health Checks**: Implement health check endpoints
- **Performance Monitoring**: Monitor response times
- **Error Tracking**: Track and alert on errors

### Logging Strategy
- **Structured Logging**: Use structured logging format
- **Log Levels**: Use appropriate log levels
- **Centralized Logging**: Centralize logs with ELK stack
- **Log Retention**: Implement log retention policies

### Alerting
- **Threshold Alerts**: Alert on metric thresholds
- **Error Alerts**: Alert on critical errors
- **Performance Alerts**: Alert on performance degradation
- **Security Alerts**: Alert on security events

---

*This document serves as the low-level design specification for the StockSteward AI platform.*
