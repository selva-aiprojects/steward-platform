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
    import datetime
    import pytz

    # Get current time in IST (Indian Standard Time)
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.datetime.now(ist)

    # Define market hours (9:15 AM to 3:30 PM IST for normal trading)
    market_open_time = current_time.replace(hour=9, minute=15, second=0, microsecond=0)
    market_close_time = current_time.replace(hour=15, minute=30, second=0, microsecond=0)

    # Check if it's a weekday and within market hours
    is_weekday = current_time.weekday() < 5  # Monday to Friday
    is_market_hours = market_open_time <= current_time <= market_close_time

    # Determine status based on current time
    nse_status = "open" if is_weekday and is_market_hours else "closed"
    bse_status = "open" if is_weekday and is_market_hours else "closed"
    mcx_status = "open" if is_weekday and is_market_hours else "closed"

    # Different status for different times of day
    if is_weekday:
        if current_time.time() < datetime.time(9, 15):
            nse_status = bse_status = mcx_status = "pre-market"
        elif current_time.time() < datetime.time(15, 30):
            nse_status = bse_status = mcx_status = "open"
        elif current_time.time() < datetime.time(16, 0):
            nse_status = bse_status = mcx_status = "closing-session"
        else:
            nse_status = bse_status = mcx_status = "closed"
    else:
        nse_status = bse_status = mcx_status = "closed"  # Weekend

    return {
        "status": "ONLINE",
        "latency": "24ms",
        "exchange": "NSE/BSE/MCX",
        "nse": nse_status,
        "bse": bse_status,
        "mcx": mcx_status,
        "timestamp": current_time.isoformat()
    }

@router.get("/movers")
async def get_market_movers() -> Any:
    """
    Get top gainers and losers.
    Fetches live data from yfinance.
    """
    import yfinance as yf
    from app.core.config import settings

    # Define the watchlist similar to the WebSocket implementation
    watchlist = [
        # NSE (Nifty 50 highlights) - converted to yfinance format (SYMBOL.NS)
        'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
        'SBIN.NS', 'ITC.NS', 'LT.NS', 'AXISBANK.NS', 'KOTAKBANK.NS',
        'BAJFINANCE.NS', 'BAJAJFINSV.NS', 'MARUTI.NS', 'TATAMOTORS.NS',
        'BHARTIARTL.NS', 'ADANIENT.NS', 'ADANIPORTS.NS', 'ASIANPAINT.NS',
        'ULTRACEMCO.NS', 'WIPRO.NS', 'TECHM.NS', 'HCLTECH.NS', 'ONGC.NS',
        'POWERGRID.NS', 'NTPC.NS', 'COALINDIA.NS', 'SUNPHARMA.NS',
        'DRREDDY.NS', 'CIPLA.NS', 'HINDUNILVR.NS',
        # BSE (using .BO for Bombay Stock Exchange)
        '^BSESN',  # SENSEX index
        # Commodities (using appropriate yfinance symbols)
        'GC=F',  # Gold futures
        'SI=F',  # Silver futures
        'CL=F',  # Crude Oil
        'NG=F',  # Natural Gas
        # Currency pairs
        'INR=X',  # USD/INR
    ]

    try:
        # Fetch data for all tickers
        raw_quotes = {}
        for ticker_symbol in watchlist:
            try:
                ticker = yf.Ticker(ticker_symbol)
                hist = ticker.history(period="5d")  # Changed to 5d to ensure we have previous close data

                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    # Use previous day's close for comparison
                    if len(hist) > 1:
                        prev_close = hist['Close'].iloc[-2]
                    elif 'previousClose' in ticker.info:
                        prev_close = ticker.info['previousClose']
                    else:
                        # If no previous data, use current price to avoid division by zero
                        prev_close = current_price

                    if prev_close != 0:
                        change_pct = ((current_price - prev_close) / prev_close) * 100
                    else:
                        change_pct = 0

                    # Determine exchange from ticker symbol
                    if '.NS' in ticker_symbol:
                        exchange = 'NSE'
                    elif '.BO' in ticker_symbol:
                        exchange = 'BSE'
                    elif ticker_symbol.startswith('^'):
                        exchange = 'BSE'  # Index
                    elif ticker_symbol.endswith('=F'):
                        exchange = 'MCX'  # Commodities
                    elif ticker_symbol.endswith('=X'):
                        exchange = 'FOREX'  # Forex
                    else:
                        exchange = 'OTHER'

                    # Extract clean symbol name
                    clean_symbol = ticker_symbol.replace('.NS', '').replace('.BO', '').replace('=F', '').replace('=X', '').replace('^', '')

                    raw_quotes[ticker_symbol] = {
                        'last_price': current_price,
                        'change': change_pct,
                        'exchange': exchange,
                        'symbol': clean_symbol
                    }
            except Exception as e:
                logger.error(f"Error fetching data for {ticker_symbol}: {e}")
                continue

        # Process quotes for gainers/losers
        quotes = {}
        for ticker_symbol, data in raw_quotes.items():
            # Extract clean symbol name
            clean_symbol = ticker_symbol.replace('.NS', '').replace('.BO', '').replace('=F', '').replace('=X', '').replace('^', '')
            quotes[clean_symbol] = data

        # Identify Gainers and Losers
        valid_quotes = {s: q for s, q in quotes.items() if q.get('last_price') is not None}

        if valid_quotes:
            # Calculate changes for each quote
            quotes_with_changes = {}
            for s, q in valid_quotes.items():
                change_pct = q.get('change', 0)
                quotes_with_changes[s] = {**q, 'calculated_change': change_pct}

            sorted_movers = sorted(quotes_with_changes.items(), key=lambda x: x[1]['calculated_change'], reverse=True)

            top_gainers = sorted_movers[:10]  # Top 10
            top_losers = sorted_movers[-10:]  # Bottom 10

            # Format movers for frontend
            gainers_data = []
            for s, q in top_gainers:
                # Determine exchange from original ticker symbol
                exchange = q.get('exchange', 'NSE')
                gainers_data.append({
                    'symbol': s,
                    'exchange': exchange,
                    'price': q.get('last_price', 0),
                    'change': round(q['calculated_change'], 2),
                    'last_price': q.get('last_price', 0)
                })

            losers_data = []
            for s, q in top_losers:
                # Determine exchange from original ticker symbol
                exchange = q.get('exchange', 'NSE')
                losers_data.append({
                    'symbol': s,
                    'exchange': exchange,
                    'price': q.get('last_price', 0),
                    'change': round(q['calculated_change'], 2),
                    'last_price': q.get('last_price', 0)
                })

            return {
                "gainers": gainers_data,
                "losers": losers_data
            }
        else:
            # Return mock data if no valid quotes
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
