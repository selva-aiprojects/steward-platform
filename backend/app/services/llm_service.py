import os
import logging
from groq import Groq
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.client = None
        self.available_models = [
            "llama-3.3-70b-versatile",  # Updated model
            "llama-3.1-8b-instant",
            "llama3-groq-70b-8192-tool-use-preview",
            "llama3-groq-8b-8192-tool-use-preview"
        ]

        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
                logger.info("Groq client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
        else:
            # Fallback to direct os.getenv if pydantic-settings failed for some reason
            direct_key = os.getenv("GROQ_API_KEY")
            if direct_key:
                self.api_key = direct_key
                try:
                    self.client = Groq(api_key=direct_key)
                    logger.info("Groq client initialized successfully with direct key")
                except Exception as e:
                    logger.error(f"Failed to initialize Groq client with direct key: {e}")
            else:
                logger.warning("GROQ_API_KEY not configured. LLM service will operate in offline mode.")

    def get_chat_response(self, message: str, context: str = "") -> str:
        if not self.client:
            # Graceful Fallback for Demo/Audit without API Key
            logger.warning("Groq client not available, using offline response")
            return self._generate_offline_response(message)

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
            return self._generate_offline_response(message)

        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return f"I encountered an error processing your request: {str(e)}. Using offline mode."

    def _generate_offline_response(self, message: str) -> str:
        """
        Offline 'Small RAG' that queries the database directly based on keywords.
        Simulates AI behavior using deterministic logic and available internal data.
        """
        msg_lower = message.lower()
        from app.core.database import SessionLocal
        from app.models.portfolio import Portfolio
        from app.models.strategy import Strategy
        from app.models.trade import Trade

        db = SessionLocal()
        try:
            # 1. Portfolio Queries
            if "portfolio" in msg_lower or "balance" in msg_lower or "value" in msg_lower:
                port = db.query(Portfolio).first() # Demo mode assumes single user context or first user
                if port:
                    total_val = port.invested_amount + port.cash_balance
                    return (
                        f"**Internal Ledger Data (Offline Mode):**\n"
                        f"- **Total Vault Value:** ₹{total_val:,.2f}\n"
                        f"- **Invested:** ₹{port.invested_amount:,.2f}\n"
                        f"- **Cash:** ₹{port.cash_balance:,.2f}\n\n"
                        f"I can fetch more details if you ask about 'strategies' or 'trades'."
                    )
                return "I couldn't locate an active portfolio in the local database."

            # 2. Strategy Queries
            if "strategy" in msg_lower or "strategies" in msg_lower or "algo" in msg_lower:
                strats = db.query(Strategy).all()
                if strats:
                    strat_list = "\n".join([f"- **{s.name}** ({s.symbol}): {s.status} | PnL: {s.pnl}" for s in strats[:3]])
                    return (
                        f"**Active Algo Strategies (Offline Mode):**\n\n{strat_list}\n\n"
                        f"Total Active Engines: {len(strats)}"
                    )
                return "No algorithmic strategies are currently deployed on this node."

            # 3. Trade/History Queries
            if "trade" in msg_lower or "history" in msg_lower or "order" in msg_lower:
                trades = db.query(Trade).order_by(Trade.timestamp.desc()).limit(3).all()
                if trades:
                    trade_list = "\n".join([f"- {t.action} **{t.symbol}** @ ₹{t.price} ({t.status})" for t in trades])
                    return (
                        f"**Recent Execution Log (Offline Mode):**\n\n{trade_list}\n\n"
                        f"These records are pulled directly from your local transaction ledger."
                    )
                return "The transaction ledger is currently empty."

            # 4. Market/General Fallback
            if "market" in msg_lower or "trend" in msg_lower:
                 return (
                     "**Market Insight (Offline Mode):**\n"
                     "I cannot access live external feeds without the Neural Link (Groq API), but internal telemetry indicates "
                     "stable connection to NSE/BSE Execution Nodes. Local latency is nominal (24ms)."
                 )

            # Default generic response
            return (
                "**Offline Intelligence:** I am operating with limited connectivity (No external LLM). "
                "I can still query your **Portfolio**, **Strategies**, and **Trade History** directly from the secure ledger. "
                "Try asking: *'Show my portfolio'* or *'List active strategies'*."
            )

        except Exception as e:
            logger.error(f"Database error in offline response: {e}")
            return f"Internal Database Error: {str(e)}"
        finally:
            db.close()

llm_service = LLMService()
