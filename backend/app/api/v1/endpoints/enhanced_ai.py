"""
Enhanced AI Endpoints for StockSteward AI
Integrates multiple LLM providers with financial data sources
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import logging
import asyncio
import httpx
import time

from app.core.rbac import get_current_user
from app.core.database import SessionLocal
from app.models.user import User
from app.models.portfolio import Portfolio
from app.models.strategy import Strategy
from app.models.optimization import StrategyOptimizationResult
from app.schemas.ai_schemas import (
    MarketAnalysisRequest,
    MarketAnalysisResponse,
    MarketResearchResponse,
    ChatRequest,
    ChatResponse,
    MultiSourceAnalysisRequest,
    AvailableModelsResponse,
    AvailableProvidersResponse
)
from app.services.enhanced_llm_service import enhanced_llm_service
from app.services.data_integration import data_integration_service
from app.observability.metrics import record_external_call, record_strategy_update

router = APIRouter()
logger = logging.getLogger(__name__)


def _clamp(v: float, low: float, high: float) -> float:
    return max(low, min(high, v))


async def _fast_live_quote(symbol: str, exchange: str = "NSE") -> Dict:
    from app.services.kite_service import kite_service
    from app.core.state import find_price_by_symbol

    normalized_symbol = (symbol or "").upper()
    lookup_symbol = normalized_symbol if normalized_symbol.endswith(".NS") else f"{normalized_symbol}.NS"

    # 1) cache/state first
    cached = find_price_by_symbol(lookup_symbol) or find_price_by_symbol(normalized_symbol)
    if cached and cached.get("price"):
        return {
            "symbol": normalized_symbol,
            "exchange": exchange,
            "last_price": float(cached["price"]),
            "change": float(cached.get("change", 0.0)),
            "source": "state_cache",
        }

    # 2) Kite with hard timeout
    try:
        started = time.perf_counter()
        quote = await asyncio.wait_for(
            asyncio.to_thread(kite_service.get_quote, normalized_symbol, exchange),
            timeout=2.5,
        )
        if quote and quote.get("last_price"):
            record_external_call("kite", "quote", time.perf_counter() - started, True)
            return quote
        record_external_call("kite", "quote", time.perf_counter() - started, False)
    except Exception:
        record_external_call("kite", "quote", None, False)
        pass

    # 3) Yahoo quote API with hard timeout
    try:
        started = time.perf_counter()
        async with httpx.AsyncClient(timeout=httpx.Timeout(2.5), headers={"User-Agent": "Mozilla/5.0"}) as client:
            response = await client.get(
                "https://query1.finance.yahoo.com/v7/finance/quote",
                params={"symbols": lookup_symbol},
            )
            response.raise_for_status()
            payload = response.json() or {}
            rows = (((payload.get("quoteResponse") or {}).get("result")) or [])
            if rows:
                row = rows[0]
                current = row.get("regularMarketPrice")
                prev = row.get("regularMarketPreviousClose")
                current_f = float(current) if current is not None else None
                if current_f is not None:
                    prev_f = float(prev) if prev is not None else current_f
                    change = 0.0 if prev_f == 0 else ((current_f - prev_f) / prev_f) * 100
                    record_external_call("yahoo_quote_api", "quote", time.perf_counter() - started, True)
                    return {
                        "symbol": normalized_symbol,
                        "exchange": exchange,
                        "last_price": current_f,
                        "change": change,
                        "source": "yahoo_quote_api",
                    }
            record_external_call("yahoo_quote_api", "quote", time.perf_counter() - started, False)
    except Exception:
        record_external_call("yahoo_quote_api", "quote", None, False)
        pass

    return {}


def _derive_strategy_update_params(analysis_result: Dict, market_dict: Dict) -> Dict:
    confidence = float(analysis_result.get("confidence", 55.0))
    confidence_scale = _clamp(confidence / 100.0, 0.1, 1.0)
    recommendation = str(analysis_result.get("recommendation", "HOLD")).upper()

    current_price = None
    for key in ["last_price", "current_price", "price", "close"]:
        try:
            if key in market_dict and market_dict.get(key) is not None:
                current_price = float(market_dict[key])
                break
        except Exception:
            continue
    if current_price is None or current_price <= 0:
        current_price = 100.0

    target_price = float(analysis_result.get("target_price", current_price))
    stop_loss_price = float(analysis_result.get("stop_loss", current_price * 0.98))
    delta_up = abs((target_price - current_price) / current_price)
    delta_down = abs((current_price - stop_loss_price) / current_price)

    entry_threshold = _clamp(0.005 + (delta_up * 0.5), 0.001, 0.05)
    exit_threshold = _clamp(0.003 + (delta_down * 0.5), 0.001, 0.03)

    if recommendation == "BUY":
        take_profit = _clamp(max(delta_up, 0.02), 0.02, 0.30)
        stop_loss = _clamp(max(delta_down, 0.01), 0.01, 0.15)
    elif recommendation == "SELL":
        take_profit = _clamp(max(delta_down, 0.02), 0.02, 0.30)
        stop_loss = _clamp(max(delta_up, 0.01), 0.01, 0.15)
    else:
        take_profit = 0.03
        stop_loss = 0.02

    position_size = int(10000 * confidence_scale)
    if recommendation == "HOLD":
        position_size = int(position_size * 0.5)

    return {
        "entry_threshold": round(entry_threshold, 4),
        "exit_threshold": round(exit_threshold, 4),
        "stop_loss": round(stop_loss, 4),
        "take_profit": round(take_profit, 4),
        "position_size": max(1000, position_size),
    }


def _apply_dynamic_strategy_update(user_id: int, symbol: str, params: Dict) -> Dict:
    db = SessionLocal()
    try:
        portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
        if not portfolio:
            return {"updated": False, "reason": "portfolio_not_found"}

        strategy_query = db.query(Strategy).filter(Strategy.portfolio_id == portfolio.id)
        if symbol:
            strategy_query = strategy_query.filter(Strategy.symbol == symbol)
        strategy = (
            strategy_query
            .filter(Strategy.status.in_(["RUNNING", "ACTIVE"]))
            .order_by(Strategy.id.desc())
            .first()
        )
        if not strategy:
            strategy = (
                db.query(Strategy)
                .filter(Strategy.portfolio_id == portfolio.id)
                .order_by(Strategy.id.desc())
                .first()
            )
        if not strategy:
            return {"updated": False, "reason": "strategy_not_found"}

        optimization_row = StrategyOptimizationResult(
            user_id=user_id,
            strategy_name=strategy.name,
            symbol=symbol or strategy.symbol,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow(),
            parameter_space={"source": "llm_dynamic_update", "type": "bounded_params"},
            best_parameters=params,
            best_score=0.0,
            optimization_trace=[{"timestamp": datetime.utcnow().isoformat(), "params": params}],
            execution_time=0.0,
            status="COMPLETED",
        )
        db.add(optimization_row)
        db.commit()
        db.refresh(optimization_row)
        record_strategy_update(True)
        return {
            "updated": True,
            "strategy_id": strategy.id,
            "optimization_id": optimization_row.id,
            "params": params,
        }
    except Exception as e:
        db.rollback()
        record_strategy_update(False)
        logger.error("Failed dynamic strategy update for user_id=%s symbol=%s: %s", user_id, symbol, e)
        return {"updated": False, "reason": "exception", "error": str(e)}
    finally:
        db.close()

@router.post("/market-analysis", response_model=MarketAnalysisResponse)
async def enhanced_market_analysis(
    request: MarketAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Perform enhanced market analysis using multiple LLM providers and data sources
    """
    try:
        # New orchestration/update controls are superadmin-only.
        if current_user.role != "SUPERADMIN" and not current_user.is_superuser:
            if request.orchestration_framework != "native":
                raise HTTPException(
                    status_code=403,
                    detail="Only SUPERADMIN can use non-native orchestration frameworks"
                )
            request.auto_update_strategy = False

        # Fetch market data based on request parameters
        if request.data_source == "historical":
            # Fetch historical data for analysis
            market_data = await data_integration_service.fetch_nse_data(
                symbol=request.symbol,
                start_date=request.start_date or datetime.now() - timedelta(days=30),
                end_date=request.end_date or datetime.now(),
                interval=request.interval or "day"
            )
            
            if market_data.empty:
                raise HTTPException(status_code=404, detail="No market data found for the specified parameters")
            
            # Preprocess data for analysis
            processed_data = await data_integration_service.preprocess_data(market_data)
            
            # Convert to dictionary format for LLM
            market_dict = processed_data.tail(1).to_dict('records')[0] if not processed_data.empty else {}
        else:
            # Use real-time data from existing services
            market_dict = await _fast_live_quote(request.symbol, request.exchange or "NSE")
        
        # Get user context
        user_context = {
            "risk_tolerance": current_user.risk_tolerance,
            "investment_horizon": getattr(current_user, 'investment_horizon', 'MEDIUM_TERM'),
            "portfolio_size": getattr(current_user, 'portfolio_size', 'VARIES'),
            "experience_level": getattr(current_user, 'experience_level', 'INTERMEDIATE')
        }
        
        # Perform analysis with specified LLM provider
        result = await enhanced_llm_service.analyze_market_data(
            market_data=market_dict,
            user_context=user_context,
            llm_provider=request.llm_provider or "groq",
            model=request.model,
            analysis_type=request.analysis_type or "comprehensive",
            orchestration_framework=request.orchestration_framework or "native",
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result.get("error", "Analysis failed"))

        if request.auto_update_strategy:
            params = _derive_strategy_update_params(result, market_dict if isinstance(market_dict, dict) else {})
            strategy_update = _apply_dynamic_strategy_update(
                user_id=current_user.id,
                symbol=request.symbol.upper(),
                params=params,
            )
            result["strategy_update"] = strategy_update
        
        return MarketAnalysisResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in enhanced market analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market-research", response_model=MarketResearchResponse)
async def enhanced_market_research(
    sector: Optional[str] = Query(None, description="Specific sector to analyze"),
    llm_provider: str = Query("groq", description="LLM provider to use"),
    current_user: User = Depends(get_current_user)
):
    """
    Generate enhanced market research and sector analysis
    """
    try:
        # Fetch sector-specific data if requested
        sector_data = None
        if sector:
            # This would fetch sector-specific data from various sources
            from app.services.kite_service import kite_service
            sector_symbols = kite_service.get_sector_symbols(sector)
            if sector_symbols:
                # Get recent data for sector constituents
                sector_data = {}
                for symbol in sector_symbols[:10]:  # Limit to top 10 stocks
                    quote = kite_service.get_quote(symbol, "NSE")
                    if quote and 'error' not in quote:
                        sector_data[symbol] = quote
        
        # Generate market research using enhanced LLM service
        research_result = await enhanced_llm_service.generate_market_research(
            sector_data=sector_data,
            llm_provider=llm_provider
        )
        
        if "error" in research_result:
            raise HTTPException(status_code=500, detail=research_result.get("error", "Research generation failed"))
        
        return MarketResearchResponse(**research_result)
        
    except Exception as e:
        logger.error(f"Error in enhanced market research: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=ChatResponse)
async def enhanced_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Enhanced chat with financial data context
    """
    try:
        # Enhance the user's request with market context
        enhanced_context = f"""
        User Context:
        - Role: {current_user.role}
        - Risk Tolerance: {current_user.risk_tolerance}
        - Trading Mode: {getattr(current_user, 'trading_mode', 'PAPER')}
        
        User Request: {request.message}
        
        Additional Context: {request.context}
        """
        
        # Use the enhanced LLM service for response
        if request.llm_provider == "openai":
            result = await enhanced_llm_service.analyze_with_openai(
                prompt=enhanced_context,
                model=request.model or "gpt-4-turbo"
            )
        elif request.llm_provider == "anthropic":
            result = await enhanced_llm_service.analyze_with_anthropic(
                prompt=enhanced_context,
                model=request.model or "claude-3-sonnet-20240229"
            )
        elif request.llm_provider == "huggingface":
            result = await enhanced_llm_service.analyze_with_huggingface(
                prompt=enhanced_context,
                model_name=request.model or "ProsusAI/finbert"
            )
        else:  # Default to Groq
            result = await enhanced_llm_service.analyze_with_groq(
                prompt=enhanced_context,
                model=request.model or "llama-3.3-70b-versatile"
            )
        
        if "error" in result:
            # Return a fallback response if LLM call fails
            return ChatResponse(
                response="I'm currently experiencing technical difficulties. Market analysis is temporarily unavailable. Please try again later."
            )
        
        # Extract response from result (might be nested in analysis object)
        if isinstance(result, dict):
            if "response" in result:
                response_text = result["response"]
            elif "analysis" in result and "summary" in result["analysis"]:
                response_text = result["analysis"]["summary"]
            elif "prediction" in result:
                response_text = result["prediction"]
            else:
                # Convert the entire result to a readable format
                response_text = json.dumps(result, indent=2, default=str)
        else:
            response_text = str(result)
        
        return ChatResponse(response=response_text)
        
    except Exception as e:
        logger.error(f"Error in enhanced chat: {e}")
        return ChatResponse(
            response="I'm currently experiencing technical difficulties. Please try again later."
        )


@router.post("/multi-source-analysis")
async def multi_source_analysis(
    symbols: List[str] = Query(..., description="List of symbols to analyze"),
    start_date: Optional[datetime] = Query(None, description="Start date for historical data"),
    end_date: Optional[datetime] = Query(None, description="End date for historical data"),
    llm_provider: str = Query("groq", description="LLM provider to use"),
    data_source: str = Query("nse", description="Data source to use"),
    current_user: User = Depends(get_current_user)
):
    """
    Perform analysis using multiple data sources and LLM providers
    """
    try:
        # Fetch data from multiple sources
        all_data = await data_integration_service.fetch_combined_data(
            symbols=symbols,
            start_date=start_date or datetime.now() - timedelta(days=30),
            end_date=end_date or datetime.now(),
            data_source=data_source
        )
        
        results = {}
        
        for symbol, data in all_data.items():
            if not data.empty:
                # Prepare data for LLM analysis
                features = await data_integration_service.get_features_for_llm(data)
                
                # Perform analysis
                analysis = await enhanced_llm_service.analyze_market_data(
                    market_data=features,
                    user_context={
                        "risk_tolerance": current_user.risk_tolerance,
                        "investment_horizon": getattr(current_user, 'investment_horizon', 'MEDIUM_TERM')
                    },
                    llm_provider=llm_provider,
                    analysis_type="comprehensive"
                )
                
                results[symbol] = analysis
        
        return {"analyses": results, "summary": f"Analyzed {len(results)} symbols from {data_source}"}
        
    except Exception as e:
        logger.error(f"Error in multi-source analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/available-models")
async def get_available_models(
    provider: Optional[str] = Query(None, description="Specific provider to query")
):
    """
    Get available models from different LLM providers
    """
    try:
        models = enhanced_llm_service.get_available_models(provider)
        return {"models": models}
    except Exception as e:
        logger.error(f"Error getting available models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/available-providers")
async def get_available_providers():
    """
    Get list of available LLM providers
    """
    try:
        providers = enhanced_llm_service.get_available_providers()
        return {"providers": providers}
    except Exception as e:
        logger.error(f"Error getting available providers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Add the router to the API
