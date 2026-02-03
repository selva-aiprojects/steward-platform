from kiteconnect import KiteConnect
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class KiteService:
    _instance = None
    _kite = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KiteService, cls).__new__(cls)
        return cls._instance

    def get_client(self):
        if self._kite is None:
            if not settings.ZERODHA_API_KEY:
                logger.warning("ZERODHA_API_KEY not configured.")
                return None
            
            self._kite = KiteConnect(api_key=settings.ZERODHA_API_KEY)
            
            if settings.ZERODHA_ACCESS_TOKEN:
                self._kite.set_access_token(settings.ZERODHA_ACCESS_TOKEN)
            else:
                logger.warning("ZERODHA_ACCESS_TOKEN not set. Manual authentication required.")
        
        return self._kite

    def get_quote(self, symbol: str, exchange: str = "NSE"):
        kite = self.get_client()
        if not kite or not settings.ZERODHA_ACCESS_TOKEN:
            return None
        
        try:
            instrument = f"{exchange}:{symbol}"
            quotes = kite.quote([instrument])
            return quotes.get(instrument)
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            return None

    def get_quotes(self, symbols: list):
        """Fetches quotes for multiple symbols at once."""
        kite = self.get_client()
        if not kite or not settings.ZERODHA_ACCESS_TOKEN:
            return {}
        
        try:
            instruments = [f"NSE:{s}" if ":" not in s else s for s in symbols]
            return kite.quote(instruments)
        except Exception as e:
            logger.error(f"Error fetching bulk quotes: {e}")
            return {}

    def get_historical(self, symbol: str, from_date, to_date, interval="day", exchange="NSE"):
        """Fetches historical OHLC data from Kite."""
        kite = self.get_client()
        if not kite or not settings.ZERODHA_ACCESS_TOKEN:
            return []
        
        try:
            # Need instrument_token for historical data. 
            # In production, this would be cached or fetched once.
            instruments = kite.instruments(exchange)
            token = next((i['instrument_token'] for i in instruments if i['tradingsymbol'] == symbol), None)
            
            if not token:
                logger.error(f"Instrument token not found for {symbol}")
                return []
                
            return kite.historical_data(token, from_date, to_date, interval)
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return []

    def generate_session(self, request_token: str):
        kite = self.get_client()
        if not kite or not settings.ZERODHA_API_SECRET:
            return None
        
        try:
            data = kite.generate_session(request_token, api_secret=settings.ZERODHA_API_SECRET)
            self._kite.set_access_token(data["access_token"])
            return data
        except Exception as e:
            logger.error(f"Error generating session: {e}")
            return None

kite_service = KiteService()
