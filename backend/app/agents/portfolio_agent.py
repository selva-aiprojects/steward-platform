"""
PortfolioAgent — Handles multi-asset portfolio investment.

This agent is a NEW high-level agent that integrates into the existing orchestrator
pipeline. It replaces the single-trade TradeDecisionAgent when the request is
a portfolio investment (investment_amount present in context).

Flow:
1. Receives investment request with amount and optional symbols
2. Uses AIPortfolioBuilder to construct AI-optimized portfolio
3. Applies 25% buffer (via RiskBufferManager)
4. Generates multiple execution orders (one per symbol)
5. Passes each order through the existing risk → execution pipeline

The agent maintains the existing safety gates (risk check, approval, execution mode)
while extending the system from single-trade to multi-asset portfolio capability.
"""
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from app.agents.base import BaseAgent
from app.portfolio_construction.ai_portfolio_builder import ai_portfolio_builder
from app.portfolio_construction.risk_buffer_manager import risk_buffer_manager
from app.schemas.portfolio_construction import (
    InvestmentStrategy, RiskProfile, PortfolioInvestmentResponse, AllocationItem,
    RebalanceOrder, RebalanceTrigger, RotationOpportunity,
)

logger = logging.getLogger(__name__)


class PortfolioAgent(BaseAgent):
    """
    Portfolio-level investment agent.

    Responsibilities:
    - Handle portfolio investment requests (invest X amount across multiple stocks)
    - Use AI ensemble (FinBERT + LLM + LSTM + Risk) to score candidates
    - Apply Modern Portfolio Theory optimization
    - Manage the 25% buffer for rotation/risk
    - Generate multi-order execution plans
    - Monitor portfolio performance and detect rotation opportunities
    """

    def __init__(self):
        super().__init__(name="PortfolioAgent")
        logger.info("PortfolioAgent initialized")

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point. Detects if this is a portfolio or single-trade request.

        Returns:
            If portfolio: {"execution_plan": [orders], "portfolio_info": {...}}
            If single trade: delegates to existing TradeDecisionAgent logic
        """
        # Detect portfolio mode
        investment_amount = context.get("investment_amount")
        if not investment_amount:
            # Not a portfolio request — signal orchestrator to use normal flow
            return {"portfolio_mode": False}

        logger.info(f"PortfolioAgent: Building portfolio for amount ${investment_amount}")

        # Extract parameters from context
        symbols = context.get("symbols")
        risk_profile_str = context.get("risk_profile", "MODERATE")
        strategy_type_str = context.get("strategy_type", "AI_HYBRID")
        buffer_pct = context.get("buffer_percentage", 25.0) / 100.0
        user_id = context.get("user_id")

        # Map strings to enums
        try:
            risk_profile = RiskProfile(risk_profile_str.upper())
        except (ValueError, AttributeError):
            risk_profile = RiskProfile.MODERATE

        try:
            strategy_type = InvestmentStrategy(strategy_type_str.upper())
        except (ValueError, AttributeError):
            strategy_type = InvestmentStrategy.AI_HYBRID

        # Build AI-optimized portfolio
        result = await ai_portfolio_builder.build_portfolio(
            investment_amount=investment_amount,
            symbols=symbols,
            risk_profile=risk_profile,
            strategy_type=strategy_type,
            buffer_pct=buffer_pct,
            user_id=user_id,
        )

        if not result.get("success"):
            logger.error(f"Portfolio building failed: {result.get('error')}")
            return {
                "portfolio_mode": True,
                "success": False,
                "error": result.get("error", "Portfolio construction failed"),
            }

        portfolio = result["portfolio"]

        # Generate execution orders for each allocation
        execution_orders = []
        for alloc in portfolio["allocations"]:
            order = {
                "action": "BUY",
                "symbol": alloc["symbol"],
                "quantity": alloc["quantity"],
                "price": alloc["estimated_price"],
                "estimated_total": alloc["amount"],
                "ai_score": alloc["ai_score"],
                "risk_score": alloc["risk_score"],
                "predicted_return": alloc["predicted_return"],
                "source": "PORTFOLIO_ALLOCATION",
            }
            if order["quantity"] > 0:
                execution_orders.append(order)

        # Buffer management
        buffer_info = risk_buffer_manager.get_buffer_status(
            buffer_amount=portfolio["buffer_amount"],
            total_investment=portfolio["investment_amount"],
            active_positions={a["symbol"]: a for a in portfolio["allocations"]},
        )

        logger.info(f"PortfolioAgent: Generated {len(execution_orders)} orders, "
                    f"buffer: ${portfolio['buffer_amount']:.2f} ({buffer_info['health']})")

        return {
            "portfolio_mode": True,
            "success": True,
            "execution_plan": {
                "orders": execution_orders,
                "total_active": portfolio["active_allocation"],
                "total_buffer": portfolio["buffer_amount"],
                "total_investment": portfolio["investment_amount"],
            },
            "portfolio_info": portfolio,
            "buffer_info": buffer_info,
        }

    # ======================================================================
    # POST-CREATION MANAGEMENT
    # ======================================================================

    async def check_rotation_opportunities(
        self,
        allocation_id: int,
        current_positions: Dict[str, Dict],
        buffer_amount: float,
        total_value: float,
    ) -> Dict[str, Any]:
        """
        Check if AI scores have changed enough to trigger rotation trades.
        Called periodically by a scheduler or on demand.
        """
        opportunities = await risk_buffer_manager.detect_rotation_opportunities(
            active_positions=current_positions,
            buffer_amount=buffer_amount,
        )

        if opportunities:
            orders, new_buffer = await risk_buffer_manager.generate_rebalance_plan(
                active_positions=current_positions,
                buffer_amount=buffer_amount,
                total_portfolio_value=total_value,
                opportunities=opportunities,
            )

            return {
                "has_opportunities": True,
                "opportunities_count": len(opportunities),
                "recommended_orders": len(orders),
                "orders": [o.model_dump() for o in orders],
                "new_buffer_amount": new_buffer,
            }

        return {"has_opportunities": False, "opportunities_count": 0, "orders": []}

    async def apply_rebalance(
        self,
        current_positions: Dict[str, Dict],
        buffer_amount: float,
        total_value: float,
        specific_trigger: str = "MANUAL",
    ) -> Dict[str, Any]:
        """
        Force rebalance the portfolio based on current market conditions.
        This is the full rebalance path.
        """
        # 1. Get fresh AI scores
        symbols = list(current_positions.keys())
        fresh_scores = await ai_portfolio_builder.compute_scores_for_symbols(symbols)

        # 2. Detect opportunities
        opportunities = await risk_buffer_manager.detect_rotation_opportunities(
            active_positions=current_positions,
            buffer_amount=buffer_amount,
        )

        # 3. Generate orders
        orders, new_buffer = await risk_buffer_manager.generate_rebalance_plan(
            active_positions=current_positions,
            buffer_amount=buffer_amount,
            total_portfolio_value=total_value,
            opportunities=opportunities,
            max_rotation_trades=5,
        )

        return {
            "trigger": specific_trigger,
            "rebalance_orders": [o.model_dump() for o in orders],
            "previous_buffer_amount": buffer_amount,
            "new_buffer_amount": new_buffer,
            "ai_scores_at_rebalance": {
                s: fresh_scores.get(s, {}).get("final_score", 0) for s in symbols
            },
            "opportunities_detected": len(opportunities),
        }


# Singleton instance
portfolio_agent = PortfolioAgent()
