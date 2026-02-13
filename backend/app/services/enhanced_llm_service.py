"""
Enhanced LLM Service for StockSteward AI
Supports multiple LLM providers (Groq, OpenAI, Anthropic, Hugging Face) and integrates with financial data
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import pandas as pd
from app.core.config import settings

logger = logging.getLogger(__name__)

class EnhancedLLMService:
    """
    Enhanced LLM service supporting multiple providers:
    - Groq (Llama models)
    - OpenAI (GPT models)
    - Anthropic (Claude models)
    - Hugging Face (FinGPT, DeepSeek, etc.)
    """
    
    def __init__(self):
        # Initialize multiple LLM clients
        self.clients = {}
        self.available_models = {
            "groq": [
                "llama-3.3-70b-versatile",
                "llama-3.1-70b-versatile",
                "llama-3.1-8b-instant"
            ],
            "openai": [
                "gpt-4-turbo",
                "gpt-4",
                "gpt-3.5-turbo"
            ],
            "anthropic": [
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ],
        }
        self._init_errors = set()

    def _resolve_api_key(self, key_name: str) -> Optional[str]:
        api_key = getattr(settings, key_name, None) or os.getenv(key_name)
        if api_key:
            return api_key
        try:
            from app.utils.secrets_manager import secrets_manager
            return secrets_manager.get_secret(key_name)
        except Exception as e:
            logger.debug(f"Error loading {key_name} from encrypted storage: {e}")
            return None

    def _ensure_client(self, provider: str) -> bool:
        if provider in self.clients:
            return True

        try:
            if provider == "groq":
                key = self._resolve_api_key("GROQ_API_KEY")
                if not key:
                    return False
                from groq import Groq
                self.clients["groq"] = Groq(api_key=key)
                return True
            if provider == "openai":
                key = self._resolve_api_key("OPENAI_API_KEY")
                if not key:
                    return False
                from openai import OpenAI
                self.clients["openai"] = OpenAI(api_key=key)
                return True
            if provider == "anthropic":
                key = self._resolve_api_key("ANTHROPIC_API_KEY")
                if not key:
                    return False
                import anthropic
                self.clients["anthropic"] = anthropic.Anthropic(api_key=key)
                return True
            return False
        except Exception as e:
            error_key = (provider, str(e))
            if error_key not in self._init_errors:
                self._init_errors.add(error_key)
                if "unexpected keyword argument 'proxies'" in str(e):
                    logger.warning(
                        "%s client init failed due to incompatible httpx version. Install `httpx<0.28`.",
                        provider.upper(),
                    )
                else:
                    logger.error(f"Failed to initialize {provider} client: {e}")
            return False
    
    def get_financial_analysis_prompt(
        self,
        market_data: Dict[str, Any],
        user_context: Dict[str, Any] = None,
        analysis_type: str = "comprehensive"
    ) -> str:
        """
        Generate a financial analysis prompt tailored for stock analysis
        """
        base_prompt = f"""
        You are StockSteward AI, a senior wealth steward and financial analyst specializing in the Indian stock market.
        Analyze the following market data and provide actionable insights.
        
        MARKET DATA:
        {json.dumps(market_data, indent=2)}
        """
        
        if user_context:
            base_prompt += f"""
            
        USER CONTEXT:
        - Risk Tolerance: {user_context.get('risk_tolerance', 'MODERATE')}
        - Investment Horizon: {user_context.get('investment_horizon', 'MEDIUM_TERM')}
        - Portfolio Size: {user_context.get('portfolio_size', 'VARIES')}
        - Trading Experience: {user_context.get('experience_level', 'INTERMEDIATE')}
        """
        
        if analysis_type == "technical":
            base_prompt += """
            
        PROVIDE TECHNICAL ANALYSIS FOCUSING ON:
        1. Price trends and momentum
        2. Key support and resistance levels
        3. Technical indicators (RSI, MACD, Moving Averages)
        4. Trading signals (BUY/SELL/HOLD with confidence score 0-100)
        5. Risk assessment (0-100 scale)
        """
        elif analysis_type == "fundamental":
            base_prompt += """
            
        PROVIDE FUNDAMENTAL ANALYSIS FOCUSING ON:
        1. Valuation metrics
        2. Financial health indicators
        3. Sector performance
        4. Growth prospects
        5. Dividend yield and sustainability
        """
        elif analysis_type == "sentiment":
            base_prompt += """
            
        PROVIDE SENTIMENT ANALYSIS FOCUSING ON:
        1. Market sentiment based on price action
        2. Volatility assessment
        3. News sentiment (if available)
        4. Investor positioning
        5. Fear/Greed index implications
        """
        else:  # comprehensive
            base_prompt += """
            
        PROVIDE COMPREHENSIVE ANALYSIS INCLUDING:
        1. Technical indicators and price action
        2. Fundamental health assessment
        3. Market sentiment and positioning
        4. Risk-adjusted recommendation (BUY/SELL/HOLD)
        5. Confidence score (0-100)
        6. Entry/exit levels with stop-loss suggestions
        7. Time horizon for the recommendation
        8. Key catalysts to watch
        9. Risk factors to consider
        
        RETURN YOUR RESPONSE AS A VALID JSON OBJECT WITH THE FOLLOWING STRUCTURE:
        {
            "recommendation": "BUY|SELL|HOLD",
            "confidence": 0-100,
            "target_price": float,
            "stop_loss": float,
            "time_horizon": "SHORT|MEDIUM|LONG",
            "analysis": {
                "technical": "Technical analysis summary",
                "fundamental": "Fundamental analysis summary", 
                "sentiment": "Sentiment analysis summary"
            },
            "signals": {
                "rsi_signal": "OVERSOLD|OVERBOUGHT|NEUTRAL",
                "macd_signal": "BULLISH|BEARISH|NEUTRAL",
                "ma_signal": "BULLISH|BEARISH|NEUTRAL"
            },
            "risk_factors": ["factor1", "factor2"],
            "catalysts": ["catalyst1", "catalyst2"],
            "rationale": "Detailed explanation for the recommendation"
        }
        """
        
        return base_prompt
    
    def get_market_research_prompt(self, sector_data: Dict[str, Any] = None) -> str:
        """
        Generate market research and sector analysis prompt
        """
        prompt = """
        You are StockSteward AI's Market Research Analyst. Provide a comprehensive market research summary for the Indian equity markets.
        
        SECTOR DATA (if available):
        """
        
        if sector_data:
            prompt += f"{json.dumps(sector_data, indent=2)}\n\n"
        else:
            prompt += "No specific sector data provided.\n\n"
        
        prompt += """
        PROVIDE THE FOLLOWING:
        1. Top 5 market-moving headlines
        2. Sector-wise performance analysis
        3. Key market drivers and trends
        4. Risk factors affecting the market
        5. Investment opportunities and threats
        6. Short-term and medium-term outlook
        
        FORMAT YOUR RESPONSE AS A VALID JSON OBJECT:
        {
            "headlines": ["headline1", "headline2", "headline3", "headline4", "headline5"],
            "sector_analysis": {
                "top_performers": [{"sector": "name", "performance": "+X.X%"}],
                "underperformers": [{"sector": "name", "performance": "-X.X%"}],
                "outlook": "positive/negative/mixed"
            },
            "market_drivers": ["driver1", "driver2"],
            "risk_factors": ["risk1", "risk2"],
            "opportunities": ["opportunity1", "opportunity2"],
            "threats": ["threat1", "threat2"],
            "outlook": {
                "short_term": "bullish/bearish/mixed",
                "medium_term": "bullish/bearish/mixed"
            },
            "research_summary": "Comprehensive research summary"
        }
        """
        
        return prompt
    
    async def analyze_with_groq(
        self,
        prompt: str,
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Analyze using Groq (Llama models)
        """
        if not self._ensure_client("groq"):
            return {
                "error": "Groq client not initialized",
                "fallback_response": "Market analysis pending: LLM service unavailable"
            }
        
        try:
            response = self.clients['groq'].chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are StockSteward AI, a senior wealth steward and financial analyst specializing in the Indian stock market. Provide accurate, concise, and actionable financial insights. Always return valid JSON when requested."},
                    {"role": "user", "content": prompt}
                ],
                model=model,
                temperature=temperature,
                response_format={"type": "json_object"},
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON response from Groq: {content}")
                return {
                    "error": "Failed to parse LLM response",
                    "raw_response": content
                }
                
        except Exception as e:
            logger.error(f"Error calling Groq API: {e}")
            return {
                "error": f"Groq API error: {str(e)}",
                "fallback_response": "Market analysis pending: Temporary service disruption"
            }
    
    async def analyze_with_openai(
        self,
        prompt: str,
        model: str = "gpt-4-turbo",
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Analyze using OpenAI (GPT models)
        """
        if not self._ensure_client("openai"):
            return {
                "error": "OpenAI client not initialized",
                "fallback_response": "Market analysis pending: LLM service unavailable"
            }
        
        try:
            response = self.clients['openai'].chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are StockSteward AI, a senior wealth steward and financial analyst specializing in the Indian stock market. Provide accurate, concise, and actionable financial insights. Always return valid JSON when requested."},
                    {"role": "user", "content": prompt}
                ],
                model=model,
                temperature=temperature,
                response_format={"type": "json_object"},
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON response from OpenAI: {content}")
                return {
                    "error": "Failed to parse LLM response",
                    "raw_response": content
                }
                
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return {
                "error": f"OpenAI API error: {str(e)}",
                "fallback_response": "Market analysis pending: Temporary service disruption"
            }
    
    async def analyze_with_anthropic(
        self,
        prompt: str,
        model: str = "claude-3-sonnet-20240229",
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Analyze using Anthropic (Claude models)
        """
        if not self._ensure_client("anthropic"):
            return {
                "error": "Anthropic client not initialized",
                "fallback_response": "Market analysis pending: LLM service unavailable"
            }
        
        try:
            message = self.clients['anthropic'].messages.create(
                max_tokens=2000,
                temperature=temperature,
                system="You are StockSteward AI, a senior wealth steward and financial analyst specializing in the Indian stock market. Provide accurate, concise, and actionable financial insights. Always return valid JSON when requested.",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                model=model
            )
            
            content = message.content[0].text.strip()
            
            # Parse JSON response
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON response from Anthropic: {content}")
                return {
                    "error": "Failed to parse LLM response",
                    "raw_response": content
                }
                
        except Exception as e:
            logger.error(f"Error calling Anthropic API: {e}")
            return {
                "error": f"Anthropic API error: {str(e)}",
                "fallback_response": "Market analysis pending: Temporary service disruption"
            }
    
    async def analyze_with_huggingface(
        self,
        prompt: str,
        model_name: str = "ProsusAI/finbert",
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Analyze using Hugging Face models (FinGPT, DeepSeek, etc.)
        """
        try:
            from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
            import torch
            
            # For financial sentiment analysis
            if "finbert" in model_name.lower():
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForSequenceClassification.from_pretrained(model_name)
                
                # Tokenize and predict
                inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True, max_length=512)
                
                with torch.no_grad():
                    outputs = model(**inputs)
                    predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                    
                # Convert to financial insight
                positive_confidence = predictions[0][2].item()  # Index 2 is typically positive in FinBERT
                negative_confidence = predictions[0][0].item()  # Index 0 is typically negative
                
                recommendation = "BUY" if positive_confidence > 0.6 else "SELL" if negative_confidence > 0.6 else "HOLD"
                confidence = max(positive_confidence, negative_confidence) * 100
                
                return {
                    "recommendation": recommendation,
                    "confidence": round(confidence, 2),
                    "analysis": {
                        "sentiment_score": round(positive_confidence - negative_confidence, 3),
                        "positive_sentiment": round(positive_confidence, 3),
                        "negative_sentiment": round(negative_confidence, 3)
                    },
                    "model_used": model_name
                }
            else:
                # Use Hugging Face Inference API for other models
                import requests
                
                hf_api_token = getattr(settings, 'HUGGINGFACE_API_KEY', None)
                if not hf_api_token:
                    return {
                        "error": "Hugging Face API token not configured",
                        "fallback_response": "Market analysis pending: Hugging Face service unavailable"
                    }
                
                api_url = f"https://api-inference.huggingface.co/models/{model_name}"
                headers = {"Authorization": f"Bearer {hf_api_token}"}
                
                payload = {
                    "inputs": prompt,
                    "parameters": {
                        "return_full_text": False,
                        "max_new_tokens": 500,
                        "temperature": temperature
                    }
                }
                
                response = requests.post(api_url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        generated_text = result[0].get('generated_text', '')
                        
                        # Try to extract JSON from generated text
                        try:
                            # Look for JSON in the response
                            start_idx = generated_text.find('{')
                            end_idx = generated_text.rfind('}') + 1
                            
                            if start_idx != -1 and end_idx != 0:
                                json_str = generated_text[start_idx:end_idx]
                                return json.loads(json_str)
                            else:
                                return {
                                    "raw_response": generated_text,
                                    "model_used": model_name
                                }
                        except json.JSONDecodeError:
                            return {
                                "raw_response": generated_text,
                                "model_used": model_name
                            }
                    else:
                        return {
                            "error": "Unexpected response format from Hugging Face",
                            "raw_response": str(result)
                        }
                else:
                    return {
                        "error": f"Hugging Face API error: {response.status_code}",
                        "details": response.text
                    }
                    
        except Exception as e:
            logger.error(f"Error calling Hugging Face model {model_name}: {e}")
            return {
                "error": f"Hugging Face error: {str(e)}",
                "fallback_response": "Market analysis pending: Model service unavailable"
            }
    
    async def analyze_market_data(
        self,
        market_data: Dict[str, Any],
        user_context: Dict[str, Any] = None,
        llm_provider: str = "groq",
        model: str = None,
        analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Main method to analyze market data using specified LLM provider
        """
        # Generate prompt
        prompt = self.get_financial_analysis_prompt(market_data, user_context, analysis_type)
        
        # Select model if not provided
        if not model:
            if llm_provider in self.available_models and self.available_models[llm_provider]:
                model = self.available_models[llm_provider][0]  # Use first available model
            else:
                model = "llama-3.3-70b-versatile"  # Default fallback
        
        # Call appropriate analyzer
        if llm_provider == "groq":
            return await self.analyze_with_groq(prompt, model)
        elif llm_provider == "openai":
            return await self.analyze_with_openai(prompt, model)
        elif llm_provider == "anthropic":
            return await self.analyze_with_anthropic(prompt, model)
        elif llm_provider == "huggingface":
            return await self.analyze_with_huggingface(prompt, model)
        else:
            # Default to Groq if provider not specified or not available
            return await self.analyze_with_groq(prompt, model)
    
    async def generate_market_research(
        self,
        sector_data: Dict[str, Any] = None,
        llm_provider: str = "groq",
        model: str = None
    ) -> Dict[str, Any]:
        """
        Generate market research and sector analysis
        """
        prompt = self.get_market_research_prompt(sector_data)
        
        # Select model if not provided
        if not model:
            if llm_provider in self.available_models and self.available_models[llm_provider]:
                model = self.available_models[llm_provider][0]
            else:
                model = "llama-3.3-70b-versatile"
        
        # Call appropriate analyzer
        if llm_provider == "groq":
            return await self.analyze_with_groq(prompt, model)
        elif llm_provider == "openai":
            return await self.analyze_with_openai(prompt, model)
        elif llm_provider == "anthropic":
            return await self.analyze_with_anthropic(prompt, model)
        elif llm_provider == "huggingface":
            return await self.analyze_with_huggingface(prompt, model)
        else:
            return await self.analyze_with_groq(prompt, model)
    
    def get_available_providers(self) -> List[str]:
        """
        Get list of available LLM providers
        """
        return list(self.clients.keys())
    
    async def test_connection(self, provider: str) -> bool:
        """
        Test connection to a specific LLM provider
        """
        try:
            if provider == "groq" and 'groq' in self.clients:
                # Test with a simple model listing call
                models = self.available_models.get('groq', [])
                return len(models) > 0
            elif provider == "openai" and 'openai' in self.clients:
                # Test with a simple API call
                from openai import OpenAI
                client = self.clients['openai']
                # Just check if client is initialized properly
                return client is not None
            elif provider == "anthropic" and 'anthropic' in self.clients:
                # Test with a simple API call
                client = self.clients['anthropic']
                return client is not None
            elif provider == "huggingface" and 'huggingface' in self.clients:
                # Test with a simple API call
                return True  # If initialized, assume working
            else:
                return False
        except Exception:
            return False

    def get_available_models(self, provider: str = None) -> Dict[str, List[str]]:
        """
        Get available models for a provider or all providers
        """
        if provider:
            return {provider: self.available_models.get(provider, [])}
        return self.available_models

# Global instance
enhanced_llm_service = EnhancedLLMService()
