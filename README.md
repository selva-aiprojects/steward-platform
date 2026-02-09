# StockSteward AI

StockSteward AI is an advanced algorithmic trading platform that combines machine learning, real-time market data feeds, and sophisticated risk management to enable automated trading decisions. The system integrates with multiple data sources and brokers to provide both paper trading and live trading capabilities.

## Architecture Overview

The system follows a microservices architecture with the following key components:

### Core Services

1. **Data Integration Service** (`backend/app/services/data_integration.py`)
   - Integrates multiple data sources including NSE via KiteConnect, Kaggle datasets, Alpha Vantage, and Yahoo Finance
   - Provides preprocessing capabilities with technical indicators (SMA, EMA, MACD, RSI, Bollinger Bands)
   - Handles real-time and historical data retrieval
   - Implements fallback mechanisms for data availability

2. **Execution Engine** (`backend/app/execution/engine.py`)
   - Manages order placement and execution
   - Supports multiple order types (MARKET, LIMIT, STOP, TRAILING_STOP)
   - Implements algorithmic order types (TWAP, VWAP, PARTICIPATE, MIDPOINT)
   - Provides paper trading and live trading modes

3. **AI/ML Services** (`backend/app/services/enhanced_llm_service.py`)
   - Integrates multiple LLM providers (Groq, OpenAI, Anthropic, Hugging Face)
   - Performs market analysis and research
   - Generates trading signals based on market data
   - Implements multi-provider redundancy

4. **Kite Service** (`backend/app/services/kite_service.py`)
   - Handles Zerodha KiteConnect integration
   - Manages real-time market data feeds
   - Processes order execution for NSE

### Agent System

The platform implements an intelligent agent-based architecture:

1. **Orchestrator Agent** (`backend/app/agents/orchestrator.py`)
   - Coordinates the entire trading workflow
   - Manages data flow between agents
   - Handles error recovery and fallbacks

2. **User Profile Agent** (`backend/app/agents/user_profile.py`)
   - Retrieves and manages user-specific settings
   - Applies user-defined risk parameters
   - Checks account status and permissions

3. **Market Data Agent** (`backend/app/agents/market_data.py`)
   - Fetches real-time and historical market data
   - Provides normalized data for strategy consumption
   - Falls back to mock data when live data is unavailable

4. **Strategy Agent** (`backend/app/agents/strategy.py`)
   - Analyzes market data using LLMs
   - Generates trading signals (BUY, SELL, HOLD)
   - Implements risk management protocols

5. **Trade Decision Agent** (`backend/app/agents/trade_decision.py`)
   - Evaluates trading proposals
   - Applies risk management rules
   - Determines optimal position sizing

6. **Risk Management Agent** (`backend/app/agents/risk_management.py`)
   - Monitors portfolio risk
   - Enforces compliance rules
   - Implements kill switches

7. **Execution Agent** (`backend/app/agents/execution.py`)
   - Executes trades via broker interfaces
   - Manages execution modes (PAPER/LIVE)
   - Handles order confirmations

8. **Reporting Agent** (`backend/app/agents/reporting.py`)
   - Generates performance reports
   - Tracks trading metrics
   - Maintains audit trails

### Database Models

The system uses SQLAlchemy ORM with the following models:

- **User** (`backend/app/models/user.py`): User accounts and authentication
- **Portfolio** (`backend/app/models/portfolio.py`): Portfolio management and cash balances
- **Holding** (`backend/app/models/portfolio.py`): Individual stock holdings
- **Trade** (`backend/app/models/trade.py`): Trade execution records
- **Strategy** (`backend/app/models/strategy.py`): Trading strategies and parameters
- **Projection** (`backend/app/models/projection.py`): Financial projections
- **WatchlistItem** (`backend/app/models/watchlist.py`): User watchlists
- **Activity** (`backend/app/models/activity.py`): User activity logs
- **AuditLog** (`backend/app/models/audit_log.py`): Comprehensive audit trail
- **TradeApproval** (`backend/app/models/trade_approval.py`): Trade approval workflows
- **KYCApplication** (`backend/app/models/kyc.py`): Know Your Customer applications
- **PortfolioOptimizationResult** (`backend/app/models/optimization.py`): Portfolio optimization results
- **StrategyOptimizationResult** (`backend/app/models/optimization.py`): Strategy optimization results

### API Endpoints

The system exposes RESTful APIs under `/api/v1/`:

- `/users/` - User management
- `/portfolio/` - Portfolio operations
- `/trades/` - Trade execution
- `/backtesting/` - Backtesting capabilities
- `/strategies/` - Strategy management
- `/market-data/` - Market data retrieval
- `/reports/` - Reporting endpoints
- `/approvals/` - Trade approval workflows
- `/enhanced-ai/` - Advanced AI analytics
- `/portfolio-optimization/` - Portfolio optimization
- `/health/` - Health check endpoints

### Key Features

#### 1. Multi-Broker Support
- Paper trading simulation
- Live trading via broker integrations
- Order execution management
- Execution mode switching (PAPER/LIVE)

#### 2. Risk Management
- Position sizing algorithms
- Stop-loss and take-profit mechanisms
- Portfolio-level risk controls
- Compliance monitoring
- Global and user-level kill switches

#### 3. Backtesting Engine
- Historical data analysis
- Strategy performance evaluation
- Optimization capabilities
- Performance metrics calculation

#### 4. Real-time Analytics
- Live market data feeds
- Technical indicator calculations
- Sentiment analysis
- Market regime detection

#### 5. Compliance & Audit
- Comprehensive audit logging
- Trade approval workflows
- Regulatory compliance checks
- Activity monitoring
- Transaction recording

#### 6. Advanced AI Capabilities
- Multi-LLM provider support
- Market research and analysis
- Predictive modeling
- Sentiment analysis integration

#### 7. RAG (Retrieval Augmented Generation) System
- **Bronze Layer**: Raw data ingestion from multiple sources (NSE, Kaggle, Alpha Vantage, Yahoo Finance)
- **Silver Layer**: Data cleansing, transformation, and standardization
- **Gold Layer**: Feature engineering, indexing, and optimization for AI consumption
- Vector embeddings for semantic search and similarity matching
- Context-aware AI responses based on historical and real-time data

### Configuration

The system uses Pydantic for configuration management (`backend/app/core/config.py`):

- Database connection settings
- Broker API credentials
- LLM provider configurations
- Execution mode (PAPER_TRADING/LIVE_TRADING)
- Risk parameters
- API rate limits
- Feature flags

### Authentication & Authorization

- JWT-based authentication
- Role-based access control (RBAC)
- OAuth2 password flow
- Secure password hashing
- Session management

### Socket.IO Integration

Real-time communication for:
- Live market data feeds
- Trading notifications
- Portfolio updates
- System alerts
- Market mover updates

### Testing Framework

Comprehensive test coverage including:
- Unit tests for individual components
- Integration tests for service interactions
- Regression tests for critical functionality
- End-to-end testing
- Smoke tests for deployment validation

## Setup Instructions

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   # Copy .env.example to .env and configure values
   cp .env.example .env
   ```

3. Initialize the database:
   ```bash
   python -m alembic upgrade head
   ```

4. Start the application:
   ```bash
   uvicorn backend.app.main:app --reload
   ```

## Development

The system includes comprehensive testing and development tools:

- Smoke tests (`smoke_test.py`)
- Regression test suites (`tests/regression_suite.py`)
- API connectivity tests (`backend/test_api_connectivity.py`)
- Socket validation (`backend/validate_socket.py`)
- Integration tests (`backend/tests/integration_test.py`)
- Advanced strategy tests (`backend/tests/test_advanced_strategies.py`)

## Security

- Input validation and sanitization
- SQL injection prevention
- Cross-site scripting (XSS) protection
- Rate limiting
- Secure session management
- API key encryption
- Audit logging for security events

## Monitoring & Logging

- Structured logging with appropriate levels
- Performance monitoring
- Health check endpoints
- Error tracking and reporting
- Trade execution monitoring
- System resource monitoring

## Deployment

The system can be deployed using Docker containers with the provided `docker-compose.yml` file, supporting both development and production environments.

## Project Structure

```
backend/
├── app/
│   ├── agents/           # AI agents for trading workflow
│   ├── api/             # API endpoints
│   ├── core/            # Core configuration and database
│   ├── models/          # Database models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Core business logic services
│   ├── utils/           # Utility functions
│   ├── backtesting/     # Backtesting engine
│   ├── execution/       # Order execution engine
│   └── main.py          # Application entry point
├── alembic/             # Database migrations
├── tests/               # Test suite
└── requirements.txt     # Dependencies
```

## Documentation
Comprehensive documentation is available in the organized documentation hub:

- **[Documentation Hub](./DOCUMENTATION_HUB.md)** - Main entry point for all documentation
- **[User Manuals](./docs/user-manuals/)** - Role-specific guides for Trader, Auditor, Business Owner, and Super Admin
- **[Technical Documentation](./docs/technical-docs/)** - System architecture and technical specifications
- **[Requirements](./docs/requirements/)** - Software requirements and specifications
- **[Quality Assurance Report](./QUALITY_ASSURANCE_REPORT.md)** - Complete QA analysis and resolutions

## Key Technologies

- Python 3.9+
- FastAPI for web framework
- SQLAlchemy for ORM
- Socket.IO for real-time communication
- Pandas for data manipulation
- NumPy for numerical computations
- Pydantic for data validation
- Alembic for database migrations
- Docker for containerization
## Testing the Investment Workflow

To validate the complete investment workflow:

1. Create a trade user with appropriate credentials
2. Deposit funds (₹100,000 recommended for testing)
3. Create an investment strategy named "Smart Algo"
4. Add holdings for TCS, ICICI, and Reliance stocks
5. Verify that Portfolio page reflects all changes
6. Check that Investment Reports show the new strategy and holdings
7. Confirm General Reports also reflect the investment activity
8. Ensure reports pages do not auto-refresh, allowing users to view data without interruption

## Known Issues Fixed
- Reports pages no longer auto-refresh every 15 seconds
- Strategy creation properly authenticates with backend
- Investment flow guides users to select strategies before starting
- Portfolio and reports properly reflect user investments

## QA Validation Checklist
- [ ] User creation works properly
- [ ] Fund deposits are processed correctly
- [ ] Strategy creation succeeds without errors
- [ ] Holdings are added to portfolio
- [ ] Portfolio page shows accurate data
- [ ] Investment reports reflect changes
- [ ] General reports reflect changes
- [ ] No auto-refresh on reports pages
