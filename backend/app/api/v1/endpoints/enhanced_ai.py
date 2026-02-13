"""
Enhanced AI Endpoints for StockSteward AI
Integrates multiple LLM providers with financial data sources
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

from app.core.rbac import get_current_user
from app.models.user import User
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

router = APIRouter()

@router.post("/market-analysis", response_model=MarketAnalysisResponse)
async def enhanced_market_analysis(
    request: MarketAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Perform enhanced market analysis using multiple LLM providers and data sources
    """
    try:
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
            from app.services.kite_service import kite_service
            market_dict = kite_service.get_quote(request.symbol, request.exchange or "NSE")
        
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
            analysis_type=request.analysis_type or "comprehensive"
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result.get("error", "Analysis failed"))
        
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