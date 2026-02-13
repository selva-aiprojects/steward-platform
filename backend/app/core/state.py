from typing import Dict, List, Any

# Shared global state for market data to ensure consistency across Socket.IO and REST API
# This prevents "conflicting sources" issues reported by users

# Main gainers and losers
last_market_movers = {
    'gainers': [],
    'losers': [],
    'currencies': [],
    'metals': [],
    'commodities': []
}

# AI Prediction state
last_steward_prediction = {
    "prediction": "Initializing market intelligence...",
    "decision": "NEUTRAL",
    "confidence": 0,
    "signal_mix": {"technical": 0, "fundamental": 0, "news": 0},
    "risk_radar": 0,
    "history": []
}

# Exchange status
last_exchange_status = {
    'nse': 'online',
    'bse': 'online',
    'mcx': 'online',
    'status': 'ONLINE',
    'latency': '24ms'
}

# Order book depth (Latest sample)
last_order_book = {
    'bids': [],
    'asks': []
}

# Macro indicators (Latest real data)
last_macro_indicators = {
    "usd_inr": 0,
    "gold": 0,
    "crude": 0,
    "10y_yield": 0,
    "sentiment": "NEUTRAL",
    "volatility_level": "LOW"
}


def get_default_market_snapshot() -> Dict[str, List[Dict[str, Any]]]:
    """
    Stable fallback dataset used when upstream market feeds are unavailable.
    Ensures UI cards and tickers always have visible values.
    """
    gainers = [
        {"symbol": "RELIANCE", "exchange": "NSE", "price": 2855.40, "change": 1.25, "last_price": 2855.40},
        {"symbol": "TCS", "exchange": "NSE", "price": 4251.30, "change": 0.96, "last_price": 4251.30},
        {"symbol": "HDFCBANK", "exchange": "NSE", "price": 1688.20, "change": 0.82, "last_price": 1688.20},
        {"symbol": "INFY", "exchange": "NSE", "price": 1749.75, "change": 0.64, "last_price": 1749.75},
        {"symbol": "ICICIBANK", "exchange": "NSE", "price": 1228.55, "change": 0.51, "last_price": 1228.55},
    ]
    losers = [
        {"symbol": "AXISBANK", "exchange": "NSE", "price": 1092.15, "change": -0.44, "last_price": 1092.15},
        {"symbol": "ITC", "exchange": "NSE", "price": 468.80, "change": -0.58, "last_price": 468.80},
        {"symbol": "KOTAKBANK", "exchange": "NSE", "price": 1764.60, "change": -0.73, "last_price": 1764.60},
        {"symbol": "LT", "exchange": "NSE", "price": 3629.90, "change": -0.85, "last_price": 3629.90},
        {"symbol": "SBIN", "exchange": "NSE", "price": 762.40, "change": -1.02, "last_price": 762.40},
    ]
    currencies = [
        {"symbol": "USDINR", "exchange": "FOREX", "price": 83.42, "change": 0.05, "last_price": 83.42},
        {"symbol": "EURINR", "exchange": "FOREX", "price": 90.61, "change": -0.08, "last_price": 90.61},
        {"symbol": "GBPINR", "exchange": "FOREX", "price": 106.87, "change": 0.11, "last_price": 106.87},
    ]
    metals = [
        {"symbol": "GOLD", "exchange": "MCX", "price": 62450.00, "change": 0.33, "last_price": 62450.00},
        {"symbol": "SILVER", "exchange": "MCX", "price": 71240.00, "change": -0.21, "last_price": 71240.00},
        {"symbol": "COPPER", "exchange": "MCX", "price": 741.80, "change": 0.18, "last_price": 741.80},
    ]
    commodities = [
        {"symbol": "CRUDEOIL", "exchange": "MCX", "price": 6510.00, "change": -0.42, "last_price": 6510.00},
        {"symbol": "NATURALGAS", "exchange": "MCX", "price": 189.60, "change": 0.27, "last_price": 189.60},
    ]
    return {
        "gainers": gainers,
        "losers": losers,
        "currencies": currencies,
        "metals": metals,
        "commodities": commodities
    }

def clean_ticker_symbol(symbol: str) -> str:
    """Standardizes symbols by removing common yfinance suffixes/prefixes and mapping to friendly names"""
    if not symbol:
        return ""
    
    # Common mappings for commodities and indices
    mappings = {
        '^NSEI': 'NIFTY 50',
        '^BSESN': 'SENSEX',
        'USDINR=X': 'USD/INR',
        'GC=F': 'GOLD',
        'CL=F': 'CRUDEOIL',
        'SI=F': 'SILVER',
        'HG=F': 'COPPER',
        'NG=F': 'NATURALGAS',
        'RELIANCE.NS': 'RELIANCE',
        'TCS.NS': 'TCS',
        'HDFCBANK.NS': 'HDFCBANK',
        'INFY.NS': 'INFY',
        'ICICIBANK.NS': 'ICICIBANK',
        'SBIN.NS': 'SBIN'
    }
    
    # Check upper case version
    u_symbol = symbol.upper()
    if u_symbol in mappings:
        return mappings[u_symbol]
        
    return u_symbol.replace('.NS', '').replace('.BO', '').replace('=F', '').replace('=X', '').replace('^', '')

def find_price_by_symbol(symbol: str) -> Dict[str, Any]:
    """Helper to find a price for a symbol in the current global state"""
    search_sym = symbol.upper().replace('.NS', '').replace('.BO', '')
    
    # Check gainers/losers
    for group in ['gainers', 'losers']:
        for item in last_market_movers.get(group, []):
            if item['symbol'].upper() == search_sym:
                return item
    
    # Check macro
    if search_sym in ['GOLD', 'GC']:
        return {'price': last_macro_indicators['gold'], 'symbol': 'GOLD', 'change': 0}
    if search_sym in ['CRUDE', 'CL', 'CRUDEOIL']:
        return {'price': last_macro_indicators['crude'], 'symbol': 'CRUDEOIL', 'change': 0}
    if search_sym in ['USD', 'USDINR']:
        return {'price': last_macro_indicators['usd_inr'], 'symbol': 'USD/INR', 'change': 0}
        
    return None
