"""
TrueData API Service for Indian Market Data

This module implements the TrueData API service for fetching live Indian market data.
TrueData provides real-time market data for Indian exchanges (NSE, BSE, MCX).
"""

import os
import logging
import requests
from typing import Dict, List, Any, Optional
from app.core.config import settings
import yfinance as yf

logger = logging.getLogger(__name__)


class TrueDataService:
    """
    Service class for interacting with TrueData API
    """
    
    def __init__(self):
        self.api_key = settings.TRUEDATA_API_KEY
        self.base_url = "https://api.truedata.in"
        self.session = None
        
        if self.api_key:
            logger.info("TrueData API service initialized with API key")
        else:
            logger.warning("TrueData API key not configured. Using fallback data sources.")
    
    def get_client(self):
        """
        Initialize and return TrueData client
        NOTE: This is a placeholder implementation as TrueData API specifics vary
        In a real implementation, you would use the TrueData SDK or API
        """
        if not self.api_key:
            return None
            
        # Placeholder for TrueData client initialization
        # In a real implementation, you would use TrueData's specific client
        try:
            # For now, we'll simulate the TrueData client
            # In a real implementation, you would import and initialize TrueData's client
            return {
                "api_key": self.api_key,
                "base_url": self.base_url
            }
        except Exception as e:
            logger.error(f"Error initializing TrueData client: {e}")
            return None
    
    def get_quote(self, symbol: str, exchange: str = "NSE") -> Optional[Dict[str, Any]]:
        """
        Get live quote for a symbol from TrueData
        """
        if not self.api_key:
            return None
            
        try:
            # In a real implementation, this would call TrueData's API
            # For now, we'll use yfinance as a fallback for Indian stocks
            ticker = f"{symbol}.{exchange}"
            if exchange == "BSE":
                ticker = f"{symbol}.BO"
            elif exchange == "NSE":
                ticker = f"{symbol}.NS"
            
            # Use yfinance as fallback while we develop TrueData integration
            yf_ticker = yf.Ticker(ticker)
            hist = yf_ticker.history(period="5d")
            
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                
                # Calculate change percentage
                if len(hist) > 1:
                    prev_close = hist['Close'].iloc[-2]
                    change_pct = ((current_price - prev_close) / prev_close) * 100
                else:
                    change_pct = 0
                
                return {
                    "symbol": symbol,
                    "exchange": exchange,
                    "last_price": current_price,
                    "change": change_pct,
                    "volume": int(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else 0,
                    "high": hist['High'].iloc[-1],
                    "low": hist['Low'].iloc[-1],
                    "open": hist['Open'].iloc[-1]
                }
            else:
                return None
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol} from TrueData fallback: {e}")
            return None
    
    def get_batch_quotes(self, symbols: List[str], exchange: str = "NSE") -> List[Dict[str, Any]]:
        """
        Get live quotes for multiple symbols from TrueData
        """
        if not self.api_key:
            return []
        
        results = []
        for symbol in symbols:
            quote = self.get_quote(symbol, exchange)
            if quote:
                results.append(quote)
        
        return results
    
    def get_top_movers(self, count: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get top gainers and losers from TrueData
        """
        if not self.api_key:
            return {"gainers": [], "losers": []}

        try:
            # Define a watchlist of major Indian stocks
            indian_stocks = [
                "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK",
                "HINDUNILVR", "SBIN", "BHARTIARTL", "ITC", "KOTAKBANK",
                "LT", "AXISBANK", "MARUTI", "WIPRO", "TATAMOTORS",
                "SUNPHARMA", "NESTLEIND", "HCLTECH", "ULTRACEMCO", "M&M"
            ]

            # Get quotes for all stocks
            all_quotes = []
            for symbol in indian_stocks:
                quote = self.get_quote(symbol, "NSE")
                if quote and quote.get("change") is not None:
                    all_quotes.append(quote)

            # Sort by change percentage
            sorted_quotes = sorted(all_quotes, key=lambda x: x.get("change", 0), reverse=True)

            # Split into gainers and losers
            gainers = sorted_quotes[:count]
            losers = sorted_quotes[-count:]
            # Sort losers in ascending order (most negative changes first)
            losers = sorted(losers, key=lambda x: x.get("change", 0))

            return {
                "gainers": gainers,
                "losers": losers
            }
        except Exception as e:
            logger.error(f"Error fetching top movers from TrueData: {e}")
            return {"gainers": [], "losers": []}

    def get_top_movers(self, count: int = 15) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get top gainers and losers from TrueData
        This method is called by the market.py endpoint
        """
        if not self.api_key:
            return {"gainers": [], "losers": []}

        try:
            # Define a watchlist of major Indian stocks
            indian_stocks = [
                "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK",
                "HINDUNILVR", "SBIN", "BHARTIARTL", "ITC", "KOTAKBANK",
                "LT", "AXISBANK", "MARUTI", "WIPRO", "TATAMOTORS",
                "SUNPHARMA", "NESTLEIND", "HCLTECH", "ULTRACEMCO", "M&M",
                "BAJFINANCE", "HEROMOTOCO", "GRASIM", "ADANIPORTS", "POWERGRID",
                "DRREDDY", "BRITANNIA", "GODREJCP", "SHREECEM", "TITAN"
            ]

            # Get quotes for all stocks
            all_quotes = []
            for symbol in indian_stocks:
                quote = self.get_quote(symbol, "NSE")
                if quote and quote.get("change") is not None:
                    all_quotes.append(quote)

            # Sort by change percentage
            sorted_quotes = sorted(all_quotes, key=lambda x: x.get("change", 0), reverse=True)

            # Split into gainers and losers
            gainers = sorted_quotes[:count]
            losers = sorted_quotes[-count:]
            # Sort losers in ascending order (most negative changes first)
            losers = sorted(losers, key=lambda x: x.get("change", 0))

            return {
                "gainers": gainers,
                "losers": losers
            }
        except Exception as e:
            logger.error(f"Error fetching top movers from TrueData: {e}")
            return {"gainers": [], "losers": []}


# Global instance
true_data_service = TrueDataService()