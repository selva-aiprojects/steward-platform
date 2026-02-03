from typing import Any, Dict
from app.agents.base import BaseAgent

class StrategyAgent(BaseAgent):
    """
    Responsible for pure Technical/Fundamental Analysis logic.
    
    Responsibilities:
    - Analyze market data.
    - Apply trading strategies (e.g., MACD crossover, RSI).
    - output raw signals (BUY_SIGNAL, SELL_SIGNAL, HOLD).
    - DOES NOT DECIDE to trade (that's TradeDecisionAgent).
    """
    
    def __init__(self):
        super().__init__(name="StrategyAgent")

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        import os
        import json
        
        market_data = context.get("market_data", {})
        user_profile = context.get("user_profile", {})
        
        prompt = f"""
        Analyze the following market data and provide a trading signal (BUY, SELL, or HOLD).
        Market Data: {json.dumps(market_data)}
        User Risk Profile: {user_profile.get('risk_tolerance')}
        
        Return ONLY a JSON object:
        {{
            "signal": "BUY|SELL|HOLD",
            "confidence": 0.0-1.0,
            "rationale": "short explanation",
            "strategy_used": "Name of strategy"
        }}
        """
        
        try:
            from groq import Groq
            client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
            
            system_prompt = "You are the StockSteward AI Senior Analyst. Provide high-precision algorithmic trading signals based on market data and technical indicators. Always justify with institutional-grade rationale."
            
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"}
            )
            analysis = json.loads(chat_completion.choices[0].message.content)
        except Exception as e:
            # Fallback to deterministic logic if Groq fails
            analysis = {
                "signal": "HOLD", 
                "confidence": 0.5, 
                "rationale": f"AI model offline ({str(e)})", 
                "strategy_used": "Safety-Fallback"
            }
            
        return {
            "strategy_signal": {
                "strategy_used": analysis.get("strategy_used"),
                "signal": analysis.get("signal"),
                "confidence": analysis.get("confidence"),
                "rationale": analysis.get("rationale"),
                "regime_detected": market_data.get("trend")
            }
        }
