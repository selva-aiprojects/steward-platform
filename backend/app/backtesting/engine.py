"""
Advanced Backtesting Engine for Algorithmic Trading Strategies
"""
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)


class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"


@dataclass
class Order:
    symbol: str
    side: OrderSide
    quantity: int
    price: float
    timestamp: datetime
    order_type: OrderType = OrderType.MARKET
    filled: bool = False
    filled_price: Optional[float] = None
    filled_time: Optional[datetime] = None


@dataclass
class Position:
    symbol: str
    quantity: int
    avg_price: float
    entry_time: datetime
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0


@dataclass
class PortfolioState:
    cash: float
    positions: Dict[str, Position]
    total_value: float
    timestamp: datetime


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
    """
    Advanced backtesting engine with realistic market simulation
    """
    
    def __init__(
        self,
        initial_capital: float = 100000.0,
        commission_rate: float = 0.001,  # 0.1% commission
        slippage_rate: float = 0.0005,   # 0.05% slippage
        data_source: str = "historical"
    ):
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate
        self.data_source = data_source
        
        # State tracking
        self.cash = initial_capital
        self.positions: Dict[str, Position] = {}
        self.orders: List[Order] = []
        self.portfolio_history: List[PortfolioState] = []
        self.trades: List[Trade] = []
        
        # Performance metrics
        self.metrics = {
            'total_return': 0.0,
            'annualized_return': 0.0,
            'volatility': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'win_rate': 0.0,
            'profit_factor': 0.0,
            'total_trades': 0
        }
    
    def load_historical_data(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Load historical market data for backtesting
        """
        # In a real implementation, this would fetch from a database or API
        # For now, we'll generate synthetic data
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Generate realistic OHLCV data
        np.random.seed(42)  # For reproducible results
        returns = np.random.normal(0.0005, 0.02, len(dates))  # Daily returns
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
        
        # Calculate additional indicators
        data['sma_20'] = data['close'].rolling(window=20).mean()
        data['sma_50'] = data['close'].rolling(window=50).mean()
        data['rsi'] = self._calculate_rsi(data['close'])
        data['macd'], data['macd_signal'], data['macd_hist'] = self._calculate_macd(data['close'])
        
        # Add previous values for crossover detection
        data['sma_20_prev'] = data['sma_20'].shift(1)
        data['sma_50_prev'] = data['sma_50'].shift(1)
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
    
    def place_order(self, order: Order) -> bool:
        """
        Place an order in the backtesting engine
        """
        if order.filled:
            return False
            
        # Check if we have enough cash for BUY orders
        required_cash = order.quantity * order.price * (1 + self.commission_rate)
        if order.side == OrderSide.BUY and self.cash < required_cash:
            logger.warning(f"Insufficient cash for order: {order.symbol}")
            return False
        
        # Apply slippage
        filled_price = self._apply_slippage(order.price, order.side)
        
        # Execute the trade
        self._execute_trade(order, filled_price)
        return True
    
    def _apply_slippage(self, price: float, side: OrderSide) -> float:
        """
        Apply slippage based on order side
        """
        if side == OrderSide.BUY:
            return price * (1 + self.slippage_rate)
        else:
            return price * (1 - self.slippage_rate)
    
    def _execute_trade(self, order: Order, filled_price: float):
        """
        Execute a trade and update portfolio
        """
        order.filled = True
        order.filled_price = filled_price
        order.filled_time = order.timestamp
        
        # Calculate commission
        commission = order.quantity * filled_price * self.commission_rate
        
        if order.side == OrderSide.BUY:
            # Deduct cash
            cost = order.quantity * filled_price + commission
            self.cash -= cost
            
            # Update position
            if order.symbol in self.positions:
                pos = self.positions[order.symbol]
                # Average down/up
                total_qty = pos.quantity + order.quantity
                total_cost = (pos.quantity * pos.avg_price) + (order.quantity * filled_price)
                pos.avg_price = total_cost / total_qty
                pos.quantity = total_qty
            else:
                self.positions[order.symbol] = Position(
                    symbol=order.symbol,
                    quantity=order.quantity,
                    avg_price=filled_price,
                    entry_time=order.timestamp
                )
        else:  # SELL
            # Add cash
            proceeds = order.quantity * filled_price - commission
            self.cash += proceeds
            
            # Update position
            if order.symbol in self.positions:
                pos = self.positions[order.symbol]
                if pos.quantity >= order.quantity:
                    # Partial or full close
                    realized_pnl = (filled_price - pos.avg_price) * order.quantity
                    pos.realized_pnl += realized_pnl
                    
                    # Record the trade
                    trade = Trade(
                        symbol=order.symbol,
                        side='SELL',
                        quantity=order.quantity,
                        entry_price=pos.avg_price,
                        exit_price=filled_price,
                        entry_time=pos.entry_time,
                        exit_time=order.timestamp,
                        pnl=realized_pnl,
                        pnl_pct=realized_pnl / (pos.avg_price * order.quantity)
                    )
                    self.trades.append(trade)
                    
                    pos.quantity -= order.quantity
                    
                    # Remove position if fully closed
                    if pos.quantity == 0:
                        del self.positions[order.symbol]
        
        # Add to order history
        self.orders.append(order)
    
    def run_backtest(
        self,
        strategy_func: Callable,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Run a backtest with the given strategy
        """
        # Load historical data
        data = self.load_historical_data(symbol, start_date, end_date)
        
        # Reset state
        self.cash = self.initial_capital
        self.positions = {}
        self.orders = []
        self.portfolio_history = []
        self.trades = []
        
        # Run the strategy for each bar
        for idx, row in data.iterrows():
            current_time = row['date']
            
            # Update portfolio value
            portfolio_value = self._calculate_portfolio_value(row['close'])
            
            # Store portfolio state
            self.portfolio_history.append(PortfolioState(
                cash=self.cash,
                positions=self.positions.copy(),
                total_value=portfolio_value,
                timestamp=current_time
            ))
            
            # Generate signals and execute strategy
            signal = strategy_func(row, self.positions, self.cash)
            
            if signal:
                order = Order(
                    symbol=symbol,
                    side=OrderSide(signal['side']),
                    quantity=signal['quantity'],
                    price=row['close'],
                    timestamp=current_time,
                    order_type=OrderType(signal.get('order_type', 'MARKET'))
                )
                
                self.place_order(order)
        
        # Calculate final metrics
        self._calculate_metrics()
        
        return {
            'initial_capital': self.initial_capital,
            'final_value': self._calculate_portfolio_value(data.iloc[-1]['close']),
            'total_return': self.metrics['total_return'],
            'annualized_return': self.metrics['annualized_return'],
            'volatility': self.metrics['volatility'],
            'sharpe_ratio': self.metrics['sharpe_ratio'],
            'max_drawdown': self.metrics['max_drawdown'],
            'win_rate': self.metrics['win_rate'],
            'profit_factor': self.metrics['profit_factor'],
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
            'portfolio_history': [
                {
                    'timestamp': ps.timestamp,
                    'total_value': ps.total_value,
                    'cash': ps.cash
                } for ps in self.portfolio_history
            ]
        }
    
    def _calculate_portfolio_value(self, current_price: float) -> float:
        """
        Calculate total portfolio value including cash and positions
        """
        position_value = 0
        for pos in self.positions.values():
            # Use current price for this symbol if available, otherwise use last known price
            position_value += pos.quantity * current_price
        
        return self.cash + position_value
    
    def _calculate_metrics(self):
        """
        Calculate performance metrics
        """
        if not self.portfolio_history:
            return
        
        # Extract portfolio values over time
        values = [ps.total_value for ps in self.portfolio_history]
        returns = np.diff(values) / values[:-1]
        
        if len(returns) == 0:
            return
        
        # Total return
        self.metrics['total_return'] = (values[-1] - values[0]) / values[0]
        
        # Annualized return (assuming daily data)
        years = (self.portfolio_history[-1].timestamp - self.portfolio_history[0].timestamp).days / 365.25
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


# Example strategy functions
def sma_crossover_strategy(row: pd.Series, positions: Dict[str, Position], cash: float) -> Optional[Dict]:
    """
    Example SMA crossover strategy
    """
    if pd.isna(row.get('sma_20')) or pd.isna(row.get('sma_50')):
        return None
    
    symbol = 'TEST'
    current_pos = positions.get(symbol, None)
    current_qty = current_pos.quantity if current_pos else 0
    
    # Buy signal: SMA 20 crosses above SMA 50
    if (row['sma_20'] > row['sma_50'] and 
        row.get('sma_20_prev', 0) <= row.get('sma_50_prev', 0)):
        if current_qty <= 0:  # Only enter if not already long
            return {
                'side': 'BUY',
                'quantity': int(cash * 0.1 / row['close']),  # Risk 10% of capital
                'order_type': 'MARKET'
            }
    
    # Sell signal: SMA 20 crosses below SMA 50
    elif (row['sma_20'] < row['sma_50'] and 
          row.get('sma_20_prev', 0) >= row.get('sma_50_prev', 0)):
        if current_qty > 0:  # Only exit if currently long
            return {
                'side': 'SELL',
                'quantity': current_qty,
                'order_type': 'MARKET'
            }
    
    return None


def rsi_mean_reversion_strategy(row: pd.Series, positions: Dict[str, Position], cash: float) -> Optional[Dict]:
    """
    RSI mean reversion strategy
    """
    if pd.isna(row.get('rsi')):
        return None
    
    rsi = row['rsi']
    symbol = 'TEST'
    current_pos = positions.get(symbol, None)
    current_qty = current_pos.quantity if current_pos else 0
    
    # Buy signal: RSI oversold (< 30)
    if rsi < 30 and current_qty <= 0:
        return {
            'side': 'BUY',
            'quantity': int(cash * 0.05 / row['close']),  # Risk 5% of capital
            'order_type': 'MARKET'
        }
    
    # Sell signal: RSI overbought (> 70)
    elif rsi > 70 and current_qty > 0:
        return {
            'side': 'SELL',
            'quantity': current_qty,
            'order_type': 'MARKET'
        }
    
    return None


def macd_strategy(row: pd.Series, positions: Dict[str, Position], cash: float) -> Optional[Dict]:
    """
    MACD strategy
    """
    if (pd.isna(row.get('macd')) or pd.isna(row.get('macd_signal')) or 
        pd.isna(row.get('macd_hist'))):
        return None
    
    macd = row['macd']
    signal = row['macd_signal']
    
    # Previous values for crossover detection
    prev_macd = row.get('macd_prev', 0)
    prev_signal = row.get('macd_signal_prev', 0)
    
    symbol = 'TEST'
    current_pos = positions.get(symbol, None)
    current_qty = current_pos.quantity if current_pos else 0
    
    # Bullish crossover: MACD line crosses above signal line
    if macd > signal and prev_macd <= prev_signal:
        if current_qty <= 0:  # Only enter if not already long
            return {
                'side': 'BUY',
                'quantity': int(cash * 0.08 / row['close']),  # Risk 8% of capital
                'order_type': 'MARKET'
            }
    
    # Bearish crossover: MACD line crosses below signal line
    elif macd < signal and prev_macd >= prev_signal:
        if current_qty > 0:  # Only exit if currently long
            return {
                'side': 'SELL',
                'quantity': current_qty,
                'order_type': 'MARKET'
            }
    
    return None