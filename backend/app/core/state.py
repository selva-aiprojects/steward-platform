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
