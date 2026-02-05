# StockSteward AI - Technical Design Document (Low-Level)

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Backend Design](#backend-design)
3. [Frontend Design](#frontend-design)
4. [Database Schema](#database-schema)
5. [API Design](#api-design)
6. [Security Architecture](#security-architecture)
7. [Performance & Scalability](#performance--scalability)
8. [Monitoring & Logging](#monitoring--logging)

## 1. System Architecture

### 1.1 High-Level Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │◄──►│   Backend API    │◄──►│  External APIs  │
│   (React)       │    │   (FastAPI)      │    │ (Kite, etc.)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │   Message Queue   │
                    │   (Socket.IO)     │
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

### 1.2 Component Architecture
- **Frontend**: React 18 with TypeScript, Tailwind CSS, Socket.io client
- **Backend**: FastAPI with Python 3.11, SQLAlchemy ORM, PostgreSQL
- **ML/AI**: TensorFlow/PyTorch, scikit-learn, TA-Lib for technical analysis
- **Database**: PostgreSQL for relational data, Redis for caching
- **Messaging**: Socket.IO for real-time updates
- **Infrastructure**: Docker, Kubernetes (optional), AWS/GCP

## 2. Backend Design

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

settings = Settings()
```

### 2.3 Database Models

#### 2.3.1 User Model (app/models/user.py)
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

#### 2.3.2 Trade Model (app/models/trade.py)
```python
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
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

### 2.4 API Endpoints

#### 2.4.1 Trading Endpoints (app/api/v1/endpoints/trades.py)
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

### 2.5 Service Layer

#### 2.5.1 Trade Service (app/services/trade_service.py)
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

### 2.6 Backtesting Engine

#### 2.6.1 Core Backtesting Engine (app/backtesting/engine.py)
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
        prices = [100]
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
        
        # Calculate technical indicators
        data['sma_20'] = data['close'].rolling(window=20).mean()
        data['sma_50'] = data['close'].rolling(window=50).mean()
        data['rsi'] = self._calculate_rsi(data['close'])
        data['macd'], data['macd_signal'], data['macd_hist'] = self._calculate_macd(data['close'])
        
        # Add previous values for crossover detection
        data['sma_20_prev'] = data['sma_20'].shift(1)
        data['sma_50_prev'] = data['sma_50'].shift(1)
        data['rsi_prev'] = data['rsi'].shift(1)
        data['macd_prev'] = data['macd'].shift(1)
        data['macd_signal_prev'] = data['macd_signal'].shift(1)
        
        return data
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple:
        """
        Calculate MACD indicators
        """
        exp1 = prices.ewm(span=fast).mean()
        exp2 = prices.ewm(span=slow).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    
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
                    # Average down/up
                    pos = self.positions[order.symbol]
                    total_qty = pos.quantity + order.quantity
                    total_cost = (pos.quantity * pos.avg_price) + (order.quantity * execution_price)
                    pos.avg_price = total_cost / total_qty
                    pos.quantity = total_qty
                else:
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
        
        # Add to order history
        self.orders.append(order)
    
    def _calculate_portfolio_value(self, current_price: float) -> float:
        """
        Calculate total portfolio value including cash and positions
        """
        position_value = 0
        for pos in self.positions.values():
            position_value += pos.quantity * current_price
        
        return self.cash + position_value
    
    def _calculate_metrics(self):
        """
        Calculate performance metrics
        """
        if not self.portfolio_history:
            return
        
        # Extract portfolio values over time
        values = [ph['total_value'] for ph in self.portfolio_history]
        returns = np.diff(values) / values[:-1]
        
        if len(returns) == 0:
            return
        
        # Total return
        self.metrics['total_return'] = (values[-1] - values[0]) / values[0]
        
        # Annualized return (assuming daily data)
        years = (self.portfolio_history[-1]['timestamp'] - self.portfolio_history[0]['timestamp']).days / 365.25
        if years > 0:
            self.metrics['annualized_return'] = (values[-1] / values[0]) ** (1 / years) - 1
        
        # Volatility (annualized)
        if len(returns) > 1:
            self.metrics['volatility'] = np.std(returns) * np.sqrt(252)  # Annualized
        
        # Sharpe ratio (assuming risk-free rate of 0.02)
        risk_free_rate = 0.02 / 252  # Daily risk-free rate
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
            
            self.metrics['total_trades'] = len(self.trades)
```

## 3. Frontend Design

### 3.1 Directory Structure
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

### 3.2 Main Application Component (frontend/src/App.jsx)
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

### 3.3 Trading Hub Component (frontend/src/pages/TradingHub.jsx)
```jsx
import React, { useState, useEffect, useCallback } from 'react';
import { Card } from '../components/ui/Card';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Target, 
  Zap, 
  Shield, 
  Loader2, 
  Lock, 
  Unlock, 
  Settings2, 
  X, 
  ArrowRight 
} from 'lucide-react';
import { 
  fetchStrategies, 
  fetchProjections, 
  fetchUser, 
  updateUser, 
  fetchPortfolioHistory, 
  fetchPortfolioSummary, 
  fetchExchangeStatus, 
  executeTrade, 
  fetchHoldings, 
  launchStrategy, 
  socket 
} from '../services/api';

import { useUser } from '../context/UserContext';
import { useAppData } from '../context/AppDataContext';

export function TradingHub() {
  const { user: contextUser, toggleTradingMode: toggleUserTradingMode } = useUser();
  const {
    summary,
    projections,
    strategies: appStrategies,
    exchangeStatus,
    stewardPrediction: appStewardPrediction,
    marketResearch,
    marketMovers,
    watchlist,
    loading,
    refreshAllData
  } = useAppData();

  const [strategies, setStrategies] = useState([]);
  const [toggling, setToggling] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [provisioning, setProvisioning] = useState(false);
  const [showLaunchModal, setShowLaunchModal] = useState(false);
  const [newStratSymbol, setNewStratSymbol] = useState('TCS');
  const [newStratName, setNewStratName] = useState('TCS Momentum');
  const [logs, setLogs] = useState([
    { id: 1, time: new Date().toLocaleTimeString(), msg: "Initializing Global Watcher node...", type: 'system' },
    { id: 2, time: new Date().toLocaleTimeString(), msg: "Analyzing RSI divergence on Nifty 50 complex...", type: 'logic' }
  ]);
  const [orderTicker, setOrderTicker] = useState('RELIANCE');
  const [orderQty, setOrderQty] = useState(10);
  const [basket, setBasket] = useState([]);
  const [showBasketModal, setShowBasketModal] = useState(false);
  const [showTopupModal, setShowTopupModal] = useState(false);
  const [topupAmount, setTopupAmount] = useState(0);
  const [activeHoldings, setActiveHoldings] = useState([]);
  const [tradeStatus, setTradeStatus] = useState(null);

  const user = contextUser;

  useEffect(() => {
    const interval = setInterval(() => {
      const types = ['logic', 'system', 'trade'];
      const msgs = [
        "Evaluating order book depth on HDFCBANK...",
        "Sentiment analysis shift detected on social nodes.",
        "Adjusting stop-loss threshold for active mandates.",
        "Handshake pulse successful with NSE execution node.",
        "Optimization loop 842 completed."
      ];
      const newLog = {
        id: Date.now(),
        time: new Date().toLocaleTimeString(),
        msg: msgs[Math.floor(Math.random() * msgs.length)],
        type: types[Math.floor(Math.random() * types.length)]
      };
      setLogs(prev => [newLog, ...prev].slice(0, 10));
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (appStrategies) setStrategies(appStrategies);
  }, [appStrategies]);

  useEffect(() => {
    const loadHoldings = async () => {
      if (!contextUser) return;
      try {
        const currentHoldings = await fetchHoldings(contextUser.id);
        setActiveHoldings(Array.isArray(currentHoldings) ? currentHoldings : []);
      } catch (err) {
        console.error("Failed to load holdings:", err);
      }
    };
    loadHoldings();
  }, [contextUser]);

  const toggleTradingMode = async () => {
    setToggling(true);
    try {
      await toggleUserTradingMode();
    } finally {
      setToggling(false);
    }
  };

  const handleManualTrade = async (action) => {
    if (!user || !orderTicker || orderQty <= 0) {
      setTradeStatus({ type: 'error', msg: 'Select a valid ticker and quantity.' });
      setTimeout(() => setTradeStatus(null), 4000);
      return;
    }

    setExecuting(true);
    try {
      const normalizedSymbol = orderTicker.includes(':') ? orderTicker.split(':').pop() : orderTicker;
      const tradeData = {
        symbol: normalizedSymbol,
        side: action, // BUY or SELL
        quantity: orderQty,
        price: 2450.00, // Mock live price fallback
        order_type: 'MARKET',
        user_id: user.id,
        decision_logic: `User manual override: Explicit ${action} command executed via Trading Hub.`
      };

      const result = await executeTrade(tradeData);
      if (result?.status === 'INSUFFICIENT_FUNDS') {
        const required = result.required_cash || 0;
        setTopupAmount(Math.ceil(required));
        setShowTopupModal(true);
        setExecuting(false);
        return;
      }
      if (result) {
        await refreshAllData();
        const updatedHoldings = await fetchHoldings(user.id);
        setActiveHoldings(updatedHoldings);
        setTradeStatus({ type: 'success', msg: `${action} successful: ${orderQty} units of ${orderTicker}` });
        setTimeout(() => setTradeStatus(null), 5000);
      }
    } catch (err) {
      console.error("Manual trade failed:", err);
      setTradeStatus({ type: 'error', msg: `Trade Failed: ${err.message}` });
      setTimeout(() => setTradeStatus(null), 5000);
    } finally {
      setExecuting(false);
    }
  };

  const addToBasket = () => {
    if (!orderTicker || orderQty <= 0) {
      setTradeStatus({ type: 'error', msg: 'Select a valid ticker and quantity.' });
      setTimeout(() => setTradeStatus(null), 4000);
      return;
    }
    const normalized = orderTicker.includes(':') ? orderTicker.split(':').pop() : orderTicker;
    const price = 2450.00; // Mock price - would come from market data in real implementation
    setBasket(prev => ([...prev, {
      id: Date.now(),
      symbol: normalized,
      quantity: orderQty,
      price: price,
      side: 'BUY'
    }]));
    setTradeStatus({ type: 'success', msg: `Added ${orderQty} ${normalized} to basket.` });
    setTimeout(() => setTradeStatus(null), 3000);
  };

  const removeFromBasket = (id) => {
    setBasket(prev => prev.filter(item => item.id !== id));
  };

  const basketTotal = basket.reduce((sum, item) => sum + (item.price * item.quantity), 0);

  const executeBasket = async () => {
    if (!user || basket.length === 0) return;

    setExecuting(true);
    try {
      for (const item of basket) {
        await executeTrade({
          symbol: item.symbol,
          side: item.side,
          quantity: item.quantity,
          price: item.price,
          order_type: 'MARKET',
          user_id: user.id,
          decision_logic: `Basket order: ${item.side} ${item.quantity} ${item.symbol}`
        });
      }
      await refreshAllData();
      const updatedHoldings = await fetchHoldings(user.id);
      setActiveHoldings(updatedHoldings);
      setBasket([]);
      setTradeStatus({ type: 'success', msg: 'Basket executed successfully.' });
      setTimeout(() => setTradeStatus(null), 4000);
    } catch (err) {
      console.error("Basket trade failed:", err);
      setTradeStatus({ type: 'error', msg: 'Basket execution failed.' });
      setTimeout(() => setTradeStatus(null), 4000);
    } finally {
      setExecuting(false);
    }
  };

  const handleLaunchStrategy = async () => {
    if (!contextUser) return;
    setProvisioning(true);
    try {
      const stratData = {
        name: newStratName,
        symbol: newStratSymbol,
        status: 'RUNNING',
        pnl: '+? 0.00',
        trades: '0'
      };
      const result = await launchStrategy(contextUser.id, stratData);
      if (result) {
        setStrategies(prev => [...prev, result]);
        setShowLaunchModal(false);
        setNewStratName('');
        setNewStratSymbol('');
        alert(`Strategy ${newStratName} (${newStratSymbol}) successfully provisioned and deployed.`);
      }
    } catch (err) {
      console.error("Launch failed:", err);
    } finally {
      setProvisioning(false);
    }
  };

  if (loading) {
    return (
      <div className="h-[60vh] flex flex-col items-center justify-center text-slate-400">
        <Loader2 className="animate-spin mb-4" size={32} />
        <p className="font-bold uppercase text-[10px] tracking-widest text-[#0A2A4D]">Synchronizing Execution Parameters...</p>
      </div>
    );
  }

  const symbolOptions = useMemo(() => {
    const base = [
      { symbol: 'RELIANCE', exchange: 'NSE' },
      { symbol: 'TCS', exchange: 'NSE' },
      { symbol: 'HDFCBANK', exchange: 'NSE' },
      { symbol: 'INFY', exchange: 'NSE' },
      { symbol: 'ICICIBANK', exchange: 'NSE' },
      { symbol: 'SENSEX', exchange: 'BSE' },
      { symbol: 'BOM500002', exchange: 'BSE' },
      { symbol: 'BOM500010', exchange: 'BSE' },
      { symbol: 'GOLD', exchange: 'MCX' },
      { symbol: 'SILVER', exchange: 'MCX' },
      { symbol: 'CRUDEOIL', exchange: 'MCX' },
      { symbol: 'NATURALGAS', exchange: 'MCX' }
    ];

    const fromHoldings = (activeHoldings || []).map(h => ({ 
      symbol: h.symbol, 
      exchange: h.exchange || 'NSE' 
    }));
    const fromWatchlist = (watchlist || []).map(w => ({ 
      symbol: w.symbol, 
      exchange: w.exchange || 'NSE' 
    }));
    const fromMovers = (marketMovers || []).map(m => ({ 
      symbol: m.symbol, 
      exchange: m.exchange || 'NSE' 
    }));
    const fromProjections = (projections || []).map(p => ({ 
      symbol: p.ticker, 
      exchange: 'NSE' 
    }));

    const combined = [...base, ...fromHoldings, ...fromWatchlist, ...fromMovers, ...fromProjections];
    const seen = new Set();
    return combined.filter(item => {
      if (!item.symbol) return false;
      const key = `${item.exchange}:${item.symbol}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }, [activeHoldings, watchlist, marketMovers, projections]);

  useEffect(() => {
    if (symbolOptions.length > 0 && !orderTicker) {
      setOrderTicker(symbolOptions[0].symbol);
    }
  }, [symbolOptions, orderTicker]);

  return (
    <div data-testid="trading-hub-container" className="pb-4 space-y-8 animate-in slide-in-from-bottom-4 duration-500">
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 font-heading">Trading Hub</h1>
          <p className="text-slate-500 mt-1 uppercase text-[10px] font-bold tracking-widest leading-none flex items-center gap-2">
            <span data-testid="algo-status" className={`h-2 w-2 rounded-full ${user?.trading_mode === 'AUTO' ? 'bg-green-500 animate-pulse' : 'bg-orange-500'}`} />
            Algo Engine: {user?.trading_mode === 'AUTO' ? 'Autonomous Mode Active' : 'Manual Override Active'}
          </p>
        </div>

        <div className="flex items-center gap-3 bg-slate-50 p-1.5 rounded-2xl border border-slate-100 shadow-inner">
          <button
            data-testid="mode-toggle-auto"
            onClick={() => user?.trading_mode !== 'AUTO' && toggleTradingMode()}
            disabled={toggling}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all duration-300 ${user?.trading_mode === 'AUTO'
              ? 'bg-primary text-white shadow-xl shadow-primary/40 ring-4 ring-primary/10 scale-105'
              : 'bg-white text-slate-400 hover:text-slate-600 opacity-60 border border-slate-200'
              }`}
          >
            {user?.trading_mode === 'AUTO' ? <Shield size={14} className="animate-pulse" /> : <Lock size={14} />}
            Steward Auto
          </button>
          <button
            data-testid="mode-toggle-manual"
            onClick={() => user?.trading_mode !== 'MANUAL' && toggleTradingMode()}
            disabled={toggling}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all duration-300 ${user?.trading_mode === 'MANUAL'
              ? 'bg-orange-600 text-white shadow-xl shadow-orange-600/40 ring-4 ring-orange-500/10 scale-105'
              : 'bg-white text-slate-400 hover:text-slate-600 opacity-60 border border-slate-200'
              }`}
          >
            {user?.trading_mode === 'MANUAL' ? <Unlock size={14} className="animate-bounce" /> : <Shield size={14} />}
            Manual Mode
          </button>
        </div>

        <div className="h-10 w-[1px] bg-slate-100 hidden md:block mx-4" />

        <div className="flex flex-col items-end mr-4">
          <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Exchange Status</span>
          <div className="flex items-center gap-2">
            <span className="h-1.5 w-1.5 bg-green-500 rounded-full animate-pulse" />
            <span className="text-[10px] font-black text-slate-900">{exchangeStatus?.exchange || 'NSE'} {exchangeStatus?.latency || 'ONLINE'}</span>
          </div>
        </div>

        <button
          onClick={() => setShowLaunchModal(true)}
          className="bg-primary text-white px-6 py-3 rounded-xl font-bold flex items-center gap-2 hover:opacity-90 active:scale-95 transition-all shadow-lg shadow-primary/20 group"
        >
          <Zap size={18} fill="currentColor" className="group-hover:animate-bounce" />
          Launch New Strategy
        </button>
      </header>

      {/* Strategy Provisioning Modal */}
      {showLaunchModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-md animate-in fade-in duration-300">
          <div className="w-full max-w-md bg-white p-8 rounded-3xl shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary to-green-500" />
            <button
              onClick={() => !provisioning && setShowLaunchModal(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 transition-colors"
            >
              <X size={20} />
            </button>

            <div className="text-center mb-8">
              <div className="h-16 w-16 bg-slate-50 rounded-2xl flex items-center justify-center mx-auto mb-4 text-primary shadow-inner">
                <Zap size={32} fill="currentColor" />
              </div>
              <h3 className="text-xl font-black text-slate-900 uppercase tracking-tight">Provision Agent Mandate</h3>
              <p className="text-xs font-bold text-slate-500 mt-2 uppercase tracking-widest">Deploy New Autonomous Trading Node</p>
            </div>

            <div className="space-y-6">
              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Strategy Name</label>
                <input
                  type="text"
                  value={newStratName}
                  onChange={(e) => setNewStratName(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm font-black text-slate-900 focus:ring-4 focus:ring-primary/10 transition-all outline-none"
                  placeholder="Enter strategy name"
                />
              </div>

              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Target Asset/Ticker</label>
                <input
                  type="text"
                  list="strategy-ticker-options"
                  value={newStratSymbol}
                  onChange={(e) => setNewStratSymbol(e.target.value.toUpperCase())}
                  className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm font-black text-slate-900 focus:ring-4 focus:ring-primary/10 transition-all outline-none"
                  placeholder="Select or type symbol"
                />
                <datalist id="strategy-ticker-options">
                  {symbolOptions.map((item) => (
                    <option key={`${item.exchange}-strat-${item.symbol}`} value={item.symbol}>
                      {item.exchange}
                    </option>
                  ))}
                </datalist>
              </div>

              <div className="bg-slate-900 p-4 rounded-2xl text-white/80 space-y-3">
                <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-widest">
                  <span className="opacity-60">Execution Tier</span>
                  <span className="text-primary">ULTRA-LOW LATENCY</span>
                </div>
                <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-widest">
                  <span className="opacity-60">Risk Profile</span>
                  <span className="text-green-400 font-bold">BALANCED</span>
                </div>
              </div>

              <button
                onClick={handleLaunchStrategy}
                disabled={provisioning}
                className="w-full py-4 bg-primary text-white rounded-2xl font-black uppercase tracking-[0.2em] shadow-xl shadow-primary/20 hover:opacity-95 transition-all flex items-center justify-center gap-3 active:scale-95"
              >
                {provisioning ? <Loader2 className="animate-spin" size={18} /> : <Zap size={18} fill="currentColor" />}
                {provisioning ? 'Initializing Node...' : 'Confirm Deployment'}
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <Card className="p-6 border-slate-200 shadow-sm col-span-1 lg:col-span-3">
          <div className="flex justify-between items-center mb-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-slate-900 rounded-lg text-primary">
                <Activity size={20} />
              </div>
              <div>
                <h3 className="font-black text-slate-900 uppercase text-xs tracking-widest">Manual Order Ticket</h3>
                <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mt-1">Direct Exchange Access</p>
              </div>
            </div>
            {user?.trading_mode === 'AUTO' && (
              <div className="flex items-center gap-2 px-3 py-1 bg-primary/10 border border-primary/20 rounded-lg animate-pulse">
                <Activity size={12} className="text-primary" />
                <span className="text-[10px] font-black text-primary uppercase tracking-widest">AI observing order book...</span>
              </div>
            )}
          </div>

          <div data-testid="manual-order-ticket" className={`flex flex-col md:flex-row gap-6 items-end ${user?.trading_mode === 'AUTO' ? 'opacity-30 grayscale pointer-events-none' : ''}`}>
            <div className="flex-1 w-full space-y-2">
              <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Asset Ticker</label>
              <div className="relative">
                <input
                  type="text"
                  list="ticker-options"
                  value={orderTicker}
                  onChange={(e) => setOrderTicker(e.target.value.toUpperCase())}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm font-black text-slate-900 focus:ring-2 focus:ring-primary/20 transition-all outline-none"
                  placeholder="Type or select a symbol"
                />
                <datalist id="ticker-options">
                  {symbolOptions.map((item) => (
                    <option key={`${item.exchange}-${item.symbol}`} value={item.symbol}>
                      {item.exchange}
                    </option>
                  ))}
                </datalist>
              </div>
              <div className="flex flex-wrap gap-2 mt-2">
                {symbolOptions.slice(0, 6).map((item) => (
                  <button
                    key={`${item.exchange}-quick-${item.symbol}`}
                    type="button"
                    onClick={() => setOrderTicker(item.symbol)}
                    className={`px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest border ${orderTicker === item.symbol ? 'bg-primary/10 border-primary text-primary' : 'bg-white border-slate-200 text-slate-500 hover:text-slate-700'}`}
                  >
                    {item.exchange}:{item.symbol}
                  </button>
                ))}
              </div>
            </div>
            <div className="w-full md:w-32 space-y-2">
              <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Units</label>
              <input
                type="number"
                value={orderQty}
                onChange={(e) => setOrderQty(parseInt(e.target.value) || 0)}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm font-black text-slate-900 focus:ring-2 focus:ring-primary/20 transition-all outline-none"
                placeholder="Qty"
              />
            </div>
            <div className="flex gap-3 w-full md:w-auto">
              <button
                onClick={() => handleManualTrade('BUY')}
                disabled={executing}
                className="px-6 py-3.5 bg-green-600 text-white rounded-xl font-black text-sm uppercase tracking-widest hover:bg-green-700 transition-all shadow-lg shadow-green-600/20 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {executing ? <Loader2 size={16} className="animate-spin" /> : <TrendingUp size={16} />}
                Buy
              </button>
              <button
                onClick={() => handleManualTrade('SELL')}
                disabled={executing}
                className="px-6 py-3.5 bg-red-600 text-white rounded-xl font-black text-sm uppercase tracking-widest hover:bg-red-700 transition-all shadow-lg shadow-red-600/20 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {executing ? <Loader2 size={16} className="animate-spin" /> : <TrendingDown size={16} />}
                Sell
              </button>
              <button
                onClick={addToBasket}
                className="px-4 py-3.5 bg-slate-900 text-white rounded-xl font-black text-sm uppercase tracking-widest hover:bg-slate-800 transition-all"
              >
                <Target size={16} />
              </button>
            </div>
          </div>
        </Card>

        <Card className="p-6 border-slate-200 shadow-sm">
          <div className="flex flex-col h-full">
            <h3 className="font-black text-slate-900 uppercase text-xs tracking-widest mb-4">Quick Actions</h3>

            <div className="space-y-3 flex-1">
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
                  <Target size={16} className="text-primary" />
                  <span className="font-black text-slate-900">Risk Controls</span>
                </div>
                <p className="text-xs text-slate-500 mt-1">Portfolio risk management</p>
              </button>

              <button className="w-full p-4 bg-slate-50 border border-slate-200 rounded-xl text-left hover:bg-slate-100 transition-colors">
                <div className="flex items-center gap-2">
                  <Activity size={16} className="text-primary" />
                  <span className="font-black text-slate-900">Live Feed</span>
                </div>
                <p className="text-xs text-slate-500 mt-1">Real-time market data</p>
              </button>
            </div>
          </div>
        </Card>
      </div>

      {/* Active Strategies */}
      <Card className="p-6 border-slate-200 shadow-sm">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-black text-slate-900 uppercase tracking-widest">Active Strategies</h3>
          <span className="text-sm font-black bg-primary/10 text-primary px-3 py-1 rounded-full">
            {strategies.length} running
          </span>
        </div>

        {strategies.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {strategies.map((strategy) => (
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
                        <span className="font-black">{order.quantity} @ ₹ {order.price}</span>
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

                <div className="flex justify-between items-center mb-6 p-4 bg-slate-50 rounded-xl">
                  <span className="font-black text-slate-900">Total Value:</span>
                  <span className="text-xl font-black text-slate-900">₹ {basketTotal.toFixed(2)}</span>
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
                    {executing ? <Loader2 size={16} className="animate-spin" /> : <Zap size={16} />}
                    Execute Basket
                  </button>
                </div>
              </>
            ) : (
              <div className="text-center py-8">
                <Target size={48} className="mx-auto text-slate-300 mb-4" />
                <h4 className="font-black text-slate-500 mb-2">Basket is Empty</h4>
                <p className="text-sm text-slate-400">Add orders to your basket to execute them together</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Trading Logic Console */}
      <Card className="p-6 border-slate-200 shadow-sm">
        <h3 className="text-lg font-black text-slate-900 uppercase tracking-widest mb-6">Intelligence Log</h3>

        <div className="space-y-3 max-h-64 overflow-y-auto">
          {logs.map((log) => (
            <div key={log.id} className="flex gap-3 text-xs font-bold text-slate-700 bg-slate-50 p-3 rounded-xl border border-slate-100">
              <span className="text-slate-400 font-mono">[{log.time}]</span>
              <span className={`font-black uppercase tracking-widest ${
                log.type === 'system' ? 'text-indigo-600' : 
                log.type === 'logic' ? 'text-primary' : 
                'text-green-600'
              }`}>
                {log.type.toUpperCase()}:
              </span>
              <span className="text-slate-700">{log.msg}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
```

## 4. Database Schema

### 4.1 Entity Relationship Diagram
```
Users (1) ----< Portfolios
Users (1) ----< Trades
Users (1) ----< Strategies
Strategies (1) ----< Trades
Portfolios (1) ----< Holdings
Holdings (*) ----< Trades
```

### 4.2 Table Definitions

#### 4.2.1 Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    risk_tolerance VARCHAR(20) DEFAULT 'MODERATE',
    trading_mode VARCHAR(20) DEFAULT 'MANUAL',
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4.2.2 Portfolios Table
```sql
CREATE TABLE portfolios (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(255),
    total_value DECIMAL(15,2) DEFAULT 0.00,
    cash_balance DECIMAL(15,2) DEFAULT 0.00,
    invested_amount DECIMAL(15,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4.2.3 Trades Table
```sql
CREATE TABLE trades (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    strategy_id INTEGER REFERENCES strategies(id),
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL, -- BUY/SELL
    quantity INTEGER NOT NULL,
    entry_price DECIMAL(10,2) NOT NULL,
    exit_price DECIMAL(10,2),
    entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    exit_time TIMESTAMP,
    pnl DECIMAL(10,2) DEFAULT 0.00,
    pnl_percentage DECIMAL(5,2) DEFAULT 0.00,
    status VARCHAR(20) DEFAULT 'OPEN', -- OPEN/CLOSED/PENDING
    order_id VARCHAR(50),
    exchange_order_id VARCHAR(50),
    commission DECIMAL(10,2) DEFAULT 0.00,
    fees DECIMAL(10,2) DEFAULT 0.00,
    stop_loss DECIMAL(10,2),
    take_profit DECIMAL(10,2),
    trailing_stop BOOLEAN DEFAULT FALSE,
    decision_logic TEXT
);
```

#### 4.2.4 Strategies Table
```sql
CREATE TABLE strategies (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    strategy_type VARCHAR(50) NOT NULL,
    parameters JSON,
    status VARCHAR(20) DEFAULT 'INACTIVE',
    initial_capital DECIMAL(15,2) NOT NULL,
    current_capital DECIMAL(15,2) DEFAULT 0.00,
    total_pnl DECIMAL(10,2) DEFAULT 0.00,
    total_trades INTEGER DEFAULT 0,
    win_rate DECIMAL(5,2) DEFAULT 0.00,
    sharpe_ratio DECIMAL(8,4) DEFAULT 0.0000,
    max_drawdown DECIMAL(5,2) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 5. API Design

### 5.1 REST API Endpoints

#### 5.1.1 Trading Endpoints
```
POST   /api/v1/trades/place          # Place a new trade
GET    /api/v1/trades/{id}          # Get specific trade details
GET    /api/v1/trades/              # Get user's trade history
PUT    /api/v1/trades/{id}/close    # Close a trade
DELETE /api/v1/trades/{id}/cancel   # Cancel an order
```

#### 5.1.2 Portfolio Endpoints
```
GET    /api/v1/portfolio/summary     # Get portfolio summary
GET    /api/v1/portfolio/holdings    # Get current holdings
GET    /api/v1/portfolio/history     # Get portfolio history
POST   /api/v1/portfolio/deposit     # Deposit funds
POST   /api/v1/portfolio/withdraw    # Withdraw funds
```

#### 5.1.3 Strategy Endpoints
```
GET    /api/v1/strategies/          # Get all strategies
POST   /api/v1/strategies/          # Create new strategy
GET    /api/v1/strategies/{id}      # Get specific strategy
PUT    /api/v1/strategies/{id}      # Update strategy
DELETE /api/v1/strategies/{id}      # Delete strategy
POST   /api/v1/strategies/{id}/run  # Execute strategy
```

#### 5.1.4 Backtesting Endpoints
```
POST   /api/v1/backtesting/run      # Run backtest
GET    /api/v1/backtesting/strategies # Get available strategies
POST   /api/v1/backtesting/optimize  # Optimize strategy parameters
```

### 5.2 WebSocket Events

#### 5.2.1 Market Data Events
```
'market_update'      # Real-time market data
'market_movers'      # Top gainers/losers
'order_book_depth'   # Order book depth data
'portfolio_update'   # Portfolio value updates
'trade_execution'    # Trade execution notifications
'strategy_signal'    # Strategy signals
```

#### 5.2.2 User-Specific Events
```
'user_portfolio'     # User-specific portfolio updates
'user_trades'        # User-specific trade updates
'risk_alert'         # Risk management alerts
'execution_status'   # Order execution status
```

## 6. Security Architecture

### 6.1 Authentication & Authorization
- JWT-based authentication with refresh tokens
- Role-based access control (RBAC)
- OAuth2 with password flow
- Session management with automatic expiry

### 6.2 Data Protection
- AES-256 encryption for sensitive data
- SSL/TLS for all communications
- Input validation and sanitization
- SQL injection prevention
- XSS protection

### 6.3 API Security
- Rate limiting per IP/user
- API key management
- Request validation
- CORS configuration
- CSRF protection

### 6.4 Infrastructure Security
- Network segmentation
- Firewall rules
- VPN access for admin
- Regular security audits
- Vulnerability scanning

## 7. Performance & Scalability

### 7.1 Caching Strategy
- Redis for session management
- API response caching
- Market data caching with TTL
- Database query result caching

### 7.2 Database Optimization
- Connection pooling
- Query optimization
- Indexing strategy
- Partitioning for historical data

### 7.3 Load Balancing
- Multiple backend instances
- Session affinity
- Health checks
- Auto-scaling based on load

### 7.4 Performance Metrics
- Response time monitoring
- Throughput measurements
- Error rate tracking
- Resource utilization

## 8. Monitoring & Logging

### 8.1 Application Logs
- Structured logging with correlation IDs
- Different log levels for different environments
- Centralized log aggregation
- Log retention policies

### 8.2 Metrics Collection
- Application performance metrics
- Business metrics (trades, users, revenue)
- System resource metrics
- Custom business KPIs

### 8.3 Alerting System
- Real-time alerting for critical issues
- Threshold-based alerts
- Escalation policies
- Integration with monitoring tools

### 8.4 Health Checks
- Application health endpoints
- Database connectivity checks
- External service availability
- Performance monitoring

## 9. Deployment Architecture

### 9.1 Docker Configuration
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
    && cd ta-lib/ \
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

### 9.2 Docker Compose
```yaml
version: '3.8'

services:
  backend:
    build: .
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
      POSTGRES_DB: stocksteward_ai
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

## 10. Testing Strategy

### 10.1 Unit Tests
- Individual function testing
- Service layer testing
- Model validation testing
- Utility function testing

### 10.2 Integration Tests
- API endpoint testing
- Database integration testing
- External service integration
- WebSocket connection testing

### 10.3 End-to-End Tests
- Complete user journey testing
- Trading workflow testing
- Backtesting validation
- Performance metrics verification

### 10.4 Load Testing
- Concurrent user testing
- High-frequency trading simulation
- Database performance testing
- API response time validation

This comprehensive technical design document provides a detailed blueprint for the StockSteward AI platform, covering all aspects from system architecture to deployment considerations.