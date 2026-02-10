import asyncio
import yfinance as yf

async def debug_yfinance():
    print("Debugging yfinance implementation...")
    
    # Test symbols similar to what's in the watchlist
    test_symbols = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', '^BSESN']
    
    for symbol in test_symbols:
        print(f"\nTesting symbol: {symbol}")
        try:
            ticker = yf.Ticker(symbol)
            
            # Try different approaches to get data
            print("  1. Trying history with 1d period...")
            hist = ticker.history(period="1d")
            print(f"     History shape: {hist.shape}")
            if not hist.empty:
                print(f"     Last row: {hist.iloc[-1].to_dict()}")
            else:
                print("     No data returned")
            
            print("  2. Trying history with 5d period...")
            hist_5d = ticker.history(period="5d")
            print(f"     5d History shape: {hist_5d.shape}")
            if not hist_5d.empty:
                print(f"     Last row: {hist_5d.iloc[-1].to_dict()}")
            else:
                print("     No data returned")
                
            print("  3. Trying info...")
            try:
                info = ticker.info
                print(f"     Info keys: {list(info.keys())[:10]}...")  # Show first 10 keys
                print(f"     Current price (regularMarketPrice): {info.get('regularMarketPrice', 'N/A')}")
                print(f"     Previous close: {info.get('previousClose', 'N/A')}")
            except Exception as e:
                print(f"     Info error: {e}")
                
        except Exception as e:
            print(f"     Error: {e}")
    
    print("\nTesting bulk fetch approach...")
    try:
        tickers_data = yf.Tickers(' '.join(test_symbols))
        print(f"Bulk tickers object created: {hasattr(tickers_data, 'tickers')}")
        
        for sym in test_symbols:
            print(f"  Testing {sym} via bulk...")
            try:
                ticker_obj = tickers_data.tickers[sym]
                hist = ticker_obj.history(period="1d")
                print(f"    Shape: {hist.shape}")
                if not hist.empty:
                    print(f"    Close: {hist['Close'].iloc[-1] if len(hist) > 0 else 'N/A'}")
            except Exception as e:
                print(f"    Bulk error for {sym}: {e}")
    except Exception as e:
        print(f"Bulk fetch error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_yfinance())