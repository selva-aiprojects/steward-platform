"""
Risk Buffer Manager — handles the 25% buffer for rotation and risk management.

Buffer Composition:
- 60% of buffer → Rotation Reserve (for opportunistic trades)
- 40% of buffer → Risk Hedge (emergency protection)

Rotation Logic:
- Monitor AI scores continuously
- If a new symbol's score exceeds a current holding's score by threshold → rotate
- If an existing holding's score drops below threshold → trim and move to buffer

The buffer is the key differentiator — it allows the portfolio to:
1. Seize AI-detected opportunities without selling core holdings
2. Absorb drawdowns without forced liquidation
3. Maintain dry powder for market dips
"""
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import numpy as np

from app.schemas.portfolio_construction import (
    RotationOpportunity, RebalanceOrder, RiskProfile,
)
from app.portfolio_construction.ai_portfolio_builder import (
    ai_portfolio_builder,
    REBALANCE_AI_SCORE_DELTA_THRESHOLD,
    MIN_AI_SCORE_TO_INCLUDE,
)

logger = logging.getLogger(__name__)


class RiskBufferManager:
    """
    Manages the 25% buffer for a portfolio allocation.

    Tracks buffer usage, detects rotation opportunities, and generates
    rebalance orders when AI scores change significantly.
    """

    def __init__(self):
        logger.info("RiskBufferManager initialized")

    # ======================================================================
    # ROTATION OPPORTUNITY DETECTION
    # ======================================================================

    async def detect_rotation_opportunities(
        self,
        active_positions: Dict[str, Dict],   # symbol -> {weight, amount, quantity, ai_score, ...}
        buffer_amount: float,
        candidate_symbols: Optional[List[str]] = None,
    ) -> List[RotationOpportunity]:
        """
        Detect rotation opportunities by comparing current AI scores vs. holding scores.

        Returns sorted list of RotationOpportunity (highest confidence first).
        """
        if not active_positions:
            return []

        # Get current AI scores for all active symbols + candidates
        all_symbols = list(active_positions.keys())
        if candidate_symbols:
            all_symbols = list(set(all_symbols + candidate_symbols))

        current_scores = await ai_portfolio_builder.compute_scores_for_symbols(all_symbols)
        if not current_scores:
            return []

        opportunities = []

        # Check each potential rotation target
        active_symbols = list(active_positions.keys())

        for symbol, score_data in current_scores.items():
            current_score = score_data.get("final_score", 0)
            prev_score = active_positions.get(symbol, {}).get("ai_score", 0)
            score_delta = current_score - prev_score

            if symbol in active_positions:
                # Existing holding — check if score dropped significantly
                if score_delta < -REBALANCE_AI_SCORE_DELTA_THRESHOLD:
                    opportunities.append(RotationOpportunity(
                        symbol=symbol,
                        current_ai_score=current_score,
                        score_delta=score_delta,
                        reason=f"AI score dropped from {prev_score:.3f} to {current_score:.3f} "
                               f"(delta: {score_delta:.3f})",
                        estimated_entry_price=active_positions[symbol].get("price", 0),
                        rotation_type="ACTIVE_TO_BUFFER",
                        confidence=min(0.95, abs(score_delta) * 2),
                    ))
            else:
                # Candidate — check if it's significantly better than any existing holding
                for active_sym in active_symbols:
                    active_score = active_positions[active_sym].get("ai_score", 0)
                    if current_score > active_score + REBALANCE_AI_SCORE_DELTA_THRESHOLD:
                        opportunities.append(RotationOpportunity(
                            symbol=symbol,
                            current_ai_score=current_score,
                            score_delta=score_delta,
                            reason=f"Score {current_score:.3f} exceeds {active_sym}'s {active_score:.3f} "
                                   f"by {current_score - active_score:.3f}",
                            estimated_entry_price=active_positions[symbol].get("price", 0)
                            if symbol in active_positions else 100,
                            rotation_type="BUFFER_TO_ACTIVE",
                            confidence=min(0.95, (current_score - active_score) * 2),
                        ))
                        break  # One reason per candidate is enough

        # Sort by confidence descending
        opportunities.sort(key=lambda x: x.confidence, reverse=True)
        return opportunities

    # ======================================================================
    # REBALANCE PLAN GENERATION
    # ======================================================================

    async def generate_rebalance_plan(
        self,
        active_positions: Dict[str, Dict],
        buffer_amount: float,
        total_portfolio_value: float,
        opportunities: List[RotationOpportunity],
        max_rotation_trades: int = 3,
    ) -> Tuple[List[RebalanceOrder], float]:
        """
        Generate rebalance orders based on detected rotation opportunities.

        Args:
            active_positions: Current active positions
            buffer_amount: Current available buffer cash
            total_portfolio_value: Total portfolio value (active + buffer)
            opportunities: Detected rotation opportunities (sorted by confidence)
            max_rotation_trades: Max number of rotation trades to execute

        Returns:
            (list of RebalanceOrder, new_buffer_amount)
        """
        orders = []
        new_buffer = buffer_amount

        if not opportunities:
            return orders, new_buffer

        # Process top opportunities
        for opp in opportunities[:max_rotation_trades]:
            if opp.rotation_type == "ACTIVE_TO_BUFFER":
                # Trim or sell an existing position that lost AI favor
                position = active_positions.get(opp.symbol)
                if not position:
                    continue

                # Sell a portion (e.g., 50% of the position) into buffer
                sell_quantity = int(position.get("quantity", 0) * 0.5)
                if sell_quantity <= 0:
                    continue

                estimated_total = sell_quantity * position.get("price", 0)
                new_buffer += estimated_total

                orders.append(RebalanceOrder(
                    symbol=opp.symbol,
                    action="SELL",
                    quantity=sell_quantity,
                    estimated_price=position.get("price", 0),
                    estimated_total=estimated_total,
                    reason=opp.reason,
                    source="ACTIVE_PORTFOLIO",
                ))
                logger.info(f"Rotation SELL: {opp.symbol} x {sell_quantity} (${estimated_total:.2f})")

            elif opp.rotation_type == "BUFFER_TO_ACTIVE":
                # Buy a new symbol using buffer cash
                if new_buffer <= 0:
                    continue

                # Allocate up to 30% of buffer to this opportunity
                max_buy_amount = min(
                    new_buffer * 0.3,
                    total_portfolio_value * 0.05  # Max 5% of total portfolio for one rotation
                )
                if max_buy_amount < 100:  # Skip if too small
                    continue

                price = opp.estimated_entry_price or 100
                buy_quantity = int(max_buy_amount / price)
                if buy_quantity <= 0:
                    continue

                actual_cost = buy_quantity * price
                new_buffer -= actual_cost

                orders.append(RebalanceOrder(
                    symbol=opp.symbol,
                    action="BUY",
                    quantity=buy_quantity,
                    estimated_price=price,
                    estimated_total=actual_cost,
                    reason=opp.reason,
                    source="BUFFER",
                ))
                logger.info(f"Rotation BUY: {opp.symbol} x {buy_quantity} (${actual_cost:.2f})")

        return orders, max(0, new_buffer)

    # ======================================================================
    # BUFFER STATUS
    # ======================================================================

    def get_buffer_status(
        self,
        buffer_amount: float,
        total_investment: float,
        active_positions: Dict[str, Dict],
    ) -> Dict[str, Any]:
        """
        Get current buffer status and health metrics.
        """
        buffer_pct = (buffer_amount / total_investment * 100) if total_investment > 0 else 0
        target_buffer = 0.25 * total_investment

        # Compute buffer health
        if buffer_amount >= target_buffer:
            health = "HEALTHY"
        elif buffer_amount >= target_buffer * 0.5:
            health = "ADEQUATE"
        else:
            health = "DEPLETED"

        # Compute how many rotations the buffer can support
        avg_position_value = (total_investment - buffer_amount) / max(len(active_positions), 1)
        rotation_capacity = int(buffer_amount / max(avg_position_value * 0.3, 100))

        return {
            "buffer_amount": round(buffer_amount, 2),
            "buffer_pct_of_total": round(buffer_pct, 2),
            "target_buffer_amount": round(target_buffer, 2),
            "buffer_vs_target": round(buffer_amount - target_buffer, 2),
            "health": health,
            "rotation_capacity": max(rotation_capacity, 0),
            "total_investment": round(total_investment, 2),
            "active_positions_count": len(active_positions),
        }

    def get_rotation_reserve(self, buffer_amount: float) -> float:
        """60% of buffer is available for rotation."""
        return buffer_amount * 0.6

    def get_risk_hedge(self, buffer_amount: float) -> float:
        """40% of buffer is reserved as risk hedge."""
        return buffer_amount * 0.4


# Singleton instance
risk_buffer_manager = RiskBufferManager()
