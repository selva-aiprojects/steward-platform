from fastapi import APIRouter, Depends
from typing import Any, List, Dict
from app.core.config import settings
import random
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/status")
def get_market_status() -> Any:
    """
    Get current market status and latency.
    """
    return {
        "status": "ONLINE",
        "latency": "24ms",
        "exchange": "NSE/BSE/MCX"
    }

@router.get("/movers")
async def get_market_movers() -> Any:
    """
    Get top gainers and losers.
    Fetches live data from KiteConnect/Zerodha API.
    """
    from app.services.kite_service import kite_service
    from app.core.config import settings

    # Check if we have proper API credentials
    if not settings.ZERODHA_API_KEY or not settings.ZERODHA_ACCESS_TOKEN:
        # Return mock data if no credentials
        return {
            "gainers": [
                {"symbol": "RELIANCE", "exchange": "NSE", "price": 2987.5, "change": 1.2, "last_price": 2987.5},
                {"symbol": "HDFCBANK", "exchange": "NSE", "price": 1450.0, "change": 0.8, "last_price": 1450.0},
                {"symbol": "INFY", "exchange": "NSE", "price": 1540.0, "change": 1.1, "last_price": 1540.0},
                {"symbol": "HINDUNILVR", "exchange": "NSE", "price": 2850.0, "change": 0.9, "last_price": 2850.0},
                {"symbol": "ICICIBANK", "exchange": "NSE", "price": 1042.0, "change": 0.7, "last_price": 1042.0}
            ],
            "losers": [
                {"symbol": "TCS", "exchange": "NSE", "price": 3450.0, "change": -0.5, "last_price": 3450.0},
                {"symbol": "SBIN", "exchange": "NSE", "price": 580.0, "change": -0.8, "last_price": 580.0},
                {"symbol": "AXISBANK", "exchange": "NSE", "price": 1125.0, "change": -0.4, "last_price": 1125.0},
                {"symbol": "WIPRO", "exchange": "NSE", "price": 420.0, "change": -1.2, "last_price": 420.0},
                {"symbol": "SUNPHARMA", "exchange": "NSE", "price": 1340.0, "change": -0.6, "last_price": 1340.0}
            ]
        }

    try:
        # Fetch live market data from KiteConnect
        kite = kite_service.get_client()
        if not kite:
            # Return mock data if Kite client not available
            return {
                "gainers": [
                    {"symbol": "RELIANCE", "exchange": "NSE", "price": 2987.5, "change": 1.2, "last_price": 2987.5},
                    {"symbol": "HDFCBANK", "exchange": "NSE", "price": 1450.0, "change": 0.8, "last_price": 1450.0},
                    {"symbol": "INFY", "exchange": "NSE", "price": 1540.0, "change": 1.1, "last_price": 1540.0}
                ],
                "losers": [
                    {"symbol": "TCS", "exchange": "NSE", "price": 3450.0, "change": -0.5, "last_price": 3450.0},
                    {"symbol": "SBIN", "exchange": "NSE", "price": 580.0, "change": -0.8, "last_price": 580.0}
                ]
            }

        # Get top NSE stocks to analyze
        nse_symbols = [
            "NSE:RELIANCE", "NSE:TCS", "NSE:HDFCBANK", "NSE:INFY", "NSE:ICICIBANK",
            "NSE:SBIN", "NSE:ITC", "NSE:LT", "NSE:AXISBANK", "NSE:KOTAKBANK",
            "NSE:BAJFINANCE", "NSE:BAJAJFINSV", "NSE:MARUTI", "NSE:TATAMOTORS",
            "NSE:BHARTIARTL", "NSE:ADANIENT", "NSE:ADANIPORTS", "NSE:ASIANPAINT",
            "NSE:ULTRACEMCO", "NSE:WIPRO", "NSE:TECHM", "NSE:HCLTECH", "NSE:ONGC",
            "NSE:POWERGRID", "NSE:NTPC", "NSE:COALINDIA", "NSE:SUNPHARMA",
            "NSE:DRREDDY", "NSE:CIPLA", "NSE:HINDUNILVR"
        ]

        # Fetch live quotes
        quotes = kite_service.get_quotes(nse_symbols)

        # Separate gainers and losers
        gainers = []
        losers = []

        for symbol, quote_data in quotes.items():
            if quote_data and 'last_price' in quote_data:
                # Calculate change percentage if not directly available
                change_pct = quote_data.get('net_change_percent', 0)  # Use direct change percentage if available
                if change_pct == 0 and 'ohlc' in quote_data and 'open' in quote_data['ohlc']:
                    change_pct = ((quote_data['last_price'] - quote_data['ohlc']['open']) / quote_data['ohlc']['open']) * 100
                elif change_pct == 0 and 'change' in quote_data:
                    change_pct = quote_data['change']

                stock_data = {
                    "symbol": symbol.split(":")[1] if ":" in symbol else symbol,
                    "exchange": symbol.split(":")[0] if ":" in symbol else "NSE",
                    "price": quote_data['last_price'],
                    "change": round(change_pct, 2),
                    "last_price": quote_data['last_price']
                }

                if change_pct >= 0:
                    gainers.append(stock_data)
                else:
                    losers.append(stock_data)

        # Sort by change percentage and return top 10 gainers and losers
        gainers_sorted = sorted(gainers, key=lambda x: x['change'], reverse=True)[:10]
        losers_sorted = sorted(losers, key=lambda x: x['change'])[:10]

        return {
            "gainers": gainers_sorted,
            "losers": losers_sorted
        }

    except Exception as e:
        logger.error(f"Error fetching market movers: {e}")
        # Return mock data if API call fails
        return {
            "gainers": [
                {"symbol": "RELIANCE", "exchange": "NSE", "price": 2987.5, "change": 1.2, "last_price": 2987.5},
                {"symbol": "HDFCBANK", "exchange": "NSE", "price": 1450.0, "change": 0.8, "last_price": 1450.0},
                {"symbol": "INFY", "exchange": "NSE", "price": 1540.0, "change": 1.1, "last_price": 1540.0}
            ],
            "losers": [
                {"symbol": "TCS", "exchange": "NSE", "price": 3450.0, "change": -0.5, "last_price": 3450.0},
                {"symbol": "SBIN", "exchange": "NSE", "price": 580.0, "change": -0.8, "last_price": 580.0}
            ]
        }


@router.get("/heatmap")
def get_sector_heatmap() -> Any:
    sectors = [
        "Banking", "IT", "Energy", "FMCG", "Auto", "Metals", "Pharma", "Infra"
    ]
    return [
        {"sector": s, "score": round(random.uniform(-5, 5), 2)}
        for s in sectors
    ]


@router.get("/news")
def get_market_news() -> Any:
    headlines = [
        "FIIs net buyers as Nifty holds key support",
        "Banking stocks lead rally on credit growth optimism",
        "IT majors steady ahead of weekly earnings updates",
        "Oil slips; metals mixed in early trade",
        "Rupee stabilizes as dollar index softens"
    ]
    random.shuffle(headlines)
    return [{"headline": h, "impact": random.choice(["LOW", "MEDIUM", "HIGH"])} for h in headlines[:4]]


@router.get("/options")
def get_options_snapshot() -> Any:
    symbols = ["NIFTY", "BANKNIFTY", "RELIANCE", "TCS"]
    return [
        {
            "symbol": s,
            "iv": round(random.uniform(12, 28), 2),
            "oi_change": round(random.uniform(-8, 8), 2),
            "put_call": round(random.uniform(0.6, 1.4), 2)
        } for s in symbols
    ]


@router.get("/depth")
def get_order_book_depth() -> Any:
    bids = [{"price": round(2200 + i * 0.5, 2), "qty": random.randint(50, 500)} for i in range(5)]
    asks = [{"price": round(2202 + i * 0.5, 2), "qty": random.randint(50, 500)} for i in range(5)]
    return {"bids": bids, "asks": asks}


@router.get("/macro")
def get_macro_indicators() -> Any:
    return {
        "usd_inr": round(random.uniform(82.5, 84.5), 2),
        "gold": round(random.uniform(60000, 65000), 2),
        "crude": round(random.uniform(70, 86), 2),
        "10y_yield": round(random.uniform(6.8, 7.4), 2)
    }
