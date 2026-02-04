# StockSteward AI - Technical Design Document (Low-Level)

## 1. System Architecture Overview

### 1.1 High-Level Architecture
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

### 1.2 Component Interaction Flow
1. User initiates trading action through frontend
2. Frontend sends request to backend API
3. Backend validates and processes request
4. Risk manager evaluates trade risk
5. Execution engine processes order
6. Order sent to broker/exchange
7. Results stored in database
8. Updates pushed to frontend via WebSocket

## 2. Backend Architecture

### 2.1 Directory Structure
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

### 2.2 Core Components

#### 2.2.1 Main Application (app/main.py)
```python
from fastapi import FastAPI
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import engine, Base
from app.core.middleware import add_custom_middleware
import uvicorn
import asyncio

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="StockSteward AI - Advanced Algorithmic Trading Platform",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
add_custom_middleware(app)

# Include API routers
app.include_router(api_router, prefix=settings.API_V1_STR)

# Initialize database tables
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "StockSteward AI Backend is operational"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### 2.2.2 Configuration Management (app/core/config.py)
```python
from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "StockSteward AI"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/dbname")
    DATABASE_POOL_SIZE: int = 20
    DATABASE_POOL_TIMEOUT: int = 30
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # API Keys
    KITE_API_KEY: str = os.getenv("KITE_API_KEY", "")
    KITE_ACCESS_TOKEN: str = os.getenv("KITE_ACCESS_TOKEN", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Risk Management
    MAX_POSITION_SIZE_PERCENT: float = 0.10  # 10% of portfolio
    MAX_DAILY_LOSS_PERCENT: float = 0.02     # 2% daily loss limit
    MAX_TOTAL_EXPOSURE: float = 0.80         # 80% total exposure
    
    # Execution
    COMMISSION_RATE: float = 0.001           # 0.1% commission
    SLIPPAGE_RATE: float = 0.0005            # 0.05% slippage
    MIN_ORDER_QUANTITY: int = 1
    MAX_ORDER_QUANTITY: int = 10000
    
    # Backtesting
    BACKTEST_COMMISSION_RATE: float = 0.0005 # Lower for backtesting
    BACKTEST_SLIPPAGE_RATE: float = 0.001    # Higher for backtesting
    DEFAULT_LOOKBACK_PERIOD: int = 252       # 1 year of trading days
    
    # ML/AI
    AI_MODEL_TEMPERATURE: float = 0.7
    AI_MAX_TOKENS: int = 1000
    AI_MODEL_NAME: str = "llama3-groq-70b-8192-tool-use-preview"
    
    # Caching
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    CACHE_TTL: int = 300  # 5 minutes
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

#### 2.2.3 Database Models (app/models/trade.py)
```python
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from app.core.database import Base
from datetime import datetime

class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=True)
    symbol = Column(String, index=True, nullable=False)
    side = Column(String(10), nullable=False)  # BUY/SELL
    quantity = Column(Integer, nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    entry_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    exit_time = Column(DateTime, nullable=True)
    pnl = Column(Float, default=0.0)
    pnl_percentage = Column(Float, default=0.0)
    status = Column(String(20), default="OPEN", nullable=False)  # OPEN/CLOSED/PENDING
    order_id = Column(String, nullable=True)  # Broker order ID
    exchange_order_id = Column(String, nullable=True)  # Exchange order ID
    commission = Column(Float, default=0.0)
    fees = Column(Float, default=0.0)
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    trailing_stop = Column(Boolean, default=False)
    decision_logic = Column(String, nullable=True)  # AI decision explanation
    
    # Relationships
    user = relationship("User", back_populates="trades")
    strategy = relationship("Strategy", back_populates="trades")
    
    def __repr__(self):
        return f"<Trade(id={self.id}, symbol='{self.symbol}', side='{self.side}', quantity={self.quantity})>"
```

## 3. API Layer Design

### 3.1 API Endpoints Structure

#### 3.1.1 Trading Endpoints (app/api/v1/endpoints/trades.py)
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app import schemas, models, crud
from app.core.database import get_db
from app.core.security import get_current_user
from app.services.trade_service import TradeService
from app.services.risk_service import RiskService

router = APIRouter()

@router.post("/", response_model=schemas.TradeResponse)
async def place_order(
    trade_request: schemas.TradeRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Place a new trade order
    """
    # Validate request
    if not trade_request.symbol or not trade_request.side or not trade_request.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Symbol, side, and quantity are required"
        )
    
    # Check risk limits
    risk_service = RiskService(db)
    risk_check = await risk_service.check_trade_risk(
        user_id=current_user.id,
        symbol=trade_request.symbol,
        quantity=trade_request.quantity,
        price=trade_request.price
    )
    
    if not risk_check.approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trade rejected: {risk_check.reason}"
        )
    
    # Execute trade
    trade_service = TradeService(db)
    try:
        trade = await trade_service.place_order(
            user_id=current_user.id,
            symbol=trade_request.symbol,
            side=trade_request.side,
            quantity=trade_request.quantity,
            price=trade_request.price,
            order_type=trade_request.order_type,
            stop_loss=trade_request.stop_loss,
            take_profit=trade_request.take_profit
        )
        return trade
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to place order: {str(e)}"
        )

@router.get("/{trade_id}", response_model=schemas.TradeResponse)
async def get_trade(
    trade_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific trade
    """
    trade = crud.get_trade(db, trade_id=trade_id)
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade not found"
        )
    
    # Check ownership
    if trade.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this trade"
        )
    
    return trade

@router.get("/", response_model=List[schemas.TradeResponse])
async def get_user_trades(
    current_user: models.User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all trades for the current user
    """
    trades = crud.get_user_trades(
        db, 
        user_id=current_user.id, 
        skip=skip, 
        limit=limit
    )
    return trades
```

#### 3.1.2 Backtesting Endpoints (app/api/v1/endpoints/backtesting.py)
```python
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from app.schemas.backtesting import BacktestRequest, BacktestResponse
from app.core.security import get_current_user
from app.services.backtesting_service import BacktestingService
from app.models.user import User

router = APIRouter()

@router.post("/run", response_model=BacktestResponse)
async def run_backtest(
    request: BacktestRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Run a backtest with the specified parameters
    """
    if request.end_date <= request.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date"
        )
    
    if request.initial_capital <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Initial capital must be positive"
        )
    
    try:
        backtest_service = BacktestingService()
        results = await backtest_service.run_backtest(
            strategy_name=request.strategy_name,
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital,
            parameters=request.parameters
        )
        
        return BacktestResponse(
            success=True,
            results=results,
            strategy_name=request.strategy_name,
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Backtest failed: {str(e)}"
        )

@router.get("/strategies", response_model=Dict[str, Any])
async def get_available_strategies():
    """
    Get list of available backtesting strategies
    """
    backtest_service = BacktestingService()
    strategies = backtest_service.get_available_strategies()
    
    return {"strategies": strategies}
```

## 4. Service Layer Design

### 4.1 Trade Service (app/services/trade_service.py)
```python
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import asyncio
import logging
from app.models.trade import Trade
from app.models.user import User
from app.models.strategy import Strategy
from app.core.config import settings
from app.services.broker_service import BrokerService
from app.utils.risk_calculations import calculate_position_risk

logger = logging.getLogger(__name__)

class TradeService:
    def __init__(self, db: Session):
        self.db = db
        self.broker_service = BrokerService()
    
    async def place_order(
        self,
        user_id: int,
        symbol: str,
        side: str,
        quantity: int,
        price: float,
        order_type: str = "MARKET",
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> Trade:
        """
        Place a trade order with the broker
        """
        try:
            # Validate inputs
            if side.upper() not in ["BUY", "SELL"]:
                raise ValueError("Side must be BUY or SELL")
            
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            
            # Place order with broker
            broker_response = await self.broker_service.place_order(
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price,
                order_type=order_type,
                stop_loss=stop_loss,
                take_profit=take_profit
            )
            
            # Create trade record
            trade = Trade(
                user_id=user_id,
                symbol=symbol,
                side=side.upper(),
                quantity=quantity,
                entry_price=price,
                status="OPEN" if broker_response.get("status") == "SUCCESS" else "FAILED",
                order_id=broker_response.get("order_id"),
                exchange_order_id=broker_response.get("exchange_order_id"),
                commission=broker_response.get("commission", 0),
                fees=broker_response.get("fees", 0),
                stop_loss=stop_loss,
                take_profit=take_profit
            )
            
            self.db.add(trade)
            self.db.commit()
            self.db.refresh(trade)
            
            logger.info(f"Trade placed successfully: {trade.id} for {symbol}")
            
            return trade
            
        except Exception as e:
            logger.error(f"Error placing order: {str(e)}")
            raise
    
    async def close_position(
        self,
        trade_id: int,
        exit_price: float,
        user_id: int
    ) -> Trade:
        """
        Close an open position
        """
        trade = self.db.query(Trade).filter(Trade.id == trade_id).first()
        
        if not trade:
            raise ValueError("Trade not found")
        
        if trade.user_id != user_id:
            raise PermissionError("Not authorized to close this trade")
        
        if trade.status != "OPEN":
            raise ValueError("Trade is not open")
        
        # Calculate PnL
        if trade.side == "BUY":
            pnl = (exit_price - trade.entry_price) * trade.quantity
        else:  # SELL
            pnl = (trade.entry_price - exit_price) * trade.quantity
        
        pnl_percentage = (pnl / (trade.entry_price * trade.quantity)) * 100
        
        # Update trade
        trade.exit_price = exit_price
        trade.exit_time = datetime.utcnow()
        trade.pnl = pnl
        trade.pnl_percentage = pnl_percentage
        trade.status = "CLOSED"
        
        self.db.commit()
        self.db.refresh(trade)
        
        return trade
    
    async def get_user_portfolio_value(self, user_id: int) -> float:
        """
        Calculate total portfolio value for a user
        """
        trades = self.db.query(Trade).filter(Trade.user_id == user_id).all()
        
        open_trades = [t for t in trades if t.status == "OPEN"]
        
        total_value = 0
        
        for trade in open_trades:
            # Get current market price
            current_price = await self.broker_service.get_current_price(trade.symbol)
            
            if trade.side == "BUY":
                unrealized_pnl = (current_price - trade.entry_price) * trade.quantity
            else:  # SELL
                unrealized_pnl = (trade.entry_price - current_price) * trade.quantity
            
            total_value += (trade.entry_price * trade.quantity) + unrealized_pnl
        
        return total_value
```

### 4.2 Backtesting Service (app/services/backtesting_service.py)
```python
from typing import Dict, Any, List
from datetime import datetime
import pandas as pd
import numpy as np
from app.backtesting.engine import BacktestingEngine
from app.strategies.advanced_strategies import AdvancedStrategies
from app.utils.technical_analysis import TechnicalAnalysis

class BacktestingService:
    def __init__(self):
        self.engine = BacktestingEngine()
        self.ta = TechnicalAnalysis()
        self.strategies = AdvancedStrategies()
    
    async def run_backtest(
        self,
        strategy_name: str,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        initial_capital: float = 100000.0,
        parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Run a backtest with the specified strategy
        """
        # Load historical data
        data = await self.engine.load_historical_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date
        )
        
        # Calculate technical indicators
        data = self.ta.calculate_all_indicators(data)
        
        # Select strategy function
        strategy_func = self._get_strategy_function(strategy_name)
        
        # Run backtest
        results = await self.engine.run_backtest(
            strategy_func=strategy_func,
            data=data,
            initial_capital=initial_capital,
            parameters=parameters or {}
        )
        
        return results
    
    def _get_strategy_function(self, strategy_name: str):
        """
        Get the strategy function by name
        """
        strategy_map = {
            "sma_crossover": self.strategies.sma_crossover_strategy,
            "rsi_mean_reversion": self.strategies.rsi_mean_reversion_strategy,
            "macd_crossover": self.strategies.macd_crossover_strategy,
            "bollinger_bands": self.strategies.bollinger_bands_strategy,
            "mean_reversion": self.strategies.mean_reversion_strategy,
            "momentum": self.strategies.momentum_strategy,
            "breakout": self.strategies.breakout_strategy
        }
        
        if strategy_name not in strategy_map:
            raise ValueError(f"Unknown strategy: {strategy_name}")
        
        return strategy_map[strategy_name]
    
    def get_available_strategies(self) -> List[Dict[str, Any]]:
        """
        Get list of available strategies with metadata
        """
        return [
            {
                "name": "sma_crossover",
                "description": "Simple Moving Average crossover strategy",
                "type": "trend_following",
                "parameters": ["short_period", "long_period"],
                "complexity": "beginner"
            },
            {
                "name": "rsi_mean_reversion",
                "description": "RSI-based mean reversion strategy",
                "type": "mean_reversion",
                "parameters": ["rsi_period", "overbought_level", "oversold_level"],
                "complexity": "intermediate"
            },
            {
                "name": "macd_crossover",
                "description": "MACD line and signal line crossover strategy",
                "type": "momentum",
                "parameters": ["fast_period", "slow_period", "signal_period"],
                "complexity": "intermediate"
            },
            {
                "name": "bollinger_bands",
                "description": "Bollinger Bands mean reversion strategy",
                "type": "mean_reversion",
                "parameters": ["period", "std_dev"],
                "complexity": "intermediate"
            },
            {
                "name": "mean_reversion",
                "description": "General mean reversion strategy using multiple indicators",
                "type": "mean_reversion",
                "parameters": ["lookback_period", "z_score_threshold"],
                "complexity": "advanced"
            },
            {
                "name": "momentum",
                "description": "Momentum-based strategy using price acceleration",
                "type": "momentum",
                "parameters": ["momentum_period", "acceleration_threshold"],
                "complexity": "advanced"
            },
            {
                "name": "breakout",
                "description": "Breakout strategy using support/resistance levels",
                "type": "breakout",
                "parameters": ["lookback_period", "breakout_threshold"],
                "complexity": "advanced"
            }
        ]
```

## 5. Backtesting Engine Design

### 5.1 Core Backtesting Engine (app/backtesting/engine.py)
```python
from typing import Dict, Any, Callable, List
from datetime import datetime
import pandas as pd
import numpy as np
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)

class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"

class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"

@dataclass
class Order:
    symbol: str
    side: OrderSide
    quantity: int
    price: float
    timestamp: datetime
    order_type: OrderType = OrderType.MARKET
    filled: bool = False
    filled_price: float = None
    filled_time: datetime = None

@dataclass
class Position:
    symbol: str
    quantity: int
    avg_price: float
    entry_time: datetime
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0

@dataclass
class Trade:
    symbol: str
    side: str
    quantity: int
    entry_price: float
    exit_price: float
    entry_time: datetime
    exit_time: datetime
    pnl: float
    pnl_pct: float

class BacktestingEngine:
    def __init__(
        self,
        commission_rate: float = 0.0005,
        slippage_rate: float = 0.001,
        initial_capital: float = 100000.0
    ):
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, Position] = {}
        self.orders: List[Order] = []
        self.trades: List[Trade] = []
        self.portfolio_history: List[Dict] = []
        self.metrics: Dict[str, float] = {}
    
    async def load_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> pd.DataFrame:
        """
        Load historical market data for backtesting
        """
        # In production, this would fetch from a database or API
        # For demo, we'll generate synthetic data
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Generate realistic OHLCV data
        np.random.seed(42)  # For reproducible results
        returns = np.random.normal(0.0005, 0.02, len(dates))
        prices = [100]  # Starting price
        
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
        
        data = pd.DataFrame({
            'date': dates,
            'open': [p * (1 - abs(np.random.normal(0, 0.005))) for p in prices],
            'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            'close': prices,
            'volume': np.random.randint(1000000, 5000000, len(dates))
        })
        
        return data
    
    async def run_backtest(
        self,
        strategy_func: Callable,
        data: pd.DataFrame,
        initial_capital: float = 100000.0,
        parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Run the backtest with the given strategy
        """
        # Reset state
        self.cash = initial_capital
        self.positions = {}
        self.orders = []
        self.trades = []
        self.portfolio_history = []
        self.metrics = {}
        
        # Run strategy for each bar
        for idx, row in data.iterrows():
            current_time = row['date']
            
            # Update portfolio value
            portfolio_value = self._calculate_portfolio_value(row['close'])
            
            # Store portfolio state
            self.portfolio_history.append({
                'timestamp': current_time,
                'cash': self.cash,
                'portfolio_value': portfolio_value,
                'total_value': self.cash + portfolio_value
            })
            
            # Generate signals and execute strategy
            signal = strategy_func(row, self.positions, self.cash, parameters or {})
            
            if signal:
                order = Order(
                    symbol=signal['symbol'],
                    side=OrderSide(signal['side']),
                    quantity=signal['quantity'],
                    price=row['close'],
                    timestamp=current_time,
                    order_type=OrderType(signal.get('order_type', 'MARKET'))
                )
                
                self._execute_order(order, row['close'])
        
        # Calculate final metrics
        self._calculate_metrics()
        
        return {
            'initial_capital': initial_capital,
            'final_value': self._calculate_portfolio_value(data.iloc[-1]['close']),
            'total_return': self.metrics.get('total_return', 0),
            'annualized_return': self.metrics.get('annualized_return', 0),
            'volatility': self.metrics.get('volatility', 0),
            'sharpe_ratio': self.metrics.get('sharpe_ratio', 0),
            'max_drawdown': self.metrics.get('max_drawdown', 0),
            'win_rate': self.metrics.get('win_rate', 0),
            'profit_factor': self.metrics.get('profit_factor', 0),
            'total_trades': len(self.trades),
            'trades': [
                {
                    'symbol': t.symbol,
                    'side': t.side,
                    'quantity': t.quantity,
                    'entry_price': t.entry_price,
                    'exit_price': t.exit_price,
                    'entry_time': t.entry_time,
                    'exit_time': t.exit_time,
                    'pnl': t.pnl,
                    'pnl_pct': t.pnl_pct
                } for t in self.trades
            ],
            'portfolio_history': self.portfolio_history,
            'metrics': self.metrics
        }
    
    def _execute_order(self, order: Order, current_price: float):
        """
        Execute an order in the backtesting environment
        """
        # Apply slippage
        if order.side == OrderSide.BUY:
            execution_price = current_price * (1 + self.slippage_rate)
        else:
            execution_price = current_price * (1 - self.slippage_rate)
        
        # Calculate commission
        commission = order.quantity * execution_price * self.commission_rate
        
        if order.side == OrderSide.BUY:
            # Check if we have enough cash
            required_cash = order.quantity * execution_price + commission
            if self.cash >= required_cash:
                # Execute buy
                self.cash -= required_cash
                
                if order.symbol in self.positions:
                    # Average down
                    pos = self.positions[order.symbol]
                    total_qty = pos.quantity + order.quantity
                    total_cost = (pos.quantity * pos.avg_price) + (order.quantity * execution_price)
                    pos.avg_price = total_cost / total_qty
                    pos.quantity = total_qty
                else:
                    # New position
                    self.positions[order.symbol] = Position(
                        symbol=order.symbol,
                        quantity=order.quantity,
                        avg_price=execution_price,
                        entry_time=order.timestamp
                    )
        else:  # SELL
            # Check if we have the position
            if order.symbol in self.positions and self.positions[order.symbol].quantity >= order.quantity:
                pos = self.positions[order.symbol]
                
                # Calculate PnL
                pnl = (execution_price - pos.avg_price) * order.quantity
                pnl_pct = (pnl / (pos.avg_price * order.quantity)) * 100
                
                # Execute sell
                proceeds = order.quantity * execution_price - commission
                self.cash += proceeds
                
                # Update position
                pos.quantity -= order.quantity
                pos.realized_pnl += pnl
                
                # Record trade
                trade = Trade(
                    symbol=order.symbol,
                    side='SELL',
                    quantity=order.quantity,
                    entry_price=pos.avg_price,
                    exit_price=execution_price,
                    entry_time=pos.entry_time,
                    exit_time=order.timestamp,
                    pnl=pnl,
                    pnl_pct=pnl_pct
                )
                self.trades.append(trade)
                
                # Remove position if fully closed
                if pos.quantity == 0:
                    del self.positions[order.symbol]
        
        # Mark order as filled
        order.filled = True
        order.filled_price = execution_price
        order.filled_time = order.timestamp
    
    def _calculate_portfolio_value(self, current_price: float) -> float:
        """
        Calculate total portfolio value from positions
        """
        total_value = 0
        for pos in self.positions.values():
            total_value += pos.quantity * current_price
        return total_value
    
    def _calculate_metrics(self):
        """
        Calculate performance metrics
        """
        if not self.portfolio_history:
            return
        
        # Extract portfolio values
        values = [ph['total_value'] for ph in self.portfolio_history]
        returns = np.diff(values) / values[:-1]
        
        if len(returns) == 0:
            return
        
        # Total return
        self.metrics['total_return'] = (values[-1] - values[0]) / values[0]
        
        # Annualized return
        years = (self.portfolio_history[-1]['timestamp'] - self.portfolio_history[0]['timestamp']).days / 365.25
        if years > 0:
            self.metrics['annualized_return'] = (values[-1] / values[0]) ** (1 / years) - 1
        
        # Volatility
        if len(returns) > 1:
            self.metrics['volatility'] = np.std(returns) * np.sqrt(252)  # Annualized
        
        # Sharpe ratio (assuming 2% risk-free rate)
        risk_free_rate = 0.02 / 252
        if self.metrics['volatility'] > 0:
            self.metrics['sharpe_ratio'] = (np.mean(returns) - risk_free_rate) / (self.metrics['volatility'] / np.sqrt(252))
        
        # Max drawdown
        peak = values[0]
        max_dd = 0
        for value in values:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            if dd > max_dd:
                max_dd = dd
        self.metrics['max_drawdown'] = max_dd
        
        # Win rate and profit factor
        if self.trades:
            winning_trades = [t for t in self.trades if t.pnl > 0]
            losing_trades = [t for t in self.trades if t.pnl <= 0]
            
            if len(self.trades) > 0:
                self.metrics['win_rate'] = len(winning_trades) / len(self.trades)
            
            total_wins = sum(t.pnl for t in winning_trades)
            total_losses = abs(sum(t.pnl for t in losing_trades))
            
            if total_losses > 0:
                self.metrics['profit_factor'] = total_wins / total_losses
```

## 6. Risk Management System

### 6.1 Risk Manager (app/risk/manager.py)
```python
from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session
import numpy as np
from app.models.user import User
from app.models.portfolio import Portfolio
from app.models.trade import Trade

class RiskManager:
    def __init__(self, db: Session):
        self.db = db
    
    async def check_trade_risk(
        self,
        user_id: int,
        symbol: str,
        quantity: int,
        price: float
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Check if a trade passes risk controls
        """
        # Get user portfolio
        portfolio = self.db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
        if not portfolio:
            return False, "No portfolio found", {}
        
        # Calculate trade value
        trade_value = quantity * price
        
        # Check position size limits
        max_position_size = portfolio.total_value * 0.10  # 10% of portfolio
        if trade_value > max_position_size:
            return False, f"Position size exceeds limit of {max_position_size:.2f}", {
                'max_position_size': max_position_size,
                'requested_size': trade_value
            }
        
        # Check total exposure limits
        current_positions = self.db.query(Trade).filter(
            Trade.user_id == user_id,
            Trade.status == "OPEN"
        ).all()
        
        total_exposure = sum(
            (p.quantity * p.entry_price) for p in current_positions
        ) + trade_value
        
        max_total_exposure = portfolio.total_value * 0.80  # 80% of portfolio
        if total_exposure > max_total_exposure:
            return False, f"Total exposure exceeds limit of {max_total_exposure:.2f}", {
                'max_exposure': max_total_exposure,
                'current_exposure': total_exposure
            }
        
        # Check concentration risk
        same_symbol_positions = [p for p in current_positions if p.symbol == symbol]
        existing_value = sum((p.quantity * p.entry_price) for p in same_symbol_positions)
        total_concentration = existing_value + trade_value
        
        max_concentration = portfolio.total_value * 0.15  # 15% for single symbol
        if total_concentration > max_concentration:
            return False, f"Concentration in {symbol} exceeds limit of {max_concentration:.2f}", {
                'max_concentration': max_concentration,
                'current_concentration': total_concentration
            }
        
        # All checks passed
        return True, "Trade approved", {
            'position_size': trade_value,
            'total_exposure': total_exposure,
            'concentration': total_concentration
        }
    
    def calculate_portfolio_risk_metrics(self, user_id: int) -> Dict[str, float]:
        """
        Calculate overall portfolio risk metrics
        """
        trades = self.db.query(Trade).filter(
            Trade.user_id == user_id,
            Trade.status == "OPEN"
        ).all()
        
        if not trades:
            return {
                'var_95': 0.0,
                'var_99': 0.0,
                'volatility': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0
            }
        
        # Calculate portfolio value
        portfolio_value = sum((t.quantity * t.entry_price) for t in trades)
        
        # Calculate individual position risks
        position_values = [(t.quantity * t.entry_price) for t in trades]
        weights = [pv / portfolio_value for pv in position_values]
        
        # Simplified risk calculations (in reality would use historical correlations)
        # For demo purposes, using equal weighting
        avg_volatility = 0.18  # 18% average stock volatility
        portfolio_volatility = avg_volatility * np.sqrt(sum(w**2 for w in weights))  # Simplified
        
        # VaR calculations (simplified)
        var_95 = portfolio_volatility * 1.645  # 95% VaR assuming normal distribution
        var_99 = portfolio_volatility * 2.33   # 99% VaR
        
        return {
            'var_95': var_95,
            'var_99': var_99,
            'volatility': portfolio_volatility,
            'sharpe_ratio': 0.0,  # Would need historical returns
            'max_drawdown': 0.0   # Would need historical portfolio values
        }
```

## 7. Frontend Architecture

### 7.1 Directory Structure
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

### 7.2 Main Application Component (frontend/src/App.jsx)
```jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import { UserProvider } from './context/UserContext';
import { AppDataProvider } from './context/AppDataContext';
import { SocketProvider } from './context/SocketContext';

// Layout Components
import { Layout } from './components/layout/Layout';

// Page Components
import { Dashboard } from './pages/Dashboard';
import { TradingHub } from './pages/TradingHub';
import { Portfolio } from './pages/Portfolio';
import { Backtesting } from './pages/Backtesting';
import { Reports } from './pages/Reports';
import { Login } from './pages/Login';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('access_token');
  return token ? children : <Navigate to="/login" />;
};

function App() {
  return (
    <ThemeProvider>
      <UserProvider>
        <AppDataProvider>
          <SocketProvider>
            <Router>
              <div className="App">
                <Routes>
                  <Route path="/login" element={<Login />} />
                  
                  <Route 
                    path="/" 
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <Dashboard />
                        </Layout>
                      </ProtectedRoute>
                    } 
                  />
                  
                  <Route 
                    path="/trading" 
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <TradingHub />
                        </Layout>
                      </ProtectedRoute>
                    } 
                  />
                  
                  <Route 
                    path="/portfolio" 
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <Portfolio />
                        </Layout>
                      </ProtectedRoute>
                    } 
                  />
                  
                  <Route 
                    path="/backtesting" 
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <Backtesting />
                        </Layout>
                      </ProtectedRoute>
                    } 
                  />
                  
                  <Route 
                    path="/reports" 
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <Reports />
                        </Layout>
                      </ProtectedRoute>
                    } 
                  />
                </Routes>
              </div>
            </Router>
          </SocketProvider>
        </AppDataProvider>
      </UserProvider>
    </ThemeProvider>
  );
}

export default App;
```

### 7.3 Trading Hub Component (frontend/src/pages/TradingHub.jsx)
```jsx
import React, { useState, useEffect, useCallback } from 'react';
import { Card } from '../components/ui/Card';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Target, 
  Zap, 
  Play, 
  Pause, 
  RotateCcw 
} from 'lucide-react';
import { 
  fetchStrategies, 
  fetchUser, 
  updateUser, 
  fetchPortfolioSummary, 
  executeTrade,
  launchStrategy
} from '../services/api';

const TradingHub = () => {
  const [user, setUser] = useState(null);
  const [strategies, setStrategies] = useState([]);
  const [activeStrategies, setActiveStrategies] = useState([]);
  const [orderTicker, setOrderTicker] = useState('');
  const [orderQty, setOrderQty] = useState(1);
  const [orderType, setOrderType] = useState('MARKET');
  const [orderPrice, setOrderPrice] = useState(0);
  const [tradingMode, setTradingMode] = useState('MANUAL'); // MANUAL or AUTO
  const [executing, setExecuting] = useState(false);
  const [tradeStatus, setTradeStatus] = useState(null);
  const [basket, setBasket] = useState([]);
  const [showBasketModal, setShowBasketModal] = useState(false);

  // Load initial data
  useEffect(() => {
    const loadData = async () => {
      try {
        const userData = await fetchUser();
        setUser(userData);
        
        const stratData = await fetchStrategies();
        setStrategies(stratData);
      } catch (error) {
        console.error('Error loading trading data:', error);
      }
    };
    
    loadData();
  }, []);

  // Place manual trade
  const handleManualTrade = async (side) => {
    if (!orderTicker || orderQty <= 0) {
      setTradeStatus({ type: 'error', message: 'Please select a ticker and quantity' });
      return;
    }

    setExecuting(true);
    try {
      const tradeData = {
        symbol: orderTicker,
        side: side,
        quantity: orderQty,
        price: orderType === 'MARKET' ? null : orderPrice,
        order_type: orderType,
        user_id: user.id
      };

      const result = await executeTrade(tradeData);
      
      if (result.success) {
        setTradeStatus({ 
          type: 'success', 
          message: `${side} order placed successfully for ${orderQty} shares of ${orderTicker}` 
        });
        
        // Clear form
        setOrderQty(1);
        setOrderPrice(0);
      } else {
        setTradeStatus({ 
          type: 'error', 
          message: result.error || 'Trade execution failed' 
        });
      }
    } catch (error) {
      setTradeStatus({ 
        type: 'error', 
        message: error.message || 'An error occurred during trade execution' 
      });
    } finally {
      setExecuting(false);
    }
  };

  // Add to basket
  const addToBasket = () => {
    if (!orderTicker || orderQty <= 0) {
      setTradeStatus({ type: 'error', message: 'Invalid order details' });
      return;
    }

    const newOrder = {
      id: Date.now(),
      symbol: orderTicker,
      side: 'BUY', // Default to buy, user can change
      quantity: orderQty,
      price: orderPrice,
      type: orderType
    };

    setBasket(prev => [...prev, newOrder]);
    setTradeStatus({ type: 'success', message: 'Added to basket' });
  };

  // Execute basket
  const executeBasket = async () => {
    if (basket.length === 0) return;

    setExecuting(true);
    try {
      for (const order of basket) {
        await executeTrade({
          symbol: order.symbol,
          side: order.side,
          quantity: order.quantity,
          price: order.price,
          order_type: order.type,
          user_id: user.id
        });
      }
      
      setTradeStatus({ 
        type: 'success', 
        message: `Executed ${basket.length} orders from basket` 
      });
      
      setBasket([]);
      setShowBasketModal(false);
    } catch (error) {
      setTradeStatus({ 
        type: 'error', 
        message: 'Basket execution failed: ' + error.message 
      });
    } finally {
      setExecuting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-black text-slate-900">Trading Hub</h1>
          <p className="text-slate-500 mt-1">Advanced algorithmic trading interface</p>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 bg-slate-100 p-1 rounded-xl">
            <button
              onClick={() => setTradingMode('MANUAL')}
              className={`px-4 py-2 rounded-lg text-sm font-black uppercase tracking-widest ${
                tradingMode === 'MANUAL' 
                  ? 'bg-white text-primary shadow-sm' 
                  : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              Manual
            </button>
            <button
              onClick={() => setTradingMode('AUTO')}
              className={`px-4 py-2 rounded-lg text-sm font-black uppercase tracking-widest ${
                tradingMode === 'AUTO' 
                  ? 'bg-white text-primary shadow-sm' 
                  : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              Auto
            </button>
          </div>
          
          <button className="bg-primary text-white px-6 py-3 rounded-xl font-black text-sm uppercase tracking-widest hover:opacity-90 transition-opacity">
            <Zap size={18} className="inline mr-2" />
            Launch Strategy
          </button>
        </div>
      </div>

      {/* Manual Trading Panel */}
      <Card className="p-6 border-slate-200">
        <div className="flex flex-col lg:flex-row gap-8">
          <div className="flex-1">
            <h3 className="text-lg font-black text-slate-900 mb-4">Manual Order Ticket</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-black text-slate-700 mb-2">Symbol</label>
                <input
                  type="text"
                  value={orderTicker}
                  onChange={(e) => setOrderTicker(e.target.value.toUpperCase())}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm font-black text-slate-900 focus:ring-2 focus:ring-primary/20 transition-all outline-none"
                  placeholder="Enter symbol (e.g., RELIANCE)"
                />
              </div>
              
              <div>
                <label className="block text-sm font-black text-slate-700 mb-2">Quantity</label>
                <input
                  type="number"
                  value={orderQty}
                  onChange={(e) => setOrderQty(parseInt(e.target.value) || 0)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm font-black text-slate-900 focus:ring-2 focus:ring-primary/20 transition-all outline-none"
                  placeholder="Enter quantity"
                />
              </div>
              
              <div>
                <label className="block text-sm font-black text-slate-700 mb-2">Order Type</label>
                <select
                  value={orderType}
                  onChange={(e) => setOrderType(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm font-black text-slate-900 focus:ring-2 focus:ring-primary/20 transition-all outline-none"
                >
                  <option value="MARKET">Market</option>
                  <option value="LIMIT">Limit</option>
                  <option value="STOP">Stop</option>
                  <option value="STOP_LIMIT">Stop Limit</option>
                </select>
              </div>
              
              {orderType !== 'MARKET' && (
                <div>
                  <label className="block text-sm font-black text-slate-700 mb-2">Price</label>
                  <input
                    type="number"
                    value={orderPrice}
                    onChange={(e) => setOrderPrice(parseFloat(e.target.value) || 0)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm font-black text-slate-900 focus:ring-2 focus:ring-primary/20 transition-all outline-none"
                    placeholder="Enter price"
                  />
                </div>
              )}
            </div>
            
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => handleManualTrade('BUY')}
                disabled={executing}
                className="flex-1 bg-green-600 text-white px-6 py-3.5 rounded-xl font-black text-sm uppercase tracking-widest hover:bg-green-700 transition-all shadow-lg shadow-green-600/20 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {executing ? <RotateCcw className="animate-spin" size={18} /> : <TrendingUp size={18} />}
                Buy
              </button>
              
              <button
                onClick={() => handleManualTrade('SELL')}
                disabled={executing}
                className="flex-1 bg-red-600 text-white px-6 py-3.5 rounded-xl font-black text-sm uppercase tracking-widest hover:bg-red-700 transition-all shadow-lg shadow-red-600/20 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {executing ? <RotateCcw className="animate-spin" size={18} /> : <TrendingDown size={18} />}
                Sell
              </button>
              
              <button
                onClick={addToBasket}
                className="px-6 py-3.5 rounded-xl font-black text-sm uppercase tracking-widest bg-slate-900 text-white hover:bg-slate-800 transition-all"
              >
                Add to Basket
              </button>
            </div>
            
            {tradeStatus && (
              <div className={`mt-4 p-3 rounded-xl border text-sm font-black uppercase tracking-widest ${
                tradeStatus.type === 'success' 
                  ? 'bg-green-50 border-green-100 text-green-700' 
                  : 'bg-red-50 border-red-100 text-red-700'
              }`}>
                {tradeStatus.message}
              </div>
            )}
          </div>
          
          <div className="lg:w-80">
            <h3 className="text-lg font-black text-slate-900 mb-4">Quick Actions</h3>
            
            <div className="space-y-3">
              <button
                onClick={() => setShowBasketModal(true)}
                className="w-full p-4 bg-slate-50 border border-slate-200 rounded-xl text-left hover:bg-slate-100 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <span className="font-black text-slate-900">Order Basket</span>
                  <span className="text-xs font-black bg-primary text-white px-2 py-1 rounded-full">
                    {basket.length}
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-1">Batch execute multiple orders</p>
              </button>
              
              <button className="w-full p-4 bg-slate-50 border border-slate-200 rounded-xl text-left hover:bg-slate-100 transition-colors">
                <div className="flex items-center gap-2">
                  <Activity size={16} className="text-primary" />
                  <span className="font-black text-slate-900">Live Market Feed</span>
                </div>
                <p className="text-xs text-slate-500 mt-1">Real-time market data</p>
              </button>
              
              <button className="w-full p-4 bg-slate-50 border border-slate-200 rounded-xl text-left hover:bg-slate-100 transition-colors">
                <div className="flex items-center gap-2">
                  <Target size={16} className="text-primary" />
                  <span className="font-black text-slate-900">Risk Controls</span>
                </div>
                <p className="text-xs text-slate-500 mt-1">Portfolio risk management</p>
              </button>
            </div>
          </div>
        </div>
      </Card>

      {/* Active Strategies */}
      <Card className="p-6 border-slate-200">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-black text-slate-900">Active Strategies</h3>
          <span className="text-sm font-black bg-primary/10 text-primary px-3 py-1 rounded-full">
            {activeStrategies.length} running
          </span>
        </div>
        
        {activeStrategies.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {activeStrategies.map((strategy) => (
              <div key={strategy.id} className="p-4 border border-slate-200 rounded-xl bg-white">
                <div className="flex justify-between items-start mb-3">
                  <h4 className="font-black text-slate-900">{strategy.name}</h4>
                  <span className={`px-2 py-1 rounded-full text-xs font-black uppercase ${
                    strategy.status === 'RUNNING' 
                      ? 'bg-green-100 text-green-700' 
                      : 'bg-amber-100 text-amber-700'
                  }`}>
                    {strategy.status}
                  </span>
                </div>
                
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Symbol:</span>
                    <span className="font-black">{strategy.symbol}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">PnL:</span>
                    <span className={`font-black ${strategy.pnl >= 0 ? 'text-green-600' : 'text-red-500'}`}>
                      {strategy.pnl >= 0 ? '+' : ''}{strategy.pnl.toFixed(2)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Trades:</span>
                    <span className="font-black">{strategy.total_trades}</span>
                  </div>
                </div>
                
                <div className="mt-4 flex gap-2">
                  <button className="flex-1 py-2 bg-slate-100 text-slate-700 rounded-lg text-xs font-black uppercase tracking-widest hover:bg-slate-200 transition-colors">
                    Pause
                  </button>
                  <button className="flex-1 py-2 bg-primary text-white rounded-lg text-xs font-black uppercase tracking-widest hover:opacity-90 transition-opacity">
                    Stats
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <Activity size={48} className="mx-auto text-slate-300 mb-4" />
            <h4 className="font-black text-slate-500 mb-2">No Active Strategies</h4>
            <p className="text-sm text-slate-400">Launch a strategy to begin automated trading</p>
          </div>
        )}
      </Card>

      {/* Order Basket Modal */}
      {showBasketModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-md">
          <div className="bg-white rounded-3xl p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-black text-slate-900">Order Basket</h3>
              <button 
                onClick={() => setShowBasketModal(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X size={24} />
              </button>
            </div>
            
            {basket.length > 0 ? (
              <>
                <div className="space-y-3 mb-6">
                  {basket.map((order, index) => (
                    <div key={order.id} className="flex items-center justify-between p-4 border border-slate-200 rounded-xl">
                      <div>
                        <span className="font-black text-slate-900">{order.symbol}</span>
                        <span className="text-sm text-slate-500 ml-2">{order.side}</span>
                      </div>
                      <div className="flex items-center gap-4">
                        <span className="font-black">{order.quantity} @ ? {order.price}</span>
                        <button 
                          onClick={() => setBasket(prev => prev.filter((_, i) => i !== index))}
                          className="text-red-500 hover:text-red-700"
                        >
                          <X size={16} />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
                
                <div className="flex justify-end gap-3">
                  <button
                    onClick={() => setShowBasketModal(false)}
                    className="px-6 py-3 border border-slate-200 text-slate-700 rounded-xl font-black text-sm uppercase tracking-widest hover:bg-slate-50 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={executeBasket}
                    disabled={executing}
                    className="px-6 py-3 bg-primary text-white rounded-xl font-black text-sm uppercase tracking-widest hover:opacity-90 transition-opacity disabled:opacity-50 flex items-center gap-2"
                  >
                    {executing ? <RotateCcw className="animate-spin" size={16} /> : <Zap size={16} />}
                    Execute Basket
                  </button>
                </div>
              </>
            ) : (
              <div className="text-center py-8">
                <ShoppingBag size={48} className="mx-auto text-slate-300 mb-4" />
                <h4 className="font-black text-slate-500 mb-2">Basket is Empty</h4>
                <p className="text-sm text-slate-400">Add orders to your basket to execute them together</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default TradingHub;
```

## 8. Database Schema Design

### 8.1 Entity Relationship Diagram (Conceptual)
```
Users (1) ----< Portfolios
Users (1) ----< Trades
Users (1) ----< Strategies
Strategies (1) ----< Trades
Portfolios (1) ----< Positions
Positions (*) ----< Trades
```

### 8.2 Database Models

#### 8.2.1 User Model (app/models/user.py)
```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    risk_tolerance = Column(String(20), default="MODERATE")  # LOW, MODERATE, HIGH
    trading_mode = Column(String(20), default="MANUAL")     # MANUAL, AUTO
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    portfolios = relationship("Portfolio", back_populates="user")
    trades = relationship("Trade", back_populates="user")
    strategies = relationship("Strategy", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', full_name='{self.full_name}')>"
```

#### 8.2.2 Strategy Model (app/models/strategy.py)
```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Strategy(Base):
    __tablename__ = "strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    strategy_type = Column(String, nullable=False)  # SMA_CROSSOVER, RSI_MEAN_REVERSION, etc.
    parameters = Column(String, nullable=True)      # JSON string of parameters
    status = Column(String(20), default="INACTIVE") # INACTIVE, ACTIVE, PAUSED
    initial_capital = Column(Float, nullable=False)
    current_capital = Column(Float, default=0.0)
    total_pnl = Column(Float, default=0.0)
    total_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="strategies")
    trades = relationship("Trade", back_populates="strategy")
    
    def __repr__(self):
        return f"<Strategy(id={self.id}, name='{self.name}', symbol='{self.symbol}')>"
```

## 9. Security & Compliance

### 9.1 Authentication Flow
1. User credentials validated against database
2. JWT token generated with user claims
3. Token stored in HTTP-only cookie or localStorage
4. All subsequent requests include Authorization header
5. Token validated on each protected endpoint

### 9.2 Authorization Model
- Role-based access control (RBAC)
- User roles: TRADER, ADMIN, AUDITOR, SUPERADMIN
- Permission matrix for different operations
- API rate limiting per user/IP
- Session management and timeout

### 9.3 Data Protection
- AES-256 encryption for sensitive data
- SSL/TLS for all communications
- Input validation and sanitization
- SQL injection prevention
- XSS protection

## 10. Performance & Scalability

### 10.1 Caching Strategy
- Redis for session management
- API response caching
- Market data caching with TTL
- Database query result caching

### 10.2 Database Optimization
- Connection pooling
- Query optimization
- Indexing strategy
- Partitioning for historical data

### 10.3 Load Balancing
- Multiple backend instances
- Session affinity
- Health checks
- Auto-scaling based on load

## 11. Monitoring & Observability

### 11.1 Logging
- Structured logging with correlation IDs
- Different log levels for different environments
- Centralized log aggregation
- Log retention policies

### 11.2 Metrics
- Application performance metrics
- Business metrics (trades, users, revenue)
- System resource metrics
- Custom business KPIs

### 11.3 Alerting
- Real-time alerting for critical issues
- Threshold-based alerts
- Escalation policies
- Integration with monitoring tools

This technical design document provides a comprehensive overview of the StockSteward AI platform architecture, covering all major components, their interactions, and implementation details.