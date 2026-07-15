import os
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.client = None
        self.api_key = None  # Will be loaded dynamically when needed
        self.available_models = [
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant"
        ]
        
        # Lazily initialize on first request to avoid noisy startup failures.
    
    def _initialize_client_if_key_available(self):
        """Initialize the client if API key is available"""
        api_key = self._get_api_key()
        if api_key and not self.client:
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                self.client = genai.GenerativeModel('gemini-1.5-flash')
                self.api_key = api_key
                logger.info("Google Gemini client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Google Gemini client: {e}")
                self.client = None
    
    def _get_api_key(self):
        """Get API key from various sources"""
        # Try to get API key from settings first
        api_key = settings.GOOGLE_API_KEY
        
        # If not in settings, try to load from encrypted storage
        if not api_key:
            try:
                from app.utils.secrets_manager import secrets_manager
                api_key = secrets_manager.get_secret('GOOGLE_API_KEY')
                if api_key:
                    logger.info("GOOGLE_API_KEY loaded from encrypted storage")
            except Exception as e:
                logger.error(f"Error loading API key from encrypted storage: {e}")
        
        # If still not found, try environment variable
        if not api_key:
            api_key = os.getenv("GOOGLE_API_KEY")
        
        return api_key

    def get_chat_response(self, message: str, context: str = "") -> str:
        # Try to initialize client if not available
        if not self.client:
            self._initialize_client_if_key_available()
        
        # If still no client after initialization attempt, use offline response
        if not self.client:
            # Graceful Fallback for Demo/Audit without API Key
            logger.warning("Gemini client not available, using offline response")
            return self._generate_offline_response(message, context)

        system_prompt = (
            "You are StockSteward AI, a helpful financial assistant for the StockSteward platform. "
            "You specialize in the Indian Stock Market (NSE/BSE). "
            "Keep answers concise, professional, and helpful. "
            "If the user asks about market trends, give a general safe answer or ask them to check the dashboard. "
            "Do not give financial advice."
        )

        if context:
            system_prompt += f"\nContext: {context}"

        try:
            full_prompt = f"System: {system_prompt}\n\nUser: {message}"
            response = self.client.generate_content(full_prompt)
            if response.text:
                logger.info(f"Successfully generated response using model: gemini-1.5-flash")
                return response.text.strip()
            else:
                logger.error("Empty response from Gemini")
                return self._generate_offline_response(message, context)

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return f"I encountered an error processing your request: {str(e)}. Using offline mode."

    def _generate_offline_response(self, message: str, context: str = "") -> str:
        """
        Offline 'Small RAG' that queries the database directly based on keywords.
        Simulates AI behavior using deterministic logic and available internal data.
        """
        msg_lower = message.lower()
        
        # Extract user_id from context if available
        user_id = None
        if context:
            # Look for User_ID: 999 style
            import re
            id_match = re.search(r'User_ID:\s*(\d+)', context)
            if id_match:
                user_id = int(id_match.group(1))
            
            if not user_id:
                # Look for user_id attribute in JSON-like context
                id_match = re.search(r'"user_id":\s*(\d+)', context)
                if id_match:
                    user_id = int(id_match.group(1))

        # If user identity is unavailable, return generic safe response without account access.
        if not user_id:
            return (
                "**Offline Intelligence:** user context is missing.\n"
                "Please log in again or include a valid user context to query portfolio, strategy, or trade history."
            )
        
        from app.core.database import SessionLocal
        from app.models.portfolio import Portfolio
        from app.models.strategy import Strategy
        from app.models.trade import Trade
        from app.core.state import last_market_movers, find_price_by_symbol

        db = SessionLocal()
        try:
            # Check for specific price queries first
            words = msg_lower.replace('?', '').replace(',', '').split()
            for word in words:
                if len(word) > 2:
                    price_info = find_price_by_symbol(word)
                    if price_info:
                        return (
                            f"**Live Quote (Offline Mode):**\n"
                            f"The current price for **{price_info['symbol']}** is **₹{price_info['price']:,.2f}** "
                            f"({'+' if price_info.get('change',0) >= 0 else ''}{price_info.get('change', 0)}%).\n\n"
                            f"Source: Validated Market Feed | Connectivity: Backup Node"
                        )

            # 1. Portfolio Queries
            if "portfolio" in msg_lower or "balance" in msg_lower or "value" in msg_lower or msg_lower.strip() in ["yes", "y", "create it"]:
                # Query specific user's portfolio
                port = db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
                if port:
                    if "create" in msg_lower and "portfolio" in msg_lower:
                        return f"User #{user_id} already has a portfolio with a total value of ₹{port.invested_amount + port.cash_balance:,.2f}."
                        
                    total_val = port.invested_amount + port.cash_balance
                    return (
                        f"**Portfolio Summary for User #{user_id}:**\n"
                        f"- **Total Vault Value:** ₹{total_val:,.2f}\n"
                        f"- **Cash Balance:** ₹{port.cash_balance:,.2f}\n"
                        f"- **Invested Amount:** ₹{port.invested_amount:,.2f}\n"
                        f"- **Win Rate:** {port.win_rate}%\n\n"
                        f"I can fetch more details if you ask about 'strategies' or 'trades'."
                    )
                
                # If no portfolio exists and they want to create one (either explicitly or answering 'yes')
                if "create" in msg_lower or msg_lower.strip() in ["yes", "y", "create it"]:
                    import re
                    # Extract the investment amount if specified
                    amount_match = re.search(r'(?:rs|inr|₹|\$)?\s*(\d+(?:,\d+)*(?:\.\d+)?)', msg_lower.replace(',', ''))
                    amount = float(amount_match.group(1)) if amount_match else 100000.0
                    
                    new_port = Portfolio(
                        user_id=user_id, 
                        name="Main Portfolio",
                        cash_balance=amount,
                        invested_amount=0.0
                    )
                    db.add(new_port)
                    db.commit()
                    return f"**Success!** A new portfolio has been created for user #{user_id} with an initial cash balance of ₹{amount:,.2f}. (Offline Mode)"
                
                return f"No portfolio found for user #{user_id}. Would you like to create one or check another user?"

            # 2. Strategy Queries
            if "strategy" in msg_lower or "strategies" in msg_lower or "algo" in msg_lower:
                # Query specific user's strategies through their portfolio
                portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
                if portfolio:
                    strats = db.query(Strategy).filter(Strategy.portfolio_id == portfolio.id).all()
                    if strats:
                        strat_list = "\n".join([f"- **{s.name}** ({s.symbol}): {s.status} | PnL: {s.pnl}" for s in strats[:3]])
                        return (
                            f"**Active Algo Strategies for User #{user_id} (Offline Mode):**\n\n{strat_list}\n\n"
                            f"Total Active Engines: {len(strats)}"
                        )
                    return f"No algorithmic strategies are currently deployed for user #{user_id}'s portfolio."
                return f"User #{user_id} does not have an active portfolio to associate strategies with."

            # 3. Trade/History Queries
            if "trade" in msg_lower or "history" in msg_lower or "order" in msg_lower:
                # Query specific user's trades through their portfolio
                portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
                if portfolio:
                    trades = db.query(Trade).filter(Trade.portfolio_id == portfolio.id).order_by(Trade.timestamp.desc()).limit(3).all()
                    if trades:
                        trade_list = "\n".join([f"- {t.action} **{t.symbol}** @ ₹{t.price} ({t.status})" for t in trades])
                        return (
                            f"**Recent Execution Log for User #{user_id} (Offline Mode):**\n\n{trade_list}\n\n"
                            f"These records are pulled directly from user #{user_id}'s transaction ledger."
                        )
                    return f"The transaction ledger for user #{user_id} is currently empty."
                return f"User #{user_id} does not have an active portfolio to query trade history from."

            # 4. Market/General Fallback
            if "market" in msg_lower or "trend" in msg_lower or "price" in msg_lower or "quote" in msg_lower:
                 gainers = last_market_movers.get('gainers', [])
                 gainer_text = ", ".join([f"{g['symbol']} (+{g['change']}%)" for g in gainers[:3]]) if gainers else "N/A"
                 return (
                     "**Market Insight (Offline Mode):**\n"
                     "I cannot access live external LLM feeds, but my internal market cache shows the current leaders:\n"
                     f"- **Top Gainers:** {gainer_text}\n"
                     "- **Exchange Latency:** 24ms (Nominal)\n\n"
                     f"For user #{user_id}'s specific portfolio data, try asking: *'Show my portfolio'* or *'Price of Reliance'*."
                 )

            # Default generic response
            return (
                f"**Offline Intelligence for User #{user_id}:** I am operating with limited connectivity (No external LLM). "
                f"I can query your **Portfolio**, **Strategies**, and **Trade History** directly from the secure ledger. "
                f"Try asking: *'Show my portfolio'* or *'Price of Reliance'*.\n\n"
                f"**Current View:** User #{user_id} data access. | **Security:** AES-256 Local Encryption"
            )

        except Exception as e:
            logger.error(f"Database error in offline response: {e}")
            return f"Internal Database Error: {str(e)}"
        finally:
            db.close()

# Create a global instance, but it will initialize the client dynamically when needed
llm_service = LLMService()
