# StockSteward AI - Data Flow Documentation

## Overview

This document describes the data flow within the StockSteward AI system, from market data ingestion to trade execution. The system follows an agent-based architecture where different specialized agents process data in a sequential pipeline.

## Data Flow Architecture

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

## Data Flow Diagram

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

## Example Data Flow

### Example 1: Simple BUY Trade Request

**Initial Request:**
```json
{
  "symbol": "RELIANCE",
  "quantity": 10,
  "action": "BUY",
  "user_id": 1,
  "execution_mode": "PAPER_TRADING"
}
```

**Step-by-step Flow:**

1. **API Layer:**
   - Receives trade request via POST /trades/
   - Validates input parameters using Pydantic schemas
   - Authenticates user via JWT token
   - Passes to TradeService

2. **Trade Service:**
   - Creates initial context with trace ID for audit trail:
     ```python
     context = {
       "user_id": 1,
       "symbol": "RELIANCE",
       "execution_mode": "PAPER_TRADING",
       "manual_override": {...},
       "trace_id": "uuid-v4-string"
     }
     ```

3. **User Profile Agent:**
   - Fetches user profile for user_id=1 from database
   - Updates context with user-specific settings (approval_threshold, confidence_threshold)
   - Confirms trading is not suspended
   - Checks global kill switch status

4. **Market Data Agent:**
   - Fetches current RELIANCE price (e.g., ₹2,450.00) from KiteConnect
   - Calculates technical indicators (SMA, RSI, MACD, Bollinger Bands, etc.)
   - Returns market data with comprehensive indicators:
     ```python
     {
       "market_data": {
         "symbol": "RELIANCE",
         "current_price": 2450.00,
         "volume": 1000000,
         "trend": "BULLISH",
         "rsi": 62.5,
         "sma_20": 2420.30,
         "sma_50": 2380.45,
         "macd": 12.34,
         "bb_upper": 2500.00,
         "bb_lower": 2400.00,
         "volatility": 2.5,
         "source": "Zerodha KiteConnect Live"
       }
     }
     ```

5. **Strategy Agent:**
   - Sends market data to configured LLM provider for analysis
   - Receives BUY signal with confidence score of 0.85
   - Returns strategy output with detailed rationale:
     ```python
     {
       "signal": "BUY",
       "confidence": 0.85,
       "rationale": "Technical indicators show bullish trend with RSI in optimal range (30-70), MACD above signal line, and price above both 20-day and 50-day SMAs",
       "recommendation_confidence": 0.85
     }
     ```

6. **Trade Decision Agent:**
   - Calculates position size based on user risk parameters and portfolio value
   - Creates detailed trade proposal with pricing and risk metrics:
     ```python
     {
       "trade_proposal": {
         "symbol": "RELIANCE",
         "action": "BUY",
         "quantity": 10,
         "estimated_price": 2450.00,
         "estimated_total": 24500.00,
         "position_size_percentage": 0.05,
         "risk_per_share": 24.50,
         "stop_loss_price": 2327.50,  // 5% below entry
         "take_profit_price": 2572.50  // 5% above entry
       }
     }
     ```

7. **Risk Management Agent:**
   - Queries database to retrieve current portfolio state
   - Verifies sufficient cash balance (₹24,500 needed vs. ₹50,000 available)
   - Confirms trade complies with risk limits (position size < 10% of portfolio)
   - Approves the trade and assigns risk score:
     ```python
     {
       "risk_assessment": {
         "approved": True,
         "risk_score": 0.3,
         "reason": "Trade approved within risk parameters",
         "portfolio_impact": "5% of total portfolio value"
       }
     }
     ```

8. **Execution Agent:**
   - Executes trade in paper trading mode using mock broker
   - Records execution details including actual price, fees, and timestamp
   - Returns execution confirmation:
     ```python
     {
       "execution_result": {
         "status": "EXECUTED",
         "order_id": "PAPER_123456",
         "executed_price": 2450.00,
         "executed_quantity": 10,
         "fees": 0.00,  // Paper trading has no fees
         "timestamp": "2023-06-15T10:30:00Z"
       }
     }
     ```

9. **Reporting Agent:**
   - Logs completed trade to `trades` table in database
   - Updates `holdings` table to reflect new RELIANCE position
   - Updates portfolio cash balance
   - Generates comprehensive audit trail entry in `audit_log` table
   - Calculates and stores performance metrics

### Example 2: High-Value Trade Requiring Approval

For trades exceeding the approval threshold:

```
Trade Value > Approval Threshold
        │
        ▼
    Risk Management Agent
        │
        ▼
    Creates TradeApproval Record in DB
        │
        ▼
    Returns PENDING_APPROVAL Status
        │
        ▼
    Awaiting Manual Approval via Admin Interface
        │
        ▼
    Admin Approves via /approvals/{id}/approve endpoint
        │
        ▼
    Resume Execution Flow
```

**Detailed Process:**
1. Risk Management Agent detects trade value exceeds user's approval threshold
2. Creates `TradeApproval` record in database with status "PENDING"
3. Returns early with "PENDING_APPROVAL" status
4. Admin reviews trade via approval interface
5. Upon approval, system resumes execution with approval ID
6. Execution continues with validated approval

## Data Models and Storage

### Market Data Flow
```
External Data Source → Data Integration Service → Preprocessing → Storage
```

**Key Components:**
- `DataIntegrationService` - Handles multiple data sources (NSE, Kaggle, Alpha Vantage, Yahoo Finance)
- Technical indicator calculations (SMA, EMA, MACD, RSI, Bollinger Bands)
- Data normalization and standardization
- Data validation and cleansing

### RAG (Retrieval Augmented Generation) Data Flow

The system implements a three-tier data architecture for AI/ML processing:

#### Bronze Layer (Raw Data)
```
External Sources → Raw Data Ingestion → Data Lake Storage
```

**Characteristics:**
- Stores raw, unprocessed data in original format
- Preserves all original attributes and metadata
- Sources include:
  - NSE historical data via KiteConnect
  - Kaggle datasets
  - Alpha Vantage API responses
  - Yahoo Finance data
  - Custom data uploads
- Immutable storage for audit and recovery purposes

#### Silver Layer (Cleansed Data)
```
Bronze Layer → Data Cleansing → Transformation → Structured Storage
```

**Processing Steps:**
- Data validation and quality checks
- Missing value imputation
- Outlier detection and handling
- Schema validation and enforcement
- Duplicate removal
- Standardization of formats and units

**Transformations:**
- Column renaming to standard schema
- Data type conversions
- Date/time normalization
- Currency conversion if needed
- Technical indicator calculations

#### Gold Layer (Curated Data)
```
Silver Layer → Feature Engineering → Indexing → Optimized Storage
```

**Processing Steps:**
- Feature extraction and selection
- Dimensionality reduction
- Index creation for fast retrieval
- Aggregation and summarization
- Quality scoring and metadata enrichment

**Indexing Strategy:**
- Vector embeddings for semantic search
- Time-series indexing for temporal queries
- Symbol-based indexing for asset-specific queries
- Technical indicator indexing for pattern matching

### Trade Data Flow
```
Trade Proposal → Validation → Risk Assessment → Execution → Storage
```

**Database Tables:**
- `trades` - Records all trade executions with status, pricing, and metadata
- `portfolios` - Portfolio management with cash balances and performance metrics
- `holdings` - Individual stock holdings with average price and P&L
- `trade_approvals` - Approval workflow tracking with status and rationale
- `audit_log` - Comprehensive audit trail of all system activities
- `users` - User accounts with permissions and risk profiles

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