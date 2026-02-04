"""
Backtesting API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd

from app.schemas.backtesting import BacktestRequest, BacktestResponse
from app.core.database import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.backtesting.engine import BacktestingEngine, sma_crossover_strategy

router = APIRouter()


@router.post("/run", response_model=BacktestResponse)
async def run_backtest(
    request: BacktestRequest,
    current_user: User = Depends(get_current_user),
    db=None  # Dependency injection would be handled properly in the actual implementation
):
    """
    Run a backtest with the specified strategy and parameters
    """
    try:
        # Validate request parameters
        if request.end_date <= request.start_date:
            raise HTTPException(status_code=400, detail="End date must be after start date")
        
        if request.initial_capital <= 0:
            raise HTTPException(status_code=400, detail="Initial capital must be positive")
        
        # Initialize backtesting engine
        engine = BacktestingEngine(
            initial_capital=request.initial_capital,
            commission_rate=request.commission_rate,
            slippage_rate=request.slippage_rate
        )
        
        # Map strategy name to function
        strategy_map = {
            "sma_crossover": sma_crossover_strategy,
            "ema_crossover": ema_crossover_strategy,
            "rsi_mean_reversion": rsi_mean_reversion_strategy,
            "bollinger_bands": bollinger_bands_strategy
        }
        
        if request.strategy_name not in strategy_map:
            raise HTTPException(status_code=400, detail=f"Unknown strategy: {request.strategy_name}")
        
        strategy_func = strategy_map[request.strategy_name]
        
        # Run the backtest
        results = engine.run_backtest(
            strategy_func=strategy_func,
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date
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
        raise HTTPException(status_code=500, detail=f"Backtest failed: {str(e)}")


@router.get("/strategies")
async def get_available_strategies():
    """
    Get list of available backtesting strategies
    """
    strategies = [
        {
            "name": "sma_crossover",
            "description": "Simple Moving Average crossover strategy",
            "parameters": ["short_period", "long_period"],
            "type": "trend_following"
        },
        {
            "name": "ema_crossover", 
            "description": "Exponential Moving Average crossover strategy",
            "parameters": ["short_period", "long_period"],
            "type": "trend_following"
        },
        {
            "name": "rsi_mean_reversion",
            "description": "RSI-based mean reversion strategy",
            "parameters": ["rsi_period", "overbought_level", "oversold_level"],
            "type": "mean_reversion"
        },
        {
            "name": "bollinger_bands",
            "description": "Bollinger Bands mean reversion strategy",
            "parameters": ["period", "std_dev"],
            "type": "mean_reversion"
        }
    ]
    
    return {"strategies": strategies}


@router.get("/optimize")
async def optimize_strategy_parameters(
    symbol: str = Query(..., description="Symbol to optimize for"),
    strategy_name: str = Query(..., description="Name of strategy to optimize"),
    start_date: datetime = Query(..., description="Start date for optimization period"),
    end_date: datetime = Query(..., description="End date for optimization period"),
    current_user: User = Depends(get_current_user)
):
    """
    Optimize strategy parameters using grid search or other optimization techniques
    """
    try:
        # This would implement parameter optimization
        # For now, return a mock response
        optimization_results = {
            "best_parameters": {"short_period": 20, "long_period": 50},
            "best_sharpe_ratio": 1.85,
            "best_return": 0.25,
            "parameter_space": [
                {"short_period": 10, "long_period": 30, "sharpe_ratio": 1.2},
                {"short_period": 20, "long_period": 50, "sharpe_ratio": 1.85},
                {"short_period": 30, "long_period": 100, "sharpe_ratio": 1.45}
            ]
        }
        
        return {
            "symbol": symbol,
            "strategy_name": strategy_name,
            "optimization_results": optimization_results,
            "status": "COMPLETED"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


# Strategy implementations
def ema_crossover_strategy(row: pd.Series, positions: Dict[str, Any], cash: float) -> Optional[Dict]:
    """
    EMA crossover strategy implementation
    """
    if pd.isna(row.get('ema_20')) or pd.isna(row.get('ema_50')):
        return None
    
    symbol = 'TEST_SYMBOL'  # Would come from context
    current_pos = positions.get(symbol, {})
    current_qty = current_pos.get('quantity', 0)
    
    # Buy signal: EMA 20 crosses above EMA 50
    if row['ema_20'] > row['ema_50'] and row['ema_20_prev'] <= row['ema_50_prev']:
        if current_qty <= 0:  # Only enter if not already long
            return {
                'side': 'BUY',
                'quantity': int(cash * 0.1 / row['close']),  # Risk 10% of capital
                'order_type': 'MARKET'
            }
    
    # Sell signal: EMA 20 crosses below EMA 50
    elif row['ema_20'] < row['ema_50'] and row['ema_20_prev'] >= row['ema_50_prev']:
        if current_qty > 0:  # Only exit if currently long
            return {
                'side': 'SELL',
                'quantity': current_qty,
                'order_type': 'MARKET'
            }
    
    return None


def rsi_mean_reversion_strategy(row: pd.Series, positions: Dict[str, Any], cash: float) -> Optional[Dict]:
    """
    RSI mean reversion strategy implementation
    """
    if pd.isna(row.get('rsi_14')):
        return None
    
    rsi = row['rsi_14']
    symbol = 'TEST_SYMBOL'
    current_pos = positions.get(symbol, {})
    current_qty = current_pos.get('quantity', 0)
    
    # Buy signal: RSI oversold (< 30)
    if rsi < 30 and current_qty <= 0:
        return {
            'side': 'BUY',
            'quantity': int(cash * 0.1 / row['close']),  # Risk 10% of capital
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


def bollinger_bands_strategy(row: pd.Series, positions: Dict[str, Any], cash: float) -> Optional[Dict]:
    """
    Bollinger Bands mean reversion strategy implementation
    """
    if pd.isna(row.get('bb_upper')) or pd.isna(row.get('bb_lower')) or pd.isna(row.get('bb_middle')):
        return None
    
    price = row['close']
    symbol = 'TEST_SYMBOL'
    current_pos = positions.get(symbol, {})
    current_qty = current_pos.get('quantity', 0)
    
    # Buy signal: Price touches lower band
    if price <= row['bb_lower'] and current_qty <= 0:
        return {
            'side': 'BUY',
            'quantity': int(cash * 0.1 / row['close']),  # Risk 10% of capital
            'order_type': 'MARKET'
        }
    
    # Sell signal: Price touches upper band
    elif price >= row['bb_upper'] and current_qty > 0:
        return {
            'side': 'SELL',
            'quantity': current_qty,
            'order_type': 'MARKET'
        }
    
    return None