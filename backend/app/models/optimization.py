from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class PortfolioOptimizationResult(Base):
    __tablename__ = "portfolio_optimization_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    strategy_name = Column(String, index=True)
    symbol = Column(String, index=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    optimization_method = Column(String)
    objective_metric = Column(String)
    best_parameters = Column(JSON)  # Store as JSON object
    best_score = Column(Float)
    execution_time = Column(Float)  # Time taken in seconds
    status = Column(String, default="COMPLETED")  # COMPLETED, FAILED, PENDING
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="optimization_results")


class StrategyOptimizationResult(Base):
    __tablename__ = "strategy_optimization_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    strategy_name = Column(String, index=True)
    symbol = Column(String, index=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    parameter_space = Column(JSON)  # Store as JSON object
    best_parameters = Column(JSON)  # Store as JSON object
    best_score = Column(Float)
    optimization_trace = Column(JSON)  # Store as JSON array
    execution_time = Column(Float)  # Time taken in seconds
    status = Column(String, default="COMPLETED")  # COMPLETED, FAILED, PENDING
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="strategy_optimization_results")