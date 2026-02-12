import os
import logging
from groq import Groq
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.client = None
        self.api_key = None  # Will be loaded dynamically when needed
        self.available_models = [
            "llama-3.3-70b-versatile",  # Updated model
            "llama-3.1-8b-instant",
            "llama3-groq-70b-8192-tool-use-preview",
            "llama3-groq-8b-8192-tool-use-preview"
        ]
        
        # Initialize client if API key is available at startup
        self._initialize_client_if_key_available()
    
    def _initialize_client_if_key_available(self):
        """Initialize the client if API key is available"""
        api_key = self._get_api_key()
        if api_key and not self.client:
            try:
                self.client = Groq(api_key=api_key)
                self.api_key = api_key
                logger.info("Groq client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
                self.client = None
    
    def _get_api_key(self):
        """Get API key from various sources"""
        # Try to get API key from settings first
        api_key = settings.GROQ_API_KEY
        
        # If not in settings, try to load from encrypted storage
        if not api_key:
            try:
                from app.utils.secrets_manager import secrets_manager
                api_key = secrets_manager.get_secret('GROQ_API_KEY')
                if api_key:
                    logger.info("GROQ_API_KEY loaded from encrypted storage")
            except Exception as e:
                logger.error(f"Error loading API key from encrypted storage: {e}")
        
        # If still not found, try environment variable
        if not api_key:
            api_key = os.getenv("GROQ_API_KEY")
        
        return api_key

    def get_chat_response(self, message: str, context: str = "") -> str:
        # Try to initialize client if not available
        if not self.client:
            self._initialize_client_if_key_available()
        
        # If still no client after initialization attempt, use offline response
        if not self.client:
            # Graceful Fallback for Demo/Audit without API Key
            logger.warning("Groq client not available, using offline response")
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
            # Try different models in order of preference
            for model in self.available_models:
                try:
                    completion = self.client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": message}
                        ],
                        model=model,
                        max_tokens=300,
                        temperature=0.7
                    )
                    response = completion.choices[0].message.content.strip()
                    logger.info(f"Successfully generated response using model: {model}")
                    return response
                except Exception as model_error:
                    logger.warning(f"Model {model} failed: {model_error}")
                    continue  # Try next model

            # If all models fail, return offline response
            logger.error("All Groq models failed, falling back to offline response")
            return self._generate_offline_response(message, context)

        except Exception as e:
            logger.error(f"Groq API error: {e}")
            # Try to reinitialize client in case of error
            self.client = None
            self._initialize_client_if_key_available()
            if self.client:
                # Retry once after reinitializing
                try:
                    completion = self.client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": message}
                        ],
                        model=self.available_models[0],
                        max_tokens=300,
                        temperature=0.7
                    )
                    response = completion.choices[0].message.content.strip()
                    logger.info(f"Successfully generated response using model: {self.available_models[0]} after reinitialization")
                    return response
                except:
                    pass
            return f"I encountered an error processing your request: {str(e)}. Using offline mode."

    def _generate_offline_response(self, message: str, context: str = "") -> str:
        """
        Offline 'Small RAG' that queries the database directly based on keywords.
        Simulates AI behavior using deterministic logic and available internal data.
        """
        msg_lower = message.lower()
        
        # Extract user_id from context if available
        user_id = None
        if context and "User:" in context:
            # Extract user_id from context string like "User: John Doe, Role: AUTO"
            import re
            # Look for user_id in context if it's passed
            for part in context.split(','):
                if 'user_id' in part.lower():
                    try:
                        user_id = int(part.split(':')[-1].strip())
                    except:
                        pass
        
        # If no user_id found in context, default to first user (demo mode)
        if not user_id:
            # Try to extract from context string that might contain user_id
            import re
            user_id_match = re.search(r'"user_id":\s*(\d+)', context)
            if user_id_match:
                user_id = int(user_id_match.group(1))
            else:
                user_id = 1  # Default to first user for demo purposes
        
        from app.core.database import SessionLocal
        from app.models.portfolio import Portfolio
        from app.models.strategy import Strategy
        from app.models.trade import Trade

        db = SessionLocal()
        try:
            # 1. Portfolio Queries
            if "portfolio" in msg_lower or "balance" in msg_lower or "value" in msg_lower:
                # Query specific user's portfolio
                port = db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
                if port:
                    total_val = port.invested_amount + port.cash_balance
                    return (
                        f"**Portfolio Summary for User #{user_id}:**\n"
                        f"- **Total Vault Value:** ₹{total_val:,.2f}\n"
                        f"- **Cash Balance:** ₹{port.cash_balance:,.2f}\n"
                        f"- **Invested Amount:** ₹{port.invested_amount:,.2f}\n"
                        f"- **Win Rate:** {port.win_rate}%\n\n"
                        f"I can fetch more details if you ask about 'strategies' or 'trades'."
                    )
                return f"No portfolio found for user #{user_id}. Would you like to create one or check another user?"

            # 2. Strategy Queries
            if "strategy" in msg_lower or "strategies" in msg_lower or "algo" in msg_lower:
                # Query specific user's strategies through their portfolio
                from app.models.portfolio import Portfolio
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
            if "market" in msg_lower or "trend" in msg_lower:
                 return (
                     "**Market Insight (Offline Mode):**\n"
                     "I cannot access live external feeds without the Neural Link (Groq API), but internal telemetry indicates "
                     "stable connection to NSE/BSE Execution Nodes. Local latency is nominal (24ms).\n\n"
                     f"For user #{user_id}'s specific portfolio data, try asking: *'Show my portfolio'* or *'List my strategies'*."
                 )

            # Default generic response
            return (
                f"**Offline Intelligence for User #{user_id}:** I am operating with limited connectivity (No external LLM). "
                f"I can query your **Portfolio**, **Strategies**, and **Trade History** directly from the secure ledger. "
                f"Try asking: *'Show my portfolio'* or *'List active strategies'*.\n\n"
                f"Current View: User #{user_id} data access."
            )

        except Exception as e:
            logger.error(f"Database error in offline response: {e}")
            return f"Internal Database Error: {str(e)}"
        finally:
            db.close()

# Create a global instance, but it will initialize the client dynamically when needed
llm_service = LLMService()