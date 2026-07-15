"""
Pydantic schemas for AI-powered portfolio construction and investment.
"""
from enum import Enum
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Dict, List, Optional, Any


class InvestmentStrategy(str, Enum):
    AI_HYBRID = "AI_HYBRID"
    MARKOWITZ = "MARKOWITZ"
    AI_ONLY = "AI_ONLY"
    MPT_ONLY = "MPT_ONLY"


class RiskProfile(str, Enum):
    CONSERVATIVE = "CONSERVATIVE"
    MODERATE = "MODERATE"
    AGGRESSIVE = "AGGRESSIVE"


class RebalanceTrigger(str, Enum):
    MANUAL = "MANUAL"
    AI_SIGNAL_CHANGE = "AI_SIGNAL_CHANGE"
    SCHEDULED = "SCHEDULED"
    THRESHOLD_BREACH = "THRESHOLD_BREACH"


class PortfolioInvestmentRequest(BaseModel):
    """Request to invest an amount into an AI-optimized portfolio."""
    user_id: int
    portfolio_id: Optional[int] = Field(None, description="Existing portfolio ID. If None, creates new portfolio.")
    investment_amount: float = Field(..., gt=0, description="Total amount to invest")
    symbols: Optional[List[str]] = Field(None, description="Candidates to consider. If None, system selects automatically.")
    buffer_percentage: float = Field(25.0, ge=0, le=50, description="Percentage reserved as buffer (default 25%)")
    strategy_type: InvestmentStrategy = Field(InvestmentStrategy.AI_HYBRID)
    risk_profile: RiskProfile = Field(RiskProfile.MODERATE)
    name: str = Field("AI Portfolio", description="Portfolio name")
    notes: Optional[str] = None


class AllocationItem(BaseModel):
    """A single symbol's allocation in the portfolio."""
    symbol: str
    weight: float = Field(..., ge=0, le=1, description="Allocation weight (0-1)")
    amount: float = Field(..., ge=0, description="Amount allocated")
    quantity: float = Field(0, description="Number of units/shares")
    estimated_price: float = Field(0, description="Estimated price per unit at allocation time")
    ai_score: float = Field(0, description="AI ensemble score at allocation time")
    risk_score: float = Field(0, description="Risk score (0=low, 100=high)")
    reason: str = Field("", description="AI reasoning for this allocation")
    predicted_return: float = Field(0, description="Expected return prediction")


class BufferComposition(BaseModel):
    """Breakdown of the 25% buffer."""
    rotation_reserve: float = Field(0.15, description="% held for rotation opportunities")
    risk_hedge: float = Field(0.10, description="% held as risk hedge")
    total_buffer_pct: float = Field(0.25)
    total_buffer_amount: float = Field(0)


class PortfolioInvestmentResponse(BaseModel):
    """Response after AI constructs the portfolio."""
    allocation_id: int
    portfolio_id: int
    user_id: int
    name: str
    investment_amount: float
    buffer_percentage: float
    buffer_amount: float
    active_allocation: float
    strategy_type: str
    risk_profile: str
    allocations: List[AllocationItem]
    buffer_composition: BufferComposition
    diversification_metrics: Dict[str, Any] = Field(default_factory=dict)
    ensemble_scores: Dict[str, float] = Field(default_factory=dict)
    status: str = "ACTIVE"
    created_at: datetime
    notes: Optional[str] = None


class RebalanceRequest(BaseModel):
    """Request to rebalance an existing portfolio allocation."""
    allocation_id: int
    trigger: RebalanceTrigger = RebalanceTrigger.MANUAL
    symbols_to_add: Optional[List[str]] = None
    symbols_to_remove: Optional[List[str]] = None
    new_buffer_percentage: Optional[float] = None
    force_rebalance: bool = Field(False, description="Force rebalance even if thresholds not met")


class RebalanceOrder(BaseModel):
    """A single order generated during rebalance."""
    symbol: str
    action: str = Field(..., pattern="^(BUY|SELL|HOLD)$")
    quantity: float = 0
    estimated_price: float = 0
    estimated_total: float = 0
    reason: str = ""
    source: str = "ACTIVE_PORTFOLIO"  # ACTIVE_PORTFOLIO, BUFFER


class RebalanceResponse(BaseModel):
    """Response after rebalancing."""
    allocation_id: int
    trigger: str
    previous_buffer_amount: float
    new_buffer_amount: float
    rebalance_orders: List[RebalanceOrder]
    ai_scores_at_rebalance: Dict[str, float]
    created_at: datetime


class RotationOpportunity(BaseModel):
    """A potential rotation opportunity detected by AI."""
    symbol: str
    current_ai_score: float
    score_delta: float = Field(..., description="Change from previous score")
    reason: str
    estimated_entry_price: float
    rotation_type: str = "BUFFER_TO_ACTIVE"  # BUFFER_TO_ACTIVE, ACTIVE_TO_BUFFER, ACTIVE_TO_SELL
    confidence: float = Field(..., ge=0, le=1)


class PortfolioPerformanceResponse(BaseModel):
    """Performance summary of an AI-managed portfolio."""
    allocation_id: int
    total_invested: float
    current_value: float
    total_pnl: float
    total_pnl_pct: float
    buffer_remaining: float
    rebalance_count: int
    best_performer: Optional[AllocationItem] = None
    worst_performer: Optional[AllocationItem] = None
    status: str
    last_rebalance_at: Optional[datetime] = None
    created_at: datetime
