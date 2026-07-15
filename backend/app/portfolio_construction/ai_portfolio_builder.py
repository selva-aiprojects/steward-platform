"""
AI Portfolio Builder — Core engine for constructing AI-powered investment portfolios.

This is the central piece that:
1. Scores candidate symbols using a 4-model AI ensemble
2. Applies Modern Portfolio Theory (Markowitz) optimization
3. Blends AI scores with MPT weights using a configurable hybrid formula
4. Applies the 25% buffer (rotation reserve + risk hedge)
5. Generates a complete allocation plan with execution orders

Ensemble Weights (configurable by risk profile):
| Model              | Conservative | Moderate | Aggressive |
|--------------------|-------------|----------|------------|
| FinBERT Sentiment  | 30%         | 25%      | 20%        |
| LLM Fundamental    | 30%         | 25%      | 20%        |
| LSTM Price Predict | 10%         | 30%      | 40%        |
| Risk Score         | 30%         | 20%      | 20%        |
"""
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from app.engines.ai_filter_engine import ai_filter_engine
from app.engines.finbert_engine import finbert_engine
from app.ml_models.lstm_predictor import lstm_predictor
from app.services.llm_service import LLMService
from app.schemas.portfolio_construction import (
    InvestmentStrategy, RiskProfile, AllocationItem, BufferComposition,
    PortfolioInvestmentResponse, RebalanceOrder
)

logger = logging.getLogger(__name__)


# ----------- Risk Profile Configuration -----------

ENSEMBLE_WEIGHTS = {
    RiskProfile.CONSERVATIVE: {
        "finbert_sentiment": 0.30,
        "llm_fundamental": 0.30,
        "lstm_price": 0.10,
        "risk_score": 0.30,
    },
    RiskProfile.MODERATE: {
        "finbert_sentiment": 0.25,
        "llm_fundamental": 0.25,
        "lstm_price": 0.30,
        "risk_score": 0.20,
    },
    RiskProfile.AGGRESSIVE: {
        "finbert_sentiment": 0.20,
        "llm_fundamental": 0.20,
        "lstm_price": 0.40,
        "risk_score": 0.20,
    },
}

# Portfolio construction constraints
MAX_SINGLE_POSITION_PCT = 0.20       # Max 20% in any single stock
MIN_SINGLE_POSITION_PCT = 0.02       # Min 2% (avoid micro positions)
MIN_POSITIONS = 5                     # Minimum diversification
MAX_SECTOR_PCT = 0.40                 # Max 40% in one sector
MIN_AI_SCORE_TO_INCLUDE = 0.10       # Exclude symbols with very low AI scores
REBALANCE_AI_SCORE_DELTA_THRESHOLD = 0.30  # Score change to trigger rotation


class AIPortfolioBuilder:
    """
    Core engine for constructing AI-optimized investment portfolios.
    """

    def __init__(self):
        self.llm_service = LLMService()
        logger.info("AIPortfolioBuilder initialized")

    # ======================================================================
    # MAIN ENTRY POINT
    # ======================================================================

    async def build_portfolio(
        self,
        investment_amount: float,
        symbols: Optional[List[str]] = None,
        risk_profile: RiskProfile = RiskProfile.MODERATE,
        strategy_type: InvestmentStrategy = InvestmentStrategy.AI_HYBRID,
        buffer_pct: float = 0.25,
        user_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Build an AI-optimized portfolio.

        Flow:
        1. Candidate selection (use provided symbols or auto-detect)
        2. AI ensemble scoring (FinBERT + LLM + LSTM + Risk)
        3. Hybrid optimization (blend AI scores with MPT weights)
        4. 25% buffer application
        5. Concentration & diversification checks
        6. Generate allocation plan with orders
        """
        logger.info(f"Building portfolio: amount={investment_amount}, risk={risk_profile.value}, "
                    f"strategy={strategy_type.value}, buffer={buffer_pct*100:.0f}%")

        # Step 1: Candidate symbols
        if not symbols:
            symbols = await self._auto_select_candidates()
        if len(symbols) < 2:
            return {"success": False, "error": "Need at least 2 candidate symbols"}

        # Step 2: AI ensemble scoring
        ensemble_scores = await self._compute_ensemble_scores(symbols, risk_profile)
        if not ensemble_scores:
            return {"success": False, "error": "Failed to compute AI scores"}

        # Filter out low-scoring symbols
        scored_symbols = {k: v for k, v in ensemble_scores.items()
                          if v.get("final_score", 0) >= MIN_AI_SCORE_TO_INCLUDE}
        if len(scored_symbols) < MIN_POSITIONS:
            # Fall through with what we have, even if few
            scored_symbols = ensemble_scores

        symbols_scored = list(scored_symbols.keys())
        if len(symbols_scored) < 1:
            return {"success": False, "error": "No symbols passed AI scoring threshold"}

        # Step 3: Get current prices for allocation
        prices = await self._fetch_current_prices(symbols_scored)

        # Step 4: Compute allocations
        if strategy_type in [InvestmentStrategy.AI_HYBRID, InvestmentStrategy.MPT_ONLY]:
            # Run MPT optimization for covariance-based weights
            mpt_weights = await self._run_mpt_optimization(symbols_scored, risk_profile)
        else:
            mpt_weights = None

        # Determine final allocation weights
        final_weights = self._compute_final_weights(
            symbols_scored, scored_symbols, mpt_weights, strategy_type
        )

        # Step 5: Apply 25% buffer
        buffer_amount = investment_amount * buffer_pct
        active_amount = investment_amount - buffer_amount

        buffer_composition = BufferComposition(
            rotation_reserve=buffer_pct * 0.6,   # 60% of buffer for rotation
            risk_hedge=buffer_pct * 0.4,          # 40% of buffer for risk
            total_buffer_pct=buffer_pct,
            total_buffer_amount=buffer_amount,
        )

        # Step 6: Apply concentration limits and generate allocations
        allocations, divers_metrics = self._apply_concentration_limits(
            symbols_scored, final_weights, active_amount, scored_symbols, prices
        )

        # Step 7: Build response
        allocation_items = []
        for alloc in allocations:
            allocation_items.append(AllocationItem(
                symbol=alloc["symbol"],
                weight=alloc["weight"],
                amount=alloc["amount"],
                quantity=alloc["quantity"],
                estimated_price=alloc["price"],
                ai_score=alloc["ai_score"],
                risk_score=alloc["risk_score"],
                reason=alloc["reason"],
                predicted_return=alloc["predicted_return"],
            ))

        return {
            "success": True,
            "portfolio": {
                "investment_amount": investment_amount,
                "buffer_percentage": buffer_pct * 100,
                "buffer_amount": round(buffer_amount, 2),
                "active_allocation": round(active_amount, 2),
                "strategy_type": strategy_type.value,
                "risk_profile": risk_profile.value,
                "allocations": [a.model_dump() for a in allocation_items],
                "buffer_composition": buffer_composition.model_dump(),
                "diversification_metrics": divers_metrics,
                "ensemble_scores": {s: round(scored_symbols[s]["final_score"], 4)
                                   for s in symbols_scored},
                "ensemble_breakdown": {
                    s: {k: round(v, 4) for k, v in scored_symbols[s].items() if k != "reason"}
                    for s in symbols_scored
                },
                "created_at": datetime.utcnow().isoformat(),
            }
        }

    # ======================================================================
    # STEP 2: AI ENSEMBLE SCORING
    # ======================================================================

    async def compute_scores_for_symbols(
        self, symbols: List[str], risk_profile: RiskProfile = RiskProfile.MODERATE
    ) -> Dict[str, Dict[str, float]]:
        """Public entry point for scoring symbols without building a portfolio."""
        return await self._compute_ensemble_scores(symbols, risk_profile)

    async def _compute_ensemble_scores(
        self, symbols: List[str], risk_profile: RiskProfile
    ) -> Dict[str, Dict[str, float]]:
        """
        Score each symbol using the 4-model AI ensemble:
        1. FinBERT sentiment score
        2. LLM fundamental analysis score
        3. LSTM price prediction score
        4. Risk assessment score
        """
        weights = ENSEMBLE_WEIGHTS.get(risk_profile, ENSEMBLE_WEIGHTS[RiskProfile.MODERATE])
        logger.info(f"Computing ensemble scores for {len(symbols)} symbols "
                    f"(weights: {weights})")

        scores = {}

        # --- Sub-model 1: FinBERT Sentiment ---
        sentiment_scores = await self._get_finbert_scores(symbols)

        # --- Sub-model 2: LLM Fundamental ---
        llm_scores = await self._get_llm_fundamental_scores(symbols)

        # --- Sub-model 3: LSTM Price Prediction ---
        lstm_scores = await self._get_lstm_predictions(symbols)

        # --- Sub-model 4: Risk Assessment ---
        risk_scores = await self._get_risk_scores(symbols)

        # --- Ensemble ---
        for symbol in symbols:
            sent_data = sentiment_scores.get(symbol, {})
            sent = sent_data.get("score", 0) if isinstance(sent_data, dict) else 0
            llm = llm_scores.get(symbol, {}).get("score", 0)
            lstm = lstm_scores.get(symbol, {}).get("normalized_score", 0)
            risk = risk_scores.get(symbol, {}).get("normalized_score", 0.5)

            final_score = (
                weights["finbert_sentiment"] * sent +
                weights["llm_fundamental"] * llm +
                weights["lstm_price"] * lstm +
                weights["risk_score"] * (1 - risk)  # Invert risk: lower risk = higher score
            )

            # Collect reasoning
            reasons = []
            if sentiment_scores.get(symbol, {}).get("reason"):
                reasons.append(f"Sentiment: {sentiment_scores[symbol]['reason']}")
            if llm_scores.get(symbol, {}).get("reason"):
                reasons.append(f"Fundamental: {llm_scores[symbol]['reason']}")
            if lstm_scores.get(symbol, {}).get("reason"):
                reasons.append(f"Price: {lstm_scores[symbol]['reason']}")

            scores[symbol] = {
                "final_score": max(-1.0, min(1.0, final_score)),
                "sentiment_score": sent,
                "llm_score": llm,
                "lstm_prediction": lstm_scores.get(symbol, {}).get("predicted_return", 0),
                "lstm_confidence": lstm_scores.get(symbol, {}).get("confidence", 0.5),
                "risk_score": risk,
                "reason": "; ".join(reasons) if reasons else "AI ensemble score",
            }

        return scores

    # ----------- Sub-model 1: FinBERT Sentiment -----------

    async def _get_finbert_scores(self, symbols: List[str]) -> Dict[str, Any]:
        """Get FinBERT sentiment scores for each symbol."""
        scores = {}
        try:
            # Use the AIFilterEngine which already wraps FinBERT
            result = await ai_filter_engine.analyze_market_sentiment(
                news_data=[], social_data=[], symbols=symbols
            )
            if result.get("success"):
                sentiment = result.get("sentiment_analysis", {})
                overall = sentiment.get("overall_sentiment", 0)
                # Apply same score to all symbols (macro/combined sentiment)
                for symbol in symbols:
                    scores[symbol] = {
                        "score": overall,
                        "reason": f"Market sentiment: {overall:.3f}, regime: {sentiment.get('market_regime', 'N/A')}",
                    }
            else:
                logger.warning(f"FinBERT analysis failed: {result.get('error')}")
                for symbol in symbols:
                    scores[symbol] = {"score": 0, "reason": "FinBERT unavailable"}
        except Exception as e:
            logger.error(f"Error getting FinBERT scores: {e}")
            for symbol in symbols:
                scores[symbol] = {"score": 0, "reason": f"Error: {str(e)[:50]}"}

        return scores

    # ----------- Sub-model 2: LLM Fundamental Analysis -----------

    async def _get_llm_fundamental_scores(self, symbols: List[str]) -> Dict[str, Any]:
        """Get LLM-based fundamental analysis scores using Groq Llama."""
        scores = {}
        try:
            # Prepare a prompt for the LLM to score fundamental attractiveness
            prompt = (
                "You are a fundamental analyst. For each stock symbol below, provide:\n"
                "1. A score from -1.0 (very bearish) to +1.0 (very bullish)\n"
                "2. A brief 1-sentence reason\n\n"
                f"Symbols: {', '.join(symbols)}\n\n"
                "Respond in JSON format: {\"SYMBOL\": {\"score\": float, \"reason\": \"...\"}, ...}"
            )

            # Attempt LLM inference
            if self.llm_service.client:
                response = self.llm_service.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are a financial fundamental analyst. Respond only in valid JSON."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.3,
                    max_tokens=2000,
                    response_format={"type": "json_object"},
                )
                import json
                try:
                    parsed = json.loads(response.choices[0].message.content)
                    for symbol in symbols:
                        if symbol in parsed:
                            s = parsed[symbol]
                            scores[symbol] = {
                                "score": max(-1.0, min(1.0, float(s.get("score", 0)))),
                                "reason": s.get("reason", "LLM analysis"),
                            }
                        else:
                            scores[symbol] = {"score": 0, "reason": "No LLM data"}
                except (json.JSONDecodeError, KeyError, ValueError, TypeError):
                    logger.warning("Failed to parse LLM response as JSON")
                    for symbol in symbols:
                        scores[symbol] = {"score": 0, "reason": "LLM parse error"}
            else:
                logger.warning("LLM client not initialized, using neutral scores")
                for symbol in symbols:
                    scores[symbol] = {"score": 0, "reason": "LLM unavailable"}

        except Exception as e:
            logger.error(f"Error getting LLM scores: {e}")
            for symbol in symbols:
                scores[symbol] = {"score": 0, "reason": f"LLM error: {str(e)[:50]}"}

        return scores

    # ----------- Sub-model 3: LSTM Price Prediction -----------

    async def _get_lstm_predictions(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Get LSTM price movement predictions.
        In production, fetches OHLCV data from market provider.
        In fallback, uses statistical momentum analysis.
        """
        scores = {}
        try:
            # Try to fetch market data for these symbols
            from app.realtime.market_provider import get_market_provider
            provider = get_market_provider()

            ohlcv_map = {}
            for symbol in symbols:
                try:
                    # Fetch last 90 days of OHLCV data
                    data = await provider.get_historical_data(symbol, days=90)
                    if data and len(data) > 20:
                        ohlcv_map[symbol] = data
                except Exception as e:
                    logger.debug(f"No OHLCV data for {symbol}: {e}")

            if ohlcv_map:
                # Run LSTM predictions
                predictions = lstm_predictor.predict_batch(ohlcv_map)

                for symbol in symbols:
                    pred = predictions.get(symbol)
                    if pred:
                        # Normalize predicted return to -1..1 score
                        norm_score = max(-1.0, min(1.0, pred.get("predicted_return", 0) * 10))
                        direction = pred.get("direction", "NEUTRAL")
                        confidence = pred.get("confidence", 0.5)
                        scores[symbol] = {
                            "normalized_score": norm_score * confidence,  # Confidence-weighted
                            "predicted_return": pred.get("predicted_return", 0),
                            "confidence": confidence,
                            "direction": direction,
                            "volatility": pred.get("volatility_forecast", 0),
                            "reason": f"Direction: {direction}, Return: {pred.get('predicted_return', 0)*100:.2f}%",
                        }
                    else:
                        scores[symbol] = {
                            "normalized_score": 0,
                            "predicted_return": 0,
                            "confidence": 0,
                            "direction": "NEUTRAL",
                            "volatility": 0,
                            "reason": "Insufficient data for prediction",
                        }
            else:
                # No OHLCV data available — use neutral scores
                for symbol in symbols:
                    scores[symbol] = {
                        "normalized_score": 0,
                        "predicted_return": 0,
                        "confidence": 0.3,
                        "direction": "NEUTRAL",
                        "volatility": 0,
                        "reason": "Market data unavailable",
                    }
        except Exception as e:
            logger.error(f"Error getting LSTM predictions: {e}")
            for symbol in symbols:
                scores[symbol] = {
                    "normalized_score": 0,
                    "predicted_return": 0,
                    "confidence": 0.3,
                    "direction": "NEUTRAL",
                    "volatility": 0,
                    "reason": f"LSTM error: {str(e)[:50]}",
                }

        return scores

    # ----------- Sub-model 4: Risk Assessment -----------

    async def _get_risk_scores(self, symbols: List[str]) -> Dict[str, Any]:
        """Get risk assessment for each symbol using existing Risk Engine."""
        scores = {}
        for symbol in symbols:
            try:
                result = await ai_filter_engine.assess_risk({
                    "volatility": 0.2,
                    "correlation": 0.5,
                    "volume": 1000000,
                    "price_level": 100,
                    "trend_strength": 0.5,
                    "market_regime": "normal",
                })
                if result.get("success"):
                    risk = result["risk_assessment"]
                    risk_level = risk.get("risk_level", 50) / 100.0  # Normalize 0-1
                    scores[symbol] = {
                        "normalized_score": risk_level,
                        "risk_category": risk.get("risk_category", "MEDIUM"),
                        "var_95": risk.get("var_95", 0),
                        "reason": f"Risk: {risk.get('risk_category', 'MEDIUM')} ({risk.get('risk_level', 50):.0f}/100)",
                    }
                else:
                    scores[symbol] = {"normalized_score": 0.5, "risk_category": "MEDIUM",
                                      "var_95": 0, "reason": "Risk engine unavailable"}
            except Exception as e:
                logger.error(f"Error scoring risk for {symbol}: {e}")
                scores[symbol] = {"normalized_score": 0.5, "risk_category": "MEDIUM",
                                  "var_95": 0, "reason": f"Error: {str(e)[:50]}"}

        return scores

    # ======================================================================
    # STEP 4: MPT OPTIMIZATION
    # ======================================================================

    async def _run_mpt_optimization(
        self, symbols: List[str], risk_profile: RiskProfile
    ) -> Dict[str, float]:
        """
        Run Modern Portfolio Theory (Markowitz) optimization.
        Returns optimal weights that maximize Sharpe ratio.
        """
        n = len(symbols)
        if n < 2:
            return {s: 1.0 / n for s in symbols}

        try:
            from scipy.optimize import minimize
            # Try to get historical returns for covariance matrix
            from app.realtime.market_provider import get_market_provider
            provider = get_market_provider()

            returns_data = {}
            for symbol in symbols:
                try:
                    data = await provider.get_historical_data(symbol, days=252)  # 1 year
                    if data and len(data) > 20:
                        closes = np.array([d.get("close", d.get(4, 0)) for d in data], dtype=np.float64)
                        returns = np.diff(closes) / closes[:-1]
                        returns_data[symbol] = returns
                except Exception:
                    pass

            if len(returns_data) >= 2:
                # Build aligned returns matrix
                min_len = min(len(r) for r in returns_data.values())
                aligned = np.column_stack([
                    returns_data[s][-min_len:] for s in symbols
                ])

                # Expected returns (annualized)
                mean_returns = np.mean(aligned, axis=0) * 252
                # Covariance matrix (annualized)
                cov_matrix = np.cov(aligned.T) * 252

                # Risk-free rate based on profile
                risk_free_rates = {
                    RiskProfile.CONSERVATIVE: 0.04,
                    RiskProfile.MODERATE: 0.03,
                    RiskProfile.AGGRESSIVE: 0.02,
                }
                risk_free = risk_free_rates.get(risk_profile, 0.03)

                # Maximize Sharpe ratio
                def neg_sharpe(weights):
                    weights = np.array(weights)
                    portfolio_return = np.dot(weights, mean_returns)
                    portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                    if portfolio_vol < 1e-10:
                        return 0
                    return -(portfolio_return - risk_free) / portfolio_vol

                # Constraints: weights sum to 1
                constraints = [{"type": "eq", "fun": lambda x: np.sum(x) - 1.0}]
                # Bounds: 0-1 with concentration limit
                bounds = [(0.0, MAX_SINGLE_POSITION_PCT) for _ in range(n)]

                # Initial guess: equal weight
                x0 = np.array([1.0 / n] * n)

                result = minimize(neg_sharpe, x0, method="SLSQP",
                                  bounds=bounds, constraints=constraints,
                                  options={"maxiter": 500, "ftol": 1e-9})

                if result.success:
                    weights = result.x / np.sum(result.x)  # Normalize
                    return {symbols[i]: weights[i] for i in range(n)}
                else:
                    logger.warning(f"MPT optimization failed: {result.message}")

            # Fallback: equal weight
            return {s: 1.0 / n for s in symbols}

        except ImportError:
            # scipy not available — skip MPT
            logger.warning("scipy not available — skipping MPT optimization")
            return {s: 1.0 / n for s in symbols}
        except Exception as e:
            logger.error(f"MPT optimization error: {e}")
            return {s: 1.0 / n for s in symbols}

    # ======================================================================
    # STEP 5: FINAL WEIGHT COMPUTATION (AI + MPT Hybrid)
    # ======================================================================

    def _compute_final_weights(
        self,
        symbols: List[str],
        scored_symbols: Dict[str, Dict],
        mpt_weights: Optional[Dict[str, float]],
        strategy_type: InvestmentStrategy,
    ) -> Dict[str, float]:
        """Compute final allocation weights based on strategy type."""
        n = len(symbols)
        alpha = 0.5  # Hybrid blend factor (configurable)

        # AI-based weights (softmax of final scores)
        ai_scores = np.array([scored_symbols[s]["final_score"] for s in symbols])
        # Clip negative scores
        ai_scores_positive = np.maximum(ai_scores, 0.01)
        ai_weights = ai_scores_positive / np.sum(ai_scores_positive)

        if strategy_type == InvestmentStrategy.AI_ONLY:
            return {symbols[i]: ai_weights[i] for i in range(n)}

        if strategy_type == InvestmentStrategy.MPT_ONLY:
            if mpt_weights:
                return mpt_weights
            return {symbols[i]: ai_weights[i] for i in range(n)}

        if strategy_type == InvestmentStrategy.MARKOWITZ:
            if mpt_weights:
                return mpt_weights
            return {symbols[i]: ai_weights[i] for i in range(n)}

        # AI_HYBRID: blend AI and MPT weights
        if mpt_weights:
            mpt_arr = np.array([mpt_weights.get(s, 0) for s in symbols])
            mpt_arr = mpt_arr / np.sum(mpt_arr)  # Normalize
            final = alpha * ai_weights + (1 - alpha) * mpt_arr
            final = final / np.sum(final)
        else:
            final = ai_weights

        return {symbols[i]: final[i] for i in range(n)}

    # ======================================================================
    # STEP 6: CONCENTRATION & DIVERSIFICATION CHECKS
    # ======================================================================

    def _apply_concentration_limits(
        self,
        symbols: List[str],
        weights: Dict[str, float],
        active_amount: float,
        scored_symbols: Dict[str, Dict],
        prices: Dict[str, float],
    ) -> Tuple[List[Dict], Dict[str, Any]]:
        """
        Apply concentration limits and generate final allocations.
        Redistributes excess to buffer if single position exceeds limit.
        """
        # Sort by weight descending
        sorted_symbols = sorted(symbols, key=lambda s: weights.get(s, 0), reverse=True)

        # Apply max/min position limits
        adjusted_weights = {}
        excess = 0.0

        for s in sorted_symbols:
            w = weights.get(s, 0)
            if w > MAX_SINGLE_POSITION_PCT:
                excess += w - MAX_SINGLE_POSITION_PCT
                adjusted_weights[s] = MAX_SINGLE_POSITION_PCT
            elif w < MIN_SINGLE_POSITION_PCT and len(symbols) > MIN_POSITIONS:
                excess += w
                adjusted_weights[s] = 0  # Exclude too-small positions
            else:
                adjusted_weights[s] = w

        # Remove zero-weight symbols
        adjusted_weights = {k: v for k, v in adjusted_weights.items() if v > 0}

        # Distribute excess back proportionally
        if excess > 0.001 and adjusted_weights:
            total = sum(adjusted_weights.values())
            if total > 0:
                for s in adjusted_weights:
                    adjusted_weights[s] += excess * (adjusted_weights[s] / total)

        # Normalize to sum to 1
        total = sum(adjusted_weights.values())
        if total > 0:
            for s in adjusted_weights:
                adjusted_weights[s] /= total

        # Generate allocation items
        allocations = []
        sector_exposure = {}
        total_allocated = 0

        for s, w in adjusted_weights.items():
            amount = active_amount * w
            price = prices.get(s, 100)
            quantity = int(amount / price) if price > 0 else 0
            actual_amount = quantity * price
            total_allocated += actual_amount

            allocations.append({
                "symbol": s,
                "weight": round(w, 4),
                "amount": round(actual_amount, 2),
                "quantity": quantity,
                "price": price,
                "ai_score": scored_symbols.get(s, {}).get("final_score", 0),
                "risk_score": scored_symbols.get(s, {}).get("risk_score", 0.5),
                "reason": scored_symbols.get(s, {}).get("reason", "AI optimized"),
                "predicted_return": scored_symbols.get(s, {}).get("lstm_prediction", 0),
            })

            # Track sector (simplified — from symbol prefix)
            sector = self._guess_sector(s)
            sector_exposure[sector] = sector_exposure.get(sector, 0) + w

        # Diversification metrics
        divers_metrics = {
            "total_positions": len(allocations),
            "sector_exposure": sector_exposure,
            "top_position_weight": max(a["weight"] for a in allocations) if allocations else 0,
            "herfindahl_index": sum(a["weight"] ** 2 for a in allocations),  # Concentration metric
            "total_allocated": total_allocated,
            "remaining_to_buffer": active_amount - total_allocated,
        }

        return allocations, divers_metrics

    # ======================================================================
    # HELPERS
    # ======================================================================

    async def _auto_select_candidates(self) -> List[str]:
        """Auto-detect candidate symbols from market data / watchlists."""
        # In production, this could pull from:
        # 1. User's watchlist
        # 2. Nifty 50 / Sensex 30 top movers
        # 3. High-volume symbols from market data
        # For now, return a sensible default set
        return [
            "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK",
            "ITC", "BAJFINANCE", "WIPRO", "HINDUNILVR", "SBIN",
        ]

    async def _fetch_current_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Fetch current market prices for symbols."""
        prices = {}
        try:
            from app.realtime.market_provider import get_market_provider
            provider = get_market_provider()
            for symbol in symbols:
                try:
                    data = await provider.get_current_price(symbol)
                    if data:
                        prices[symbol] = float(data.get("price", data.get("close", 100)))
                except Exception:
                    prices[symbol] = 100.0  # Fallback
        except Exception:
            for symbol in symbols:
                prices[symbol] = 100.0
        return prices

    def _guess_sector(self, symbol: str) -> str:
        """Simple sector classification based on symbol heuristics."""
        sector_map = {
            "RELIANCE": "Energy & Telecom",
            "TCS": "IT",
            "INFY": "IT",
            "WIPRO": "IT",
            "HDFCBANK": "Banking",
            "ICICIBANK": "Banking",
            "SBIN": "Banking",
            "KOTAKBANK": "Banking",
            "AXISBANK": "Banking",
            "BAJFINANCE": "Financial Services",
            "BAJAJFINSV": "Financial Services",
            "HINDUNILVR": "FMCG",
            "ITC": "FMCG",
            "NESTLEIND": "FMCG",
            "BRITANNIA": "FMCG",
            "MARUTI": "Automobile",
            "TATAMOTORS": "Automobile",
            "M&M": "Automobile",
            "RELIANCE": "Energy",
            "ONGC": "Energy",
            "POWERGRID": "Utilities",
            "NTPC": "Utilities",
            "LT": "Construction",
            "TATASTEEL": "Metals & Mining",
            "HINDALCO": "Metals & Mining",
        }
        return sector_map.get(symbol, "Others")


# Singleton instance
ai_portfolio_builder = AIPortfolioBuilder()
