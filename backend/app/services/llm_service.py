import os
from groq import Groq
from app.core.config import settings

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = None
        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                print(f"Failed to initialize Groq client: {e}")

    def get_chat_response(self, message: str, context: str = "") -> str:
        if not self.client:
            return "AI Service is currently unavailable (Groq API Key missing)."

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
            completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                model="llama-3.1-8b-instant",
                max_tokens=300
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            return f"I encountered an error processing your request: {str(e)}"

llm_service = LLMService()
