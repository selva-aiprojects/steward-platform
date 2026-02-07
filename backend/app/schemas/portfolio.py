"""
Pydantic schemas for portfolio optimization functionality
"""
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, List, Optional


class OptimizationMethod(str, Enum):
    MARKOWITZ = "markowitz"
    RISK_PARITY = "risk_parity"
    MINIMUM_VARIANCE = "minimum_variance"
    MAXIMUM_SHARPE = "maximum_sharpe"
    EQUAL_WEIGHT = "equal_weight"
    CUSTOM = "custom"


class ObjectiveMetric(str, Enum):
    SHARPE_RATIO = "sharpe_ratio"
    MINIMUM_VARIANCE = "minimum_variance"
    MAXIMUM_RETURN = "maximum_return"
    RISK_PARITY = "risk_parity"


class PortfolioOptimizationRequest(BaseModel):
    """
    Request schema for portfolio optimization
    """
    symbols: List[str] = Field(..., description="List of symbols to include in optimization")
    start_date: datetime = Field(..., description="Start date for historical data")
    end_date: datetime = Field(..., description="End date for historical data")
    optimization_method: OptimizationMethod = Field(OptimizationMethod.MARKOWITZ, 
                                                   description="Optimization method to use")
    objective_metric: ObjectiveMetric = Field(ObjectiveMetric.SHARPE_RATIO, 
                                              description="Objective metric to optimize for")
    constraints: Optional[Dict[str, float]] = Field(None, description="Constraints for optimization")
    risk_free_rate: float = Field(0.02, description="Risk-free rate for Sharpe ratio calculation")


class PortfolioOptimizationResponse(BaseModel):
    """
    Response schema for portfolio optimization
    """
    optimized_weights: Dict[str, float] = Field(..., description="Optimized allocation weights for each symbol")
    expected_return: float = Field(..., description="Expected annual return of optimized portfolio")
    volatility: float = Field(..., description="Annual volatility of optimized portfolio")
    sharpe_ratio: float = Field(..., description="Sharpe ratio of optimized portfolio")
    optimization_method: str = Field(..., description="Method used for optimization")
    execution_time: float = Field(..., description="Time taken for optimization in seconds")