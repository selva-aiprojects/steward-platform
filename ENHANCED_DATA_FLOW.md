# StockSteward AI - Enhanced Data Flow Documentation

## Overview

This document describes the enhanced data flow within the StockSteward AI system, from market data ingestion to trade execution. The system follows an agent-based architecture where different specialized agents process data in a sequential pipeline with improved reliability and performance.

## Enhanced Data Flow Architecture

### 1. Entry Point: Trade Request

The data flow begins when a trade request is initiated through the API:

```
Client Request → API Endpoint (/trades/) → TradeService → OrchestratorAgent
```

**Components Involved:**
- `backend/app/api/v1/endpoints/trades.py` - API endpoints for trade execution
- `backend/app/services/trade_service.py` - Business logic for trading
- `TradeService.execute_trade()` - Main entry point for trade execution

### 2. Orchestrator Agent Pipeline

The OrchestratorAgent manages the complete workflow through the following sequence:

#### Step 1: User Profile Agent
```
Input: user_id, context
Process: Retrieves user profile, settings, and permissions
Output: Updated context with user profile data
```

**Data Transformation:**
- Fetches user-specific settings (approval thresholds, confidence thresholds)
- Checks for global/user kill switches
- Updates execution mode based on user permissions
- Validates user authentication and authorization

#### Step 2: Market Data Agent
```
Input: symbol, exchange, execution_mode
Process: Fetches real-time or historical market data
Output: Market data with current prices, trends, and indicators
```

**Data Sources:**
- Real-time data from KiteConnect (for LIVE_TRADING)
- Historical data from multiple sources (NSE, Kaggle, Alpha Vantage, Yahoo Finance)
- Mock/fallback data when live data unavailable
- Technical indicators calculated from price data (SMA, EMA, MACD, RSI, Bollinger Bands)

#### Step 3: Strategy Agent
```
Input: market_data, user_profile
Process: Analyzes market data using LLMs
Output: Trading signal (BUY, SELL, HOLD) with rationale
```

**Data Processing:**
- Sends market data to LLM for analysis
- Generates trading signals based on technical indicators
- Includes risk assessment in the analysis
- Supports multiple LLM providers (Groq, OpenAI, Anthropic, Hugging Face)

#### Step 4: Trade Decision Agent
```
Input: market_data, strategy_output, user_profile
Process: Evaluates trading proposal
Output: Trade proposal with position sizing and pricing
```

**Data Processing:**
- Determines optimal position size based on risk parameters
- Calculates estimated trade value
- Creates detailed trade proposal
- Applies user-specific trading preferences

#### Step 5: Risk Management Agent
```
Input: trade_proposal, portfolio_state
Process: Validates trade against risk parameters
Output: Risk assessment and approval status
```

**Data Validation:**
- Checks portfolio cash balance against trade cost
- Validates trade against risk limits
- Ensures compliance with trading rules
- Implements kill switches and circuit breakers
- Performs portfolio-level risk analysis

#### Step 6: Execution Agent
```
Input: approved_trade_proposal, execution_mode
Process: Executes trade via broker interface
Output: Execution result and trade confirmation
```

**Execution Modes:**
- PAPER_TRADING: Simulated execution with mock broker
- LIVE_TRADING: Actual broker execution via KiteConnect
- Supports multiple order types (MARKET, LIMIT, STOP, TRAILING_STOP)
- Implements algorithmic orders (TWAP, VWAP, PARTICIPATE, MIDPOINT)

#### Step 7: Reporting Agent
```
Input: execution_result, trade_details
Process: Records trade and generates reports
Output: Audit trail and performance metrics
```

**Data Recording:**
- Logs trade to database in `trades` table
- Updates portfolio holdings in `holdings` table
- Updates portfolio cash balance
- Generates comprehensive audit trail in `audit_log` table
- Calculates and stores performance metrics

## Enhanced Data Flow Diagram

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   Client        │───▶│  API Endpoint    │───▶│  Trade Service   │
│                 │    │  (/trades/)      │    │                  │
└─────────────────┘    └──────────────────┘    └──────────────────┘
                                                        │
                                                        ▼
                                            ┌─────────────────────┐
                                            │  OrchestratorAgent  │
                                            └─────────────────────┘
                                                       │
          ┌────────────────────────────────────────────┼────────────────────────────────────────────┐
          │                                            │                                            │
    ┌─────────────────┐                        ┌─────────────────┐                        ┌─────────────────┐
    │User Profile     │                        │Market Data      │                        │Strategy         │
    │Agent            │                        │Agent            │                        │Agent            │
    └─────────────────┘                        └─────────────────┘                        └─────────────────┘
          │                                            │                                            │
          ▼                                            ▼                                            ▼
    ┌─────────────────┐                        ┌─────────────────┐                        ┌─────────────────┐
    │User Profile     │                        │Market Data      │                        │Trading Signal   │
    │Context Updated  │                        │with Indicators  │                        │(BUY/SELL/HOLD)  │
    └─────────────────┘                        └─────────────────┘                        └─────────────────┘
          │                                            │                                            │
          └────────────────────────────────────────────┼────────────────────────────────────────────┘
                                                       │
    ┌─────────────────┐                        ┌─────────────────┐                        ┌─────────────────┐
    │Trade Decision   │                        │Risk Management  │                        │Execution        │
    │Agent            │                        │Agent            │                        │Agent            │
    └─────────────────┘                        └─────────────────┘                        └─────────────────┘
          │                                            │                                            │
          ▼                                            ▼                                            ▼
    ┌─────────────────┐                        ┌─────────────────┐                        ┌─────────────────┐
    │Trade Proposal   │                        │Risk Assessment  │                        │Execution Result │
    │Created          │                        │and Approval     │                        │and Confirmation │
    └─────────────────┘                        └─────────────────┘                        └─────────────────┘
          │                                            │                                            │
          └────────────────────────────────────────────┼────────────────────────────────────────────┘
                                                       │
                                            ┌─────────────────────┐
                                            │   Reporting Agent   │
                                            │                     │
                                            └─────────────────────┘
                                                       │
                                                       ▼
                                            ┌─────────────────────┐
                                            │   Audit Trail &     │
                                            │   Performance Data  │
                                            └─────────────────────┘
```

## Database Schema and Data Integrity

### Core Tables
- `users` - User accounts with permissions and risk profiles
- `portfolios` - Portfolio management with cash balances and performance metrics
- `holdings` - Individual stock holdings with average price and P&L
- `trades` - Records all trade executions with status, pricing, and metadata
- `trade_approvals` - Approval workflow tracking with status and rationale
- `audit_log` - Comprehensive audit trail of all system activities

### Data Integrity Measures
- Foreign key constraints to maintain referential integrity
- Unique constraints to prevent duplicate entries
- Check constraints to enforce business rules
- Indexes on frequently queried fields for performance
- Transaction boundaries to ensure atomicity

## High Availability and Performance Optimizations

### Database Optimization
- Connection pooling with SQLAlchemy
- Read replicas for analytical queries
- Query optimization with proper indexing
- Caching layer (Redis) for frequently accessed data
- Asynchronous operations to improve throughput

### Latency Reduction Strategies
- In-memory caching for market data
- Connection pooling for database operations
- Asynchronous processing for heavy computations
- CDN for static assets
- WebSocket connections for real-time updates

## Real-time Data Flow

### WebSocket Integration
```
Market Data Feed → WebSocket Server → Client Updates
```

**Components:**
- `backend/app/main.py` - Socket.IO server managing connections
- Real-time market updates pushed to subscribed clients
- Portfolio value updates reflected in real-time
- Trading notifications and alerts
- Market mover updates for top gainers/losers

### Real-time Data Processing:
1. Market data received from KiteConnect streaming API
2. Data processed and enriched with technical indicators
3. Updates pushed to connected clients via Socket.IO
4. Clients update UI elements in real-time

## Error Handling and Fallbacks

### Data Availability Fallbacks
1. Primary: Live market data from KiteConnect
2. Secondary: Historical data from multiple sources
3. Tertiary: Mock data for testing and fallback scenarios

### Execution Mode Fallbacks
1. LIVE_TRADING: Actual broker execution (production only)
2. PAPER_TRADING: Simulated execution (development/testing/default)
3. Environment-based guards prevent live trading in non-production

### Failure Recovery
- Comprehensive error logging with context and trace IDs
- Graceful degradation to fallback modes
- Audit trail for failed transactions
- Automatic retry mechanisms for transient failures
- Circuit breaker patterns for external service failures

## Security and Compliance

### Data Protection
- Input validation at all entry points using Pydantic schemas
- Parameterized queries to prevent SQL injection
- Encrypted sensitive data storage (API keys, credentials)
- JWT token validation and refresh mechanisms
- Rate limiting to prevent abuse

### Audit Trail
- Complete transaction logging with trace IDs
- User activity tracking across all system components
- Compliance reporting with required regulatory information
- Immutable audit logs for forensic analysis

## Performance Considerations

### Caching Strategy
- Market data caching with TTL to reduce API calls
- User profile caching to minimize database queries
- Technical indicator pre-computation for frequently accessed data
- Redis-based caching layer for high-frequency data

### Asynchronous Processing
- Non-blocking I/O operations throughout the system
- Parallel data fetching from multiple sources
- Background task processing for heavy computations
- Async/await patterns for improved throughput

### Database Optimization
- Connection pooling for efficient database access
- Indexing strategies for frequently queried fields
- Batch operations for bulk data processing
- Read replicas for analytical queries

## Integration Points

### External APIs
- KiteConnect (NSE data and live trading execution)
- Multiple LLM providers (Groq, OpenAI, Anthropic, Hugging Face)
- Alternative data sources (Alpha Vantage, Yahoo Finance, Kaggle)

### Internal Services
- Database services (PostgreSQL/SQLite with SQLAlchemy ORM)
- Authentication services (JWT-based with refresh tokens)
- Notification services (WebSocket for real-time updates)
- Caching services (Redis for performance optimization)

## Configuration Management

The system uses Pydantic for configuration validation:

- Environment-specific settings (development, staging, production)
- Feature flags for gradual rollouts
- API rate limits and connection pooling
- Risk parameter defaults and overrides
- External service timeouts and retry policies

This comprehensive data flow ensures that all trading activities are properly validated, recorded, and compliant with risk management policies while providing real-time market data processing and intelligent decision making through the agent-based architecture.