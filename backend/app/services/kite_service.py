from kiteconnect import KiteConnect
from app.core.config import settings
import logging
import time
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class KiteService:
    _instance = None
    _kite = None
    _instrument_tokens = {} # Cache for instrument tokens {symbol: token}

    # Rate limiting tracking
    _last_api_call_time = 0
    _min_api_interval = 0.2  # Minimum 200ms between API calls to respect rate limits

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KiteService, cls).__new__(cls)
        return cls._instance

    def _enforce_rate_limit(self):
        """Enforce minimum time between API calls to respect rate limits."""
        current_time = time.time()
        time_since_last_call = current_time - self._last_api_call_time

        if time_since_last_call < self._min_api_interval:
            sleep_time = self._min_api_interval - time_since_last_call
            time.sleep(sleep_time)

        self._last_api_call_time = time.time()

    def get_client(self):
        if self._kite is None:
            if not settings.ZERODHA_API_KEY:
                logger.warning("ZERODHA_API_KEY not configured.")
                return None

            try:
                self._kite = KiteConnect(api_key=settings.ZERODHA_API_KEY)

                if settings.ZERODHA_ACCESS_TOKEN:
                    self._kite.set_access_token(settings.ZERODHA_ACCESS_TOKEN)
                    logger.info("Kite client initialized with access token.")
                else:
                    logger.warning("ZERODHA_ACCESS_TOKEN not set. Manual authentication required.")

            except Exception as e:
                logger.error(f"Error initializing KiteConnect client: {e}")
                return None

        return self._kite

    def _load_instrument_tokens(self, exchange="NSE"):
        """Downloads and caches instrument tokens for an exchange."""
        kite = self.get_client()
        if not kite or not settings.ZERODHA_ACCESS_TOKEN:
            logger.warning("Cannot load instruments: Kite client not initialized or no access token.")
            return

        try:
            self._enforce_rate_limit()
            logger.info(f"Refreshing instrument tokens for {exchange}...")
            instruments = kite.instruments(exchange)
            self._instrument_tokens = {i['tradingsymbol']: i['instrument_token'] for i in instruments}
            logger.info(f"Cached {len(self._instrument_tokens)} tokens for {exchange}.")
        except Exception as e:
            logger.error(f"Error loading instruments for {exchange}: {e}")

    def get_quote(self, symbol: str, exchange: str = "NSE") -> Optional[Dict[str, Any]]:
        kite = self.get_client()
        if not kite or not settings.ZERODHA_ACCESS_TOKEN:
            logger.warning(f"Cannot fetch quote for {symbol}: Kite client not initialized or no access token.")
            return None

        try:
            self._enforce_rate_limit()
            instrument = f"{exchange}:{symbol}"
            quotes = kite.quote([instrument])
            return quotes.get(instrument)
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            # Return a mock response to prevent complete failure
            return {
                'instrument_token': 0,
                'last_price': 0,
                'change': 0,
                'exchange': exchange,
                'tradingsymbol': symbol,
                'error': str(e),
                'timestamp': None
            }

    def get_quotes(self, symbols: List[str]) -> Dict[str, Any]:
        """Fetches quotes for multiple symbols at once."""
        kite = self.get_client()
        if not kite or not settings.ZERODHA_ACCESS_TOKEN:
            logger.warning("Cannot fetch quotes: Kite client not initialized or no access token.")
            return {}

        try:
            self._enforce_rate_limit()
            # Format: ["NSE:RELIANCE", "NSE:TCS"]
            instruments = [f"NSE:{s}" if ":" not in s else s for s in symbols]
            # Limit to 500 instruments per call to respect Kite limits
            if len(instruments) > 500:
                logger.warning(f"Too many instruments requested ({len(instruments)}), limiting to 500")
                instruments = instruments[:500]

            return kite.quote(instruments)
        except Exception as e:
            logger.error(f"Error fetching bulk quotes: {e}")
            # Return a mock response to prevent complete failure
            return {f"NSE:{s}": {
                'instrument_token': 0,
                'last_price': 0,
                'change': 0,
                'exchange': 'NSE',
                'tradingsymbol': s,
                'error': str(e),
                'timestamp': None
            } for s in symbols}

    def get_historical(self, symbol: str, from_date, to_date, interval="day", exchange="NSE") -> List[Dict[str, Any]]:
        """Fetches historical OHLC data from Kite with token caching."""
        kite = self.get_client()
        if not kite or not settings.ZERODHA_ACCESS_TOKEN:
            logger.warning(f"Cannot fetch historical data for {symbol}: Kite client not initialized or no access token.")
            return []

        try:
            self._enforce_rate_limit()
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

    def generate_session(self, request_token: str) -> Optional[Dict[str, Any]]:
        kite = self.get_client()
        if not kite or not settings.ZERODHA_API_SECRET:
            logger.warning("Cannot generate session: Kite client not initialized or no API secret.")
            return None

        try:
            self._enforce_rate_limit()
            data = kite.generate_session(request_token, api_secret=settings.ZERODHA_API_SECRET)
            self._kite.set_access_token(data["access_token"])
            logger.info(f"Session generated successfully for user: {data.get('user_id', 'Unknown')}")
            return data
        except Exception as e:
            logger.error(f"Error generating session: {e}")
            return None

    def validate_connection(self) -> bool:
        """Validate if the Kite connection is working properly."""
        kite = self.get_client()
        if not kite or not settings.ZERODHA_ACCESS_TOKEN:
            return False

        try:
            self._enforce_rate_limit()
            # Try to fetch profile to validate connection
            profile = kite.profile()
            logger.info(f"Kite connection validated for user: {profile.get('user_name', 'Unknown')}")
            return True
        except Exception as e:
            logger.error(f"Kite connection validation failed: {e}")
            return False

kite_service = KiteService()
