# StockSteward AI - Advanced Agentic AI-Driven Stock Stewardship Platform

## Overview

StockSteward AI is a sophisticated agentic AI-driven stock stewardship platform that combines multiple LLM providers (Groq/Llama/OpenAI/Anthropic/HuggingFace) with comprehensive financial data integration (NSE Historical + Kaggle + Public datasets). The platform enables users to develop, backtest, and execute trading strategies with comprehensive risk management and real-time market analysis.

## Key Features

### 1. Multi-LLM Provider Integration
- **Groq (Llama models)**: Fast inference for real-time analysis
- **OpenAI (GPT models)**: Advanced reasoning and complex analysis
- **Anthropic (Claude models)**: Safety-focused financial insights
- **Hugging Face (FinGPT/DeepSeek)**: Specialized financial models
- Automatic fallback between providers for reliability

### 2. Multi-Source Data Integration
- **NSE Live Data**: Real-time market feeds via Zerodha KiteConnect
- **Historical Datasets**: NSE historical data for backtesting
- **Kaggle Datasets**: Financial and market datasets
- **Public APIs**: Alpha Vantage, Yahoo Finance, and more
- **Custom Data Sources**: CSV, Excel, Parquet file support

### 3. Advanced Backtesting Engine
- Realistic market simulation with slippage and commission modeling
- Support for multiple order types (MARKET, LIMIT, STOP, etc.)
- Performance metrics (Sharpe ratio, max drawdown, win rate, etc.)
- Parameter optimization capabilities

### 4. Comprehensive Risk Management
- Position size limits
- Value at Risk (VaR) calculations
- Concentration risk monitoring
- Real-time risk alerts
- Stop-loss and take-profit controls

### 5. Multiple Trading Strategies
- SMA Crossover Strategy
- RSI Mean Reversion
- MACD Crossover
- Bollinger Bands Strategy
- Advanced technical analysis strategies

### 6. Real-time Market Intelligence
- Live market feeds from multiple exchanges (NSE, BSE, MCX)
- Technical indicator calculations
- Market sentiment analysis
- Sector rotation signals
- AI-powered market predictions

### 7. Portfolio Intelligence
- AI-powered market analysis
- Performance tracking
- Risk analytics
- Allocation optimization
- Multi-asset portfolio management

## Architecture

### Enhanced Tech Stack
- **Frontend**: React 18, TypeScript, Tailwind CSS, Socket.io
- **Backend**: Python 3.11, FastAPI, SQLAlchemy, PostgreSQL
- **AI/ML Stack**:
  - LLM Providers: Groq (Llama), OpenAI (GPT), Anthropic (Claude), Hugging Face (FinGPT/DeepSeek)
  - Libraries: Transformers, PyTorch, scikit-learn, TA-Lib, yfinance
- **Data Integration**:
  - Live: Zerodha KiteConnect (NSE/BSE)
  - Historical: NSE datasets, Kaggle financial datasets
  - Public: Alpha Vantage, Yahoo Finance APIs
- **Database**: PostgreSQL, Redis (caching)
- **Infrastructure**: Docker, Docker Compose

### System Components
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │◄──►│   Backend API    │◄──►│  Broker APIs    │
│   (React)       │    │   (FastAPI)      │    │ (Kite, etc.)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │   Message Queue   │
                    │   (Redis/RabbitMQ)│
                    └─────────┬─────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌────────▼────────┐   ┌───────▼────────┐
│  ML Service    │   │  Risk Manager   │   │  Execution     │
│  (AI Models)   │   │                 │   │  Engine        │
└────────────────┘   └─────────────────┘   └────────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   Database        │
                    │   (PostgreSQL)    │
                    └───────────────────┘
```

## Prerequisites

### System Requirements
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL (or Docker for containerized setup)
- At least 4GB RAM recommended

### External Dependencies
- Zerodha Kite Connect API key (for live trading)
- Multiple LLM API keys (Groq, OpenAI, Anthropic, Hugging Face) for AI features
- TA-Lib C library (for technical analysis)
- Alpha Vantage/Yahoo Finance API keys (for additional data sources)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/stocksteward-ai.git
cd stocksteward-ai
```

### 2. Install TA-Lib C Library (Critical Step!)

#### For Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install build-essential wget
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
```

#### For CentOS/RHEL/Fedora:
```bash
sudo yum install gcc gcc-c++ wget
# or for newer versions
sudo dnf install gcc gcc-c++ wget
# Then follow same steps as Ubuntu
```

#### For macOS:
```bash
brew install ta-lib
```

#### For Windows:
1. Download pre-compiled binaries from [Christoph Gohlke's site](https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib)
2. Install using pip: `pip install TA_Lib‑0.4.XX‑cpXX‑cpXX‑win_amd64.whl`

### 3. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install
```

### 5. Environment Configuration
Create `.env` files in both backend and frontend directories:

#### Backend `.env`:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/stocksteward
REDIS_URL=redis://localhost:6379
KITE_API_KEY=your_kite_api_key
KITE_ACCESS_TOKEN=your_kite_access_token
GROQ_API_KEY=your_groq_api_key
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### Frontend `.env`:
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_SOCKET_URL=http://localhost:8000
REACT_APP_GROQ_API_KEY=your_groq_api_key
```

### 6. Database Setup
```bash
# Run database migrations
cd backend
alembic upgrade head
```

### 7. Running the Application

#### Option 1: Local Development
```bash
# Terminal 1: Start backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Start frontend
cd frontend
npm start
```

#### Option 2: Docker (Recommended)
```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/auth/profile` - Get user profile (requires auth)

### Trading
- `POST /api/v1/trades/place` - Place a trade
- `GET /api/v1/trades/history` - Get trade history
- `GET /api/v1/portfolio/holdings` - Get portfolio holdings

### Backtesting
- `POST /api/v1/backtesting/run` - Run backtest
- `GET /api/v1/backtesting/strategies` - Get available strategies

### Market Data
- `GET /api/v1/market/tickers` - Get market tickers
- `GET /api/v1/market/history` - Get historical data

### Enhanced AI Endpoints
- `POST /api/v1/enhanced-ai/market-analysis` - Comprehensive market analysis with multi-LLM support
- `GET /api/v1/enhanced-ai/market-research` - Sector and market research analysis
- `POST /api/v1/enhanced-ai/chat` - Financial chat with contextual awareness
- `POST /api/v1/enhanced-ai/multi-source-analysis` - Cross-referenced analysis from multiple data sources
- `GET /api/v1/enhanced-ai/available-models` - Get available LLM models
- `GET /api/v1/enhanced-ai/available-providers` - Get available LLM providers

## Configuration

### Risk Management Settings
The platform includes comprehensive risk controls that can be configured:

```python
# In app/core/config.py
MAX_POSITION_SIZE_PERCENT = 0.10  # 10% of portfolio per position
MAX_DAILY_LOSS_PERCENT = 0.02     # 2% daily loss limit
MAX_TOTAL_EXPOSURE = 0.80         # 80% total exposure
COMMISSION_RATE = 0.001           # 0.1% commission
SLIPPAGE_RATE = 0.0005            # 0.05% slippage
```

### Strategy Parameters
Strategies can be customized with various parameters:

```python
# Example strategy configuration
strategy_params = {
    'sma_crossover': {
        'short_period': 20,
        'long_period': 50
    },
    'rsi_mean_reversion': {
        'rsi_period': 14,
        'overbought_level': 70,
        'oversold_level': 30
    }
}
```

## Troubleshooting

### Common Issues

#### 1. TA-Lib Installation Error
If you encounter errors like `ta-lib/ta_defs.h: No such file or directory`, ensure you've installed the TA-Lib C library before installing the Python package.

#### 2. Database Connection Issues
- Verify PostgreSQL is running
- Check DATABASE_URL in environment variables
- Ensure database migrations have been applied

#### 3. API Key Issues
- Verify broker API keys are correct and active
- Check if API key permissions include trading
- Ensure account is activated for trading

For detailed troubleshooting, see [TROUBLESHOOTING_GUIDE.md](docs/TROUBLESHOOTING_GUIDE.md).

## Development

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality
```bash
# Linting
flake8 .
black .
mypy .

# Frontend linting
npm run lint
```

## Security

### Authentication
- JWT-based authentication
- Password hashing with bcrypt
- Rate limiting on auth endpoints
- Session management

### Data Protection
- AES-256 encryption for sensitive data
- SSL/TLS for all communications
- Input validation and sanitization
- SQL injection prevention

## Performance

### Optimizations
- Redis caching for frequently accessed data
- Database indexing for common queries
- Asynchronous processing for heavy operations
- WebSocket connections for real-time updates

### Monitoring
- Application performance metrics
- Database query performance
- API response times
- Resource utilization

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue in the GitHub repository or contact the development team.

---

## About StockSteward AI

StockSteward AI is designed for serious traders who want to leverage artificial intelligence and algorithmic trading to enhance their investment strategies. The platform provides enterprise-grade tools for developing, testing, and executing automated trading strategies while maintaining strict risk controls and providing transparent, auditable trading operations.

**Note**: This is a demo platform for educational purposes. Real trading involves substantial risk and may not be suitable for all investors. Past performance is not indicative of future results.