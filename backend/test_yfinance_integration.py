import asyncio
import yfinance as yf
import random

async def test_yfinance_integration():
    print("Testing yfinance integration...")
    
    # Multi-exchange Watchlist (NSE, BSE, MCX) - converted to yfinance format
    watchlist = [
        # NSE (Nifty 50 highlights) - converted to yfinance format (SYMBOL.NS)
        'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
        'SBIN.NS', 'ITC.NS', 'LT.NS', 'AXISBANK.NS', 'KOTAKBANK.NS',
        'BAJFINANCE.NS', 'BAJAJFINSV.NS', 'MARUTI.NS', 'TATAMOTORS.NS',
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

    print(f"Fetching data for {len(watchlist)} symbols...")
    
    # Fetch data for all tickers
    raw_quotes = {}
    for ticker_symbol in watchlist:
        try:
            print(f"Fetching data for {ticker_symbol}...")
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period="1d", interval="1m")
            
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                change_pct = ((current_price - prev_close) / prev_close) * 100
                
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
                
                print(f"  {clean_symbol} ({exchange}): {current_price:.2f}, {change_pct:+.2f}%")
            else:
                print(f"  No data found for {ticker_symbol}")
        except Exception as e:
            print(f"  Error fetching data for {ticker_symbol}: {e}")
            continue
    
    print(f"\nSuccessfully fetched data for {len(raw_quotes)} symbols out of {len(watchlist)}")
    
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

        top_gainers = sorted_movers[:5]  # Top 5
        top_losers = sorted_movers[-5:]   # Bottom 5

        print(f"\nTop {len(top_gainers)} Gainers:")
        for s, q in top_gainers:
            exchange = q.get('exchange', 'NSE')
            print(f"  {s} ({exchange}): {q.get('last_price', 0):.2f}, +{q['calculated_change']:.2f}%")

        print(f"\nTop {len(top_losers)} Losers:")
        for s, q in top_losers:
            exchange = q.get('exchange', 'NSE')
            print(f"  {s} ({exchange}): {q.get('last_price', 0):.2f}, {q['calculated_change']:.2f}%")
    
    print("\nyfinance integration test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_yfinance_integration())