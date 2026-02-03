from kiteconnect import KiteConnect
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class KiteService:
    _instance = None
    _kite = None
    _instrument_tokens = {} # Cache for instrument tokens {symbol: token}

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

    def _load_instrument_tokens(self, exchange="NSE"):
        """Downloads and caches instrument tokens for an exchange."""
        kite = self.get_client()
        if not kite or not settings.ZERODHA_ACCESS_TOKEN:
            return
        
        try:
            logger.info(f"Refreshing instrument tokens for {exchange}...")
            instruments = kite.instruments(exchange)
            self._instrument_tokens = {i['tradingsymbol']: i['instrument_token'] for i in instruments}
            logger.info(f"Cached {len(self._instrument_tokens)} tokens for {exchange}.")
        except Exception as e:
            logger.error(f"Error loading instruments: {e}")

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
            # Format: ["NSE:RELIANCE", "NSE:TCS"]
            instruments = [f"NSE:{s}" if ":" not in s else s for s in symbols]
            # Kite limit is usually 500 per call, which is fine for our watchlist
            return kite.quote(instruments)
        except Exception as e:
            logger.error(f"Error fetching bulk quotes: {e}")
            return {}

    def get_historical(self, symbol: str, from_date, to_date, interval="day", exchange="NSE"):
        """Fetches historical OHLC data from Kite with token caching."""
        kite = self.get_client()
        if not kite or not settings.ZERODHA_ACCESS_TOKEN:
            return []
        
        try:
            # 1. Check cache first
            token = self._instrument_tokens.get(symbol)
            
            # 2. If not in cache, refresh cache
            if not token:
                self._load_instrument_tokens(exchange)
                token = self._instrument_tokens.get(symbol)
            
            if not token:
                logger.error(f"Instrument token not found for {symbol} after refresh.")
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
