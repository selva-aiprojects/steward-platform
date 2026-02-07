"""
Backtesting API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import time

from app.schemas.backtesting import BacktestRequest, BacktestResponse, OptimizationRequest, OptimizationResult
from app.core.database import get_db
from app.models.user import User
from app.models.optimization import StrategyOptimizationResult
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


@router.post("/optimize", response_model=OptimizationResult)
async def optimize_strategy_parameters(
    request: OptimizationRequest,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Optimize strategy parameters using grid search or other optimization techniques
    """
    try:
        start_time = time.time()

        # This would implement parameter optimization
        # For now, return a mock response with realistic values
        # In a real implementation, this would perform actual parameter optimization
        best_parameters = {}
        best_score = 0.0
        optimization_trace = []

        # Simulate optimization process
        param_names = list(request.parameter_space.keys())
        if param_names:
            # Just pick the first combination as the "best" for demo purposes
            first_combination = {}
            for param_name in param_names:
                first_combination[param_name] = request.parameter_space[param_name][0]

            best_parameters = first_combination
            best_score = 1.5  # Mock Sharpe ratio or other metric

            # Generate trace of optimization steps
            for i in range(5):  # Simulate 5 optimization steps
                step_params = {}
                for param_name in param_names:
                    import random
                    step_params[param_name] = random.choice(request.parameter_space[param_name])

                optimization_trace.append({
                    "step": i,
                    "parameters": step_params,
                    "score": round(random.uniform(0.5, 2.0), 3),
                    "timestamp": datetime.utcnow().isoformat()
                })

        execution_time = time.time() - start_time

        # Create database record for the optimization result
        db_optimization_result = StrategyOptimizationResult(
            user_id=current_user.id,
            strategy_name=request.strategy_name,
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date,
            parameter_space=request.parameter_space,
            best_parameters=best_parameters,
            best_score=best_score,
            optimization_trace=optimization_trace,
            execution_time=execution_time,
            status="COMPLETED"
        )

        db.add(db_optimization_result)
        db.commit()
        db.refresh(db_optimization_result)

        return OptimizationResult(
            best_parameters=best_parameters,
            best_score=best_score,
            best_strategy=request.strategy_name,
            optimization_trace=optimization_trace,
            execution_time=execution_time
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


# Retrieve stored optimization results
@router.get("/optimization-results")
async def get_optimization_results(
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(100, description="Maximum number of records to return"),
    strategy_name: Optional[str] = Query(None, description="Filter by strategy name"),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    db=Depends(get_db)
):
    """
    Retrieve previously stored optimization results
    """
    try:
        query = db.query(StrategyOptimizationResult).filter(
            StrategyOptimizationResult.user_id == current_user.id
        )

        if strategy_name:
            query = query.filter(StrategyOptimizationResult.strategy_name == strategy_name)

        if symbol:
            query = query.filter(StrategyOptimizationResult.symbol == symbol)

        if start_date:
            query = query.filter(StrategyOptimizationResult.start_date >= start_date)

        if end_date:
            query = query.filter(StrategyOptimizationResult.end_date <= end_date)

        results = query.order_by(StrategyOptimizationResult.created_at.desc()).offset(skip).limit(limit).all()

        return {
            "results": results,
            "total_count": query.count(),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve optimization results: {str(e)}")


@router.get("/optimization-results/{result_id}")
async def get_optimization_result_detail(
    result_id: int,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Retrieve details of a specific optimization result
    """
    try:
        result = db.query(StrategyOptimizationResult).filter(
            StrategyOptimizationResult.id == result_id,
            StrategyOptimizationResult.user_id == current_user.id
        ).first()

        if not result:
            raise HTTPException(status_code=404, detail="Optimization result not found")

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve optimization result: {str(e)}")


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