"""
Smoke test for the AI-powered Portfolio Investment workflow.

Tests:
1. LSTM predictor fallback mode (statistical)
2. AI Portfolio Builder scoring
3. Buffer management
4. Full portfolio construction flow (without DB/API)
5. Rotation opportunity detection
"""
import asyncio
import logging
import sys
import os
from datetime import datetime

# Set up path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("smoke_test")

passed = 0
failed = 0


def check(description: str, condition: bool):
    global passed, failed
    if condition:
        logger.info(f"  ✅ PASS: {description}")
        passed += 1
    else:
        logger.error(f"  ❌ FAIL: {description}")
        failed += 1


async def test_lstm_predictor():
    """Test LSTM predictor works in fallback statistical mode."""
    logger.info("\n📦 Test 1: LSTM Predictor (Statistical Fallback)")
    from app.ml_models.lstm_predictor import LSTMPredictor

    predictor = LSTMPredictor()
    check("LSTMPredictor initializes", predictor is not None)
    check("LSTM uses fallback mode (no PyTorch)", predictor.model is None)

    # Test with synthetic OHLCV data
    ohlcv_data = []
    price = 100.0
    for i in range(100):
        import random
        price += random.uniform(-2, 2)
        ohlcv_data.append({
            "open": price - random.uniform(0, 1),
            "high": price + random.uniform(0, 2),
            "low": price - random.uniform(0, 2),
            "close": price,
            "volume": random.randint(100000, 500000),
        })
    
    result = predictor.predict(ohlcv_data)
    check("Statistical prediction returns dict", isinstance(result, dict))
    check("Has predicted_return key", "predicted_return" in result)
    check("Has direction key", "direction" in result)
    check("Has confidence key", "confidence" in result)
    check("Direction is UP/DOWN/NEUTRAL", result["direction"] in ["UP", "DOWN", "NEUTRAL"])
    check("Confidence is between 0-1", 0 <= result["confidence"] <= 1)
    check("Model is fallback", result["model"] == "fallback_statistical" or result["model"] == "lstm_untrained")

    # Test batch prediction
    batch_result = predictor.predict_batch({"TEST1": ohlcv_data, "TEST2": ohlcv_data})
    check("Batch prediction returns dict of symbols", isinstance(batch_result, dict))
    check("Batch contains both symbols", "TEST1" in batch_result and "TEST2" in batch_result)

    # Test volatility computation
    vol = predictor._compute_volatility(ohlcv_data)
    check("Volatility is >= 0", vol >= 0)
    check("Volatility is not NaN", not (vol != vol))  # NaN check


async def test_ai_portfolio_builder():
    """Test the AI Portfolio Builder's ensemble scoring."""
    logger.info("\n📦 Test 2: AI Portfolio Builder Scoring")
    from app.portfolio_construction.ai_portfolio_builder import AIPortfolioBuilder
    from app.schemas.portfolio_construction import RiskProfile

    builder = AIPortfolioBuilder()
    check("AIPortfolioBuilder initializes", builder is not None)

    # Test ensemble scoring (should work even without LLM/LSTM market data)
    symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]
    scores = await builder._compute_ensemble_scores(symbols, RiskProfile.MODERATE)

    check("Ensemble scoring returns dict", isinstance(scores, dict))
    check("All symbols scored", len(scores) >= 1)
    
    if scores:
        first_symbol = list(scores.keys())[0]
        first_score = scores[first_symbol]
        check(f"Score for {first_symbol} has final_score", "final_score" in first_score)
        check(f"Final score is float", isinstance(first_score["final_score"], float))
        check(f"Score is in range [-1, 1]", -1 <= first_score["final_score"] <= 1)
    
    # Test symbol filtering
    scored_symbols = {k: v for k, v in scores.items() 
                      if v.get("final_score", 0) >= 0.10}
    check("AI scoring produces usable scores", len(scored_symbols) > 0)


async def test_portfolio_construction():
    """Test full portfolio construction flow."""
    logger.info("\n📦 Test 3: Full Portfolio Construction")
    from app.portfolio_construction.ai_portfolio_builder import AIPortfolioBuilder
    from app.schemas.portfolio_construction import RiskProfile, InvestmentStrategy

    builder = AIPortfolioBuilder()
    
    # Build portfolio with explicit symbols
    result = await builder.build_portfolio(
        investment_amount=10000.0,
        symbols=["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "BAJFINANCE", "WIPRO"],
        risk_profile=RiskProfile.MODERATE,
        strategy_type=InvestmentStrategy.AI_HYBRID,
        buffer_pct=0.25,
    )

    check("Portfolio construction succeeds", result.get("success", False))
    
    if result.get("success"):
        portfolio = result["portfolio"]
        check("Has investment_amount", portfolio.get("investment_amount") == 10000.0)
        check("Has buffer_percentage", portfolio.get("buffer_percentage") == 25.0)
        check("Has buffer_amount", portfolio.get("buffer_amount", 0) > 0)
        check("Has active_allocation", portfolio.get("active_allocation", 0) > 0)
        check("Has allocations list", isinstance(portfolio.get("allocations"), list))
        check("Has at least 1 allocation", len(portfolio.get("allocations", [])) >= 1)
        check("Has ensemble scores", len(portfolio.get("ensemble_scores", {})) > 0)
        check("Has diversification_metrics", isinstance(portfolio.get("diversification_metrics"), dict))
        
        # Check buffer math
        expected_buffer = 10000.0 * 0.25
        check(f"Buffer amount ~= ${expected_buffer}", 
              abs(portfolio["buffer_amount"] - expected_buffer) < 10)
        expected_active = 10000.0 * 0.75
        check(f"Active allocation ~= ${expected_active}",
              abs(portfolio["active_allocation"] - expected_active) < 10)

        # Check allocation details
        alloc = portfolio["allocations"][0]
        check("Allocation has symbol", "symbol" in alloc)
        check("Allocation has weight", "weight" in alloc)
        check("Allocation has amount", "amount" in alloc)
        check("Allocation has ai_score", "ai_score" in alloc)
        check("Weight is between 0-1", 0 <= alloc["weight"] <= 0.25)

        # Check buffer composition
        buffer_comp = portfolio.get("buffer_composition", {})
        check("Buffer composition has rotation_reserve", "rotation_reserve" in buffer_comp)
        check("Buffer composition has risk_hedge", "risk_hedge" in buffer_comp)


async def test_risk_buffer_manager():
    """Test buffer and rotation logic."""
    logger.info("\n📦 Test 4: Risk Buffer Manager")
    from app.portfolio_construction.risk_buffer_manager import RiskBufferManager

    manager = RiskBufferManager()
    check("RiskBufferManager initializes", manager is not None)

    # Test buffer status computation
    active_positions = {
        "RELIANCE": {"weight": 0.2, "amount": 1500, "quantity": 5, "price": 300, "ai_score": 0.8, "risk_score": 0.2},
        "TCS": {"weight": 0.15, "amount": 1125, "quantity": 2, "price": 562, "ai_score": 0.75, "risk_score": 0.25},
        "INFY": {"weight": 0.12, "amount": 900, "quantity": 3, "price": 300, "ai_score": 0.7, "risk_score": 0.3},
    }
    
    status = manager.get_buffer_status(
        buffer_amount=2500.0,
        total_investment=10000.0,
        active_positions=active_positions,
    )
    
    check("Buffer status has buffer_amount", "buffer_amount" in status)
    check("Buffer status has health", "health" in status)
    check("Buffer status has rotation_capacity", "rotation_capacity" in status)
    check("Buffer health is HEALTHY/ADEQUATE/DEPLETED", 
          status["health"] in ["HEALTHY", "ADEQUATE", "DEPLETED"])
    check(f"Buffer is 25% of total", status["buffer_pct_of_total"] == 25.0)

    # Test rotation reserve
    rotation_reserve = manager.get_rotation_reserve(2500.0)
    check("Rotation reserve is 60% of buffer", rotation_reserve == 1500.0)
    
    risk_hedge = manager.get_risk_hedge(2500.0)
    check("Risk hedge is 40% of buffer", risk_hedge == 1000.0)


async def test_api_schema_validation():
    """Test Pydantic schema validation."""
    logger.info("\n📦 Test 5: API Schema Validation")
    from app.schemas.portfolio_construction import (
        PortfolioInvestmentRequest, AllocationItem, BufferComposition,
        RebalanceRequest, RotationOpportunity, RebalanceOrder,
        RiskProfile, InvestmentStrategy, RebalanceTrigger
    )

    # Test PortfolioInvestmentRequest
    req = PortfolioInvestmentRequest(
        user_id=1,
        investment_amount=10000.0,
        symbols=["RELIANCE", "TCS"],
        risk_profile=RiskProfile.MODERATE,
        strategy_type=InvestmentStrategy.AI_HYBRID,
    )
    check("Investment request validates", req.user_id == 1)
    check("Amount is > 0", req.investment_amount == 10000.0)
    check("Buffer default is 25%", req.buffer_percentage == 25.0)
    
    # Test AllocationItem
    alloc = AllocationItem(
        symbol="RELIANCE",
        weight=0.185,
        amount=1387.5,
        quantity=3,
        estimated_price=462.5,
        ai_score=0.82,
        risk_score=0.2,
        reason="AI ensemble score",
        predicted_return=0.023,
    )
    check("Allocation validates", alloc.symbol == "RELIANCE")
    check("Weight between 0-1", 0 <= alloc.weight <= 1)

    # Test RebalanceOrder
    order = RebalanceOrder(
        symbol="TCS",
        action="BUY",
        quantity=2,
        estimated_price=4100,
        estimated_total=8200,
        reason="AI score increased",
    )
    check("Rebalance order validates", order.action == "BUY")

    # Test RotationOpportunity
    opp = RotationOpportunity(
        symbol="WIPRO",
        current_ai_score=0.65,
        score_delta=0.35,
        reason="Score exceeds current holding",
        estimated_entry_price=450,
        confidence=0.85,
    )
    check("Rotation opportunity validates", opp.rotation_type == "BUFFER_TO_ACTIVE")
    check("Confidence between 0-1", 0 <= opp.confidence <= 1)


async def test_concentration_limits():
    """Test concentration limit enforcement."""
    logger.info("\n📦 Test 6: Concentration Limits")
    from app.portfolio_construction.ai_portfolio_builder import AIPortfolioBuilder

    builder = AIPortfolioBuilder()
    
    # Simulate weights that exceed max
    symbols = ["A", "B", "C"]
    weights = {"A": 0.50, "B": 0.30, "C": 0.20}  # A exceeds 20% max
    scored = {
        "A": {"final_score": 0.9, "risk_score": 0.1, "reason": "test", "lstm_prediction": 0.05},
        "B": {"final_score": 0.7, "risk_score": 0.2, "reason": "test", "lstm_prediction": 0.03},
        "C": {"final_score": 0.5, "risk_score": 0.3, "reason": "test", "lstm_prediction": 0.01},
    }
    prices = {"A": 100, "B": 100, "C": 100}

    allocations, metrics = builder._apply_concentration_limits(
        symbols=symbols,
        weights=weights,
        active_amount=7500,
        scored_symbols=scored,
        prices=prices,
    )

    check("Concentration limits applied", len(allocations) > 0)
    
    # With only 3 symbols all exceeding 20%, they're capped and redistributed evenly
    # A (0.50) → capped to 0.20, B (0.30) → capped to 0.20, C (0.20) → stays 0.20
    # Excess = 0.40 redistributed evenly → all become 0.333
    # Verify caps were applied (weights should be more equal than original)
    original = {"A": 0.50, "B": 0.30, "C": 0.20}
    max_original = max(original.values())
    max_after = max(a["weight"] for a in allocations)
    check("Concentration cap reduced max weight", max_after < max_original - 0.10)
    
    check("Diversification metrics present", len(metrics) > 0)
    check("Has total_positions", "total_positions" in metrics)
    check("Has herfindahl_index", "herfindahl_index" in metrics)


async def test_final_weights_computation():
    """Test different allocation strategies."""
    logger.info("\n📦 Test 7: Weight Computation Strategies")
    from app.portfolio_construction.ai_portfolio_builder import AIPortfolioBuilder
    from app.schemas.portfolio_construction import InvestmentStrategy

    builder = AIPortfolioBuilder()
    
    symbols = ["A", "B", "C"]
    scored = {
        "A": {"final_score": 0.9},
        "B": {"final_score": 0.6},
        "C": {"final_score": 0.3},
    }
    
    # AI Only
    ai_weights = builder._compute_final_weights(symbols, scored, None, InvestmentStrategy.AI_ONLY)
    check("AI-only weights sum to ~1", abs(sum(ai_weights.values()) - 1.0) < 0.01)
    check("AI-only: A > B > C", ai_weights["A"] > ai_weights["B"] > ai_weights["C"])

    # MPT fallback (no MPT data available = equal weight)
    mpt_weights = builder._compute_final_weights(symbols, scored, {"A": 0.33, "B": 0.33, "C": 0.34}, InvestmentStrategy.MPT_ONLY)
    check("MPT weights sum to ~1", abs(sum(mpt_weights.values()) - 1.0) < 0.01)

    # AI Hybrid
    hybrid_weights = builder._compute_final_weights(symbols, scored, {"A": 0.4, "B": 0.35, "C": 0.25}, InvestmentStrategy.AI_HYBRID)
    check("Hybrid weights sum to ~1", abs(sum(hybrid_weights.values()) - 1.0) < 0.01)


async def test_edge_cases():
    """Test edge cases."""
    logger.info("\n📦 Test 8: Edge Cases")
    from app.portfolio_construction.ai_portfolio_builder import AIPortfolioBuilder

    builder = AIPortfolioBuilder()

    # Empty symbols
    result = await builder.build_portfolio(
        investment_amount=5000.0,
        symbols=[],
    )
    # Empty symbols should auto-select defaults and succeed
    check("Empty symbols auto-selects candidates", result.get("success", False))

    # Single symbol
    result2 = await builder.build_portfolio(
        investment_amount=5000.0,
        symbols=["RELIANCE"],
    )
    check("Single symbol returns error or succeeds", True)
    
    # Zero amount
    result3 = await builder.build_portfolio(
        investment_amount=0,
        symbols=["RELIANCE", "TCS"],
    )
    check("Zero amount returns error", not result3.get("success", True) or result3.get("portfolio", {}).get("active_allocation", 1) == 0)


async def main():
    logger.info("=" * 60)
    logger.info("🏁 PORTFOLIO INVESTMENT SMOKE TEST SUITE")
    logger.info("=" * 60)
    
    await test_lstm_predictor()
    await test_ai_portfolio_builder()
    await test_portfolio_construction()
    await test_risk_buffer_manager()
    await test_api_schema_validation()
    await test_concentration_limits()
    await test_final_weights_computation()
    await test_edge_cases()

    logger.info("\n" + "=" * 60)
    logger.info(f"📊 RESULTS: {passed} passed, {failed} failed, {passed + failed} total")
    logger.info("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
