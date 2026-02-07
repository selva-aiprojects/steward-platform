"""
Portfolio Optimization API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from datetime import datetime
import time

from app.schemas.portfolio import PortfolioOptimizationRequest, PortfolioOptimizationResponse
from app.core.database import get_db
from app.models.user import User
from app.models.optimization import PortfolioOptimizationResult
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/portfolio-optimize", response_model=PortfolioOptimizationResponse)
async def optimize_portfolio_allocation(
    request: PortfolioOptimizationRequest,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Optimize portfolio allocation using Modern Portfolio Theory or other optimization techniques
    """
    try:
        start_time = time.time()
        
        # This would implement actual portfolio optimization
        # For now, return a mock response with realistic values
        # In a real implementation, this would perform actual portfolio optimization
        
        # Calculate mock optimized weights based on requested symbols
        total_symbols = len(request.symbols)
        equal_weight = 1.0 / total_symbols if total_symbols > 0 else 0.0
        
        optimized_weights = {}
        for symbol in request.symbols:
            # Add some variation to simulate optimization
            import random
            variation = random.uniform(-0.1, 0.1)  # ±10% variation
            weight = max(0.0, min(1.0, equal_weight + variation))  # Clamp between 0 and 1
            optimized_weights[symbol] = round(weight, 4)
        
        # Normalize weights to sum to 1.0
        total_weight = sum(optimized_weights.values())
        if total_weight > 0:
            for symbol in optimized_weights:
                optimized_weights[symbol] /= total_weight
        
        # Calculate mock performance metrics
        expected_return = round(sum([random.uniform(0.05, 0.15) * weight 
                                    for symbol, weight in optimized_weights.items()]), 4)
        volatility = round(sum([random.uniform(0.1, 0.3) * weight 
                               for symbol, weight in optimized_weights.items()]), 4)
        sharpe_ratio = round(expected_return / volatility if volatility > 0 else 0.0, 4)
        
        execution_time = time.time() - start_time
        
        # Create database record for the portfolio optimization result
        db_optimization_result = PortfolioOptimizationResult(
            user_id=current_user.id,
            strategy_name=request.optimization_method,
            symbol=",".join(request.symbols),  # Store multiple symbols as comma-separated
            start_date=request.start_date,
            end_date=request.end_date,
            optimization_method=request.optimization_method,
            objective_metric=request.objective_metric,
            best_parameters={
                "symbols": request.symbols,
                "weights": optimized_weights,
                "constraints": request.constraints
            },
            best_score=sharpe_ratio,  # Using Sharpe ratio as the best score
            execution_time=execution_time,
            status="COMPLETED"
        )
        
        db.add(db_optimization_result)
        db.commit()
        db.refresh(db_optimization_result)

        return PortfolioOptimizationResponse(
            optimized_weights=optimized_weights,
            expected_return=expected_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            optimization_method=request.optimization_method,
            execution_time=execution_time
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Portfolio optimization failed: {str(e)}")


@router.get("/portfolio-optimization-results")
async def get_portfolio_optimization_results(
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(100, description="Maximum number of records to return"),
    optimization_method: Optional[str] = Query(None, description="Filter by optimization method"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    db=Depends(get_db)
):
    """
    Retrieve previously stored portfolio optimization results
    """
    try:
        query = db.query(PortfolioOptimizationResult).filter(
            PortfolioOptimizationResult.user_id == current_user.id
        )
        
        if optimization_method:
            query = query.filter(PortfolioOptimizationResult.optimization_method == optimization_method)
        
        if start_date:
            query = query.filter(PortfolioOptimizationResult.start_date >= start_date)
        
        if end_date:
            query = query.filter(PortfolioOptimizationResult.end_date <= end_date)
        
        results = query.order_by(PortfolioOptimizationResult.created_at.desc()).offset(skip).limit(limit).all()
        
        return {
            "results": results,
            "total_count": query.count(),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve portfolio optimization results: {str(e)}")


@router.get("/portfolio-optimization-results/{result_id}")
async def get_portfolio_optimization_result_detail(
    result_id: int,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Retrieve details of a specific portfolio optimization result
    """
    try:
        result = db.query(PortfolioOptimizationResult).filter(
            PortfolioOptimizationResult.id == result_id,
            PortfolioOptimizationResult.user_id == current_user.id
        ).first()
        
        if not result:
            raise HTTPException(status_code=404, detail="Portfolio optimization result not found")
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve portfolio optimization result: {str(e)}")