"""
Backtesting package initialization
"""
from .engine import BacktestingEngine, sma_crossover_strategy

__all__ = ["BacktestingEngine", "sma_crossover_strategy"]