"""
API endpoints for AI-powered portfolio investment.

Endpoints:
- POST /portfolio/invest          — Invest X amount into AI-optimized portfolio
- GET  /portfolio/{id}/allocations — View current allocations
- POST /portfolio/{id}/rebalance   — Rebalance portfolio
- GET  /portfolio/{id}/rotation-opportunities — Check rotation opportunities
- GET  /portfolio/{id}/performance  — Portfolio performance summary
- GET  /portfolio/ai-scores         — Get AI ensemble scores for symbols
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.portfolio import Portfolio
from app.models.portfolio_allocation import PortfolioAllocation, PortfolioRebalanceEvent
from app.schemas.portfolio_construction import (
    PortfolioInvestmentRequest,
    PortfolioInvestmentResponse,
    AllocationItem,
    BufferComposition,
    RebalanceRequest,
    RebalanceResponse,
    RebalanceOrder,
    RotationOpportunity,
    PortfolioPerformanceResponse,
    InvestmentStrategy,
    RiskProfile,
    RebalanceTrigger,
)
from app.agents.portfolio_agent import portfolio_agent
from app.portfolio_construction.ai_portfolio_builder import ai_portfolio_builder
from app.portfolio_construction.risk_buffer_manager import risk_buffer_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/portfolio-ai", tags=["portfolio-investment"])


@router.post("/invest", response_model=dict)
async def invest_in_portfolio(
    request: PortfolioInvestmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Invest an amount into an AI-optimized portfolio.

    The system will:
    1. Score candidate symbols using AI ensemble (FinBERT + LLM + LSTM + Risk)
    2. Apply Modern Portfolio Theory optimization
    3. Reserve 25% buffer for rotation/risk
    4. Generate allocation plan with execution orders
    """
    # Validate user
    if request.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Cannot invest for other users")

    # Validate or create portfolio
    if request.portfolio_id:
        portfolio = db.query(Portfolio).filter(
            Portfolio.id == request.portfolio_id,
            Portfolio.user_id == request.user_id,
        ).first()
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
    else:
        # Create new portfolio
        portfolio = Portfolio(
            user_id=request.user_id,
            name=request.name,
            cash_balance=request.investment_amount,
            invested_amount=0.0,
        )
        db.add(portfolio)
        db.commit()
        db.refresh(portfolio)

    # Build AI-optimized portfolio
    result = await ai_portfolio_builder.build_portfolio(
        investment_amount=request.investment_amount,
        symbols=request.symbols,
        risk_profile=request.risk_profile,
        strategy_type=request.strategy_type,
        buffer_pct=request.buffer_percentage / 100.0,
        user_id=request.user_id,
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Portfolio construction failed"))

    portfolio_data = result["portfolio"]

    # Persist allocation to database
    allocation = PortfolioAllocation(
        portfolio_id=portfolio.id,
        user_id=request.user_id,
        name=request.name,
        investment_amount=request.investment_amount,
        buffer_percentage=request.buffer_percentage,
        buffer_amount=portfolio_data["buffer_amount"],
        active_allocation=portfolio_data["active_allocation"],
        strategy_type=request.strategy_type.value,
        ai_scores_snapshot=portfolio_data.get("ensemble_scores", {}),
        allocation_map={a["symbol"]: {
            "weight": a["weight"],
            "amount": a["amount"],
            "quantity": a["quantity"],
            "price": a["estimated_price"],
            "ai_score": a["ai_score"],
            "risk_score": a["risk_score"],
            "predicted_return": a["predicted_return"],
            "reason": a["reason"],
        } for a in portfolio_data["allocations"]},
        buffer_composition=portfolio_data["buffer_composition"],
        status="ACTIVE",
        notes=request.notes,
    )
    db.add(allocation)
    db.commit()
    db.refresh(allocation)

    # Update portfolio cash balance
    portfolio.cash_balance = portfolio_data["buffer_amount"]
    portfolio.invested_amount = portfolio_data["active_allocation"]
    db.commit()

    # Build response
    response = {
        "allocation_id": allocation.id,
        "portfolio_id": portfolio.id,
        "user_id": request.user_id,
        "name": request.name,
        "investment_amount": portfolio_data["investment_amount"],
        "buffer_percentage": portfolio_data["buffer_percentage"],
        "buffer_amount": portfolio_data["buffer_amount"],
        "active_allocation": portfolio_data["active_allocation"],
        "strategy_type": portfolio_data["strategy_type"],
        "risk_profile": request.risk_profile.value,
        "allocations": portfolio_data["allocations"],
        "buffer_composition": portfolio_data["buffer_composition"],
        "diversification_metrics": portfolio_data["diversification_metrics"],
        "ensemble_scores": portfolio_data["ensemble_scores"],
        "ensemble_breakdown": portfolio_data.get("ensemble_breakdown", {}),
        "status": "ACTIVE",
        "created_at": allocation.created_at.isoformat(),
        "notes": request.notes,
    }

    logger.info(f"Portfolio investment created: allocation_id={allocation.id}, "
                f"amount=${request.investment_amount}, positions={len(portfolio_data['allocations'])}")

    return {"success": True, "portfolio": response}


@router.get("/{portfolio_id}/allocations", response_model=dict)
async def get_portfolio_allocations(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all AI-managed allocations for a portfolio."""
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    if portfolio.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Access denied")

    allocations = db.query(PortfolioAllocation).filter(
        PortfolioAllocation.portfolio_id == portfolio_id
    ).order_by(PortfolioAllocation.created_at.desc()).all()

    return {
        "success": True,
        "portfolio_id": portfolio_id,
        "allocations": [
            {
                "id": a.id,
                "name": a.name,
                "investment_amount": a.investment_amount,
                "buffer_amount": a.buffer_amount,
                "active_allocation": a.active_allocation,
                "strategy_type": a.strategy_type,
                "status": a.status,
                "total_pnl": a.total_pnl,
                "total_pnl_pct": a.total_pnl_pct,
                "rebalance_count": a.rebalance_count,
                "created_at": a.created_at.isoformat(),
                "allocation_map": a.allocation_map,
            }
            for a in allocations
        ],
    }


@router.post("/{portfolio_id}/rebalance", response_model=dict)
async def rebalance_portfolio(
    portfolio_id: int,
    request: RebalanceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Rebalance an AI-managed portfolio allocation."""
    allocation = db.query(PortfolioAllocation).filter(
        PortfolioAllocation.id == request.allocation_id,
        PortfolioAllocation.portfolio_id == portfolio_id,
    ).first()
    if not allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")
    if allocation.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Access denied")

    # Get current positions from allocation_map
    current_positions = allocation.allocation_map or {}
    buffer_amount = allocation.buffer_amount
    total_value = allocation.active_allocation + buffer_amount

    # Run rebalance
    rebalance_result = await portfolio_agent.apply_rebalance(
        current_positions=current_positions,
        buffer_amount=buffer_amount,
        total_value=total_value,
        specific_trigger=request.trigger.value,
    )

    # Persist rebalance event
    rebalance_event = PortfolioRebalanceEvent(
        allocation_id=allocation.id,
        trigger=request.trigger.value,
        previous_allocation_map=current_positions,
        previous_buffer_amount=buffer_amount,
        new_allocation_map=rebalance_result.get("rebalance_orders", []),
        new_buffer_amount=rebalance_result.get("new_buffer_amount", buffer_amount),
        rebalance_orders=rebalance_result.get("rebalance_orders", []),
        ai_scores_at_rebalance=rebalance_result.get("ai_scores_at_rebalance", {}),
    )
    db.add(rebalance_event)

    # Update allocation
    allocation.rebalance_count += 1
    allocation.last_rebalance_at = datetime.utcnow()
    allocation.buffer_amount = rebalance_result.get("new_buffer_amount", buffer_amount)
    db.commit()

    return {
        "success": True,
        "rebalance": rebalance_result,
    }


@router.get("/{portfolio_id}/rotation-opportunities", response_model=dict)
async def get_rotation_opportunities(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check for AI-detected rotation opportunities in a portfolio."""
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    if portfolio.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Access denied")

    # Get latest active allocation
    allocation = db.query(PortfolioAllocation).filter(
        PortfolioAllocation.portfolio_id == portfolio_id,
        PortfolioAllocation.status == "ACTIVE",
    ).order_by(PortfolioAllocation.created_at.desc()).first()

    if not allocation:
        return {"success": True, "opportunities": [], "message": "No active allocations"}

    current_positions = allocation.allocation_map or {}
    buffer_amount = allocation.buffer_amount
    total_value = allocation.active_allocation + buffer_amount

    opportunities = await risk_buffer_manager.detect_rotation_opportunities(
        active_positions=current_positions,
        buffer_amount=buffer_amount,
    )

    return {
        "success": True,
        "allocation_id": allocation.id,
        "buffer_status": risk_buffer_manager.get_buffer_status(
            buffer_amount=buffer_amount,
            total_investment=total_value,
            active_positions=current_positions,
        ),
        "opportunities": [o.model_dump() for o in opportunities],
    }


@router.get("/{portfolio_id}/performance", response_model=dict)
async def get_portfolio_performance(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get performance summary of an AI-managed portfolio."""
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    if portfolio.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Access denied")

    allocations = db.query(PortfolioAllocation).filter(
        PortfolioAllocation.portfolio_id == portfolio_id,
        PortfolioAllocation.status == "ACTIVE",
    ).all()

    if not allocations:
        return {"success": True, "message": "No active allocations", "performance": None}

    # Aggregate performance across all active allocations
    total_invested = sum(a.investment_amount for a in allocations)
    total_buffer = sum(a.buffer_amount for a in allocations)
    total_pnl = sum(a.total_pnl for a in allocations)
    total_current = total_invested + total_pnl

    # Find best/worst performers from allocation maps
    all_positions = []
    for a in allocations:
        if a.allocation_map:
            for symbol, data in a.allocation_map.items():
                all_positions.append({
                    "symbol": symbol,
                    "amount": data.get("amount", 0),
                    "ai_score": data.get("ai_score", 0),
                    "predicted_return": data.get("predicted_return", 0),
                })

    best = max(all_positions, key=lambda x: x["predicted_return"]) if all_positions else None
    worst = min(all_positions, key=lambda x: x["predicted_return"]) if all_positions else None

    return {
        "success": True,
        "performance": {
            "total_invested": total_invested,
            "current_value": total_current,
            "total_pnl": total_pnl,
            "total_pnl_pct": round((total_pnl / total_invested * 100), 2) if total_invested > 0 else 0,
            "buffer_remaining": total_buffer,
            "active_allocations_count": len(allocations),
            "total_rebalances": sum(a.rebalance_count for a in allocations),
            "best_performer": best,
            "worst_performer": worst,
        },
    }


@router.get("/ai-scores", response_model=dict)
async def get_ai_scores(
    symbols: str = Query(..., description="Comma-separated list of symbols"),
    risk_profile: str = Query("MODERATE", description="Risk profile: CONSERVATIVE, MODERATE, AGGRESSIVE"),
    current_user: User = Depends(get_current_user),
):
    """
    Get AI ensemble scores for a list of symbols without building a portfolio.
    Useful for previewing which stocks the AI favors.
    """
    symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
    if not symbol_list:
        raise HTTPException(status_code=400, detail="No symbols provided")

    try:
        profile = RiskProfile(risk_profile.upper())
    except (ValueError, AttributeError):
        profile = RiskProfile.MODERATE

    scores = await ai_portfolio_builder.compute_scores_for_symbols(symbol_list, profile)

    return {
        "success": True,
        "risk_profile": profile.value,
        "scores": {
            symbol: {
                "final_score": round(data.get("final_score", 0), 4),
                "sentiment_score": round(data.get("sentiment_score", 0), 4),
                "llm_score": round(data.get("llm_score", 0), 4),
                "lstm_prediction": round(data.get("lstm_prediction", 0), 4),
                "lstm_confidence": round(data.get("lstm_confidence", 0), 4),
                "risk_score": round(data.get("risk_score", 0), 4),
                "reason": data.get("reason", ""),
            }
            for symbol, data in scores.items()
        },
    }
