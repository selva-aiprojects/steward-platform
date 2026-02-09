"""
AI Filter Engine for Futures, Options, and Currencies

This module implements the AI Filter Engine responsible for:
1. Market sentiment analysis using NLP
2. Technical indicator processing with ML models
3. Fundamental analysis using AI
4. Pattern recognition in market data
5. Risk assessment using AI models
6. Signal generation for trading decisions
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import asyncio

# Import database components
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.social_sentiment import SocialSentiment

logger = logging.getLogger(__name__)


class AIFilterEngineInterface(ABC):
    """Abstract interface for AI Filter Engine"""

    @abstractmethod
    async def analyze_market_sentiment(self, news_data: List[Dict[str, Any]], social_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze market sentiment from news and social media"""
        pass

    @abstractmethod
    async def process_technical_indicators(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process technical indicators using AI"""
        pass

    @abstractmethod
    async def perform_fundamental_analysis(self, fundamentals_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform fundamental analysis using AI"""
        pass

    @abstractmethod
    async def detect_patterns(self, price_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect patterns in price data using AI"""
        pass

    @abstractmethod
    async def assess_risk(self, market_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk using AI models"""
        pass

    @abstractmethod
    async def generate_signals(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trading signals based on AI analysis"""
        pass


class AIFilterEngine(AIFilterEngineInterface):
    """
    Main AI Filter Engine implementation for Futures, Options, and Currencies
    """

    def __init__(self):
        self.sentiment_models = {}
        self.pattern_detectors = {}
        self.anomaly_detectors = {}
        self.scalers = {}
        logger.info("AI Filter Engine initialized")

    async def analyze_market_sentiment(self, news_data: List[Dict[str, Any]], social_data: List[Dict[str, Any]] = None, symbols: List[str] = None) -> Dict[str, Any]:
        """Analyze market sentiment from news and social media"""
        try:
            # Process news sentiment
            news_sentiment_score = 0
            if news_data:
                news_scores = []
                for item in news_data:
                    # Simple sentiment scoring based on keywords
                    title = item.get("title", "").lower()
                    content = item.get("content", "").lower()

                    positive_keywords = ["positive", "bullish", "gain", "rise", "strong", "buy", "upgrade"]
                    negative_keywords = ["negative", "bearish", "loss", "fall", "weak", "sell", "downgrade", "crisis"]

                    pos_count = sum(1 for kw in positive_keywords if kw in title or kw in content)
                    neg_count = sum(1 for kw in negative_keywords if kw in title or kw in content)

                    score = (pos_count - neg_count) / (pos_count + neg_count + 1)  # +1 to avoid division by zero
                    news_scores.append(score)

                news_sentiment_score = sum(news_scores) / len(news_scores) if news_scores else 0

            # Process social media sentiment - prioritize database data if symbols provided
            social_sentiment_score = 0
            if symbols:
                # Fetch social media data from database for the specified symbols
                social_scores = await self._get_social_sentiment_from_db(symbols)
                if social_scores:
                    social_sentiment_score = sum(social_scores) / len(social_scores)
            elif social_data:
                # Use provided social data if no symbols specified
                social_scores = []
                for item in social_data:
                    text = item.get("text", "").lower()

                    positive_keywords = ["positive", "bullish", "buy", "strong", "great", "amazing", "profit"]
                    negative_keywords = ["negative", "bearish", "sell", "weak", "terrible", "loss", "crash"]

                    pos_count = sum(1 for kw in positive_keywords if kw in text)
                    neg_count = sum(1 for kw in negative_keywords if kw in text)

                    score = (pos_count - neg_count) / (pos_count + neg_count + 1)
                    social_scores.append(score)

                social_sentiment_score = sum(social_scores) / len(social_scores) if social_scores else 0

            # Combine sentiments with weights
            combined_sentiment = (news_sentiment_score * 0.6) + (social_sentiment_score * 0.4)

            # Normalize to -1 to 1 scale
            normalized_sentiment = max(-1, min(1, combined_sentiment))

            sentiment_analysis = {
                "overall_sentiment": normalized_sentiment,
                "news_sentiment": news_sentiment_score,
                "social_sentiment": social_sentiment_score,
                "confidence": 0.7,  # Would be calculated based on model confidence
                "timestamp": datetime.now().isoformat()
            }

            logger.info("Completed market sentiment analysis")

            return {
                "success": True,
                "sentiment_analysis": sentiment_analysis
            }
        except Exception as e:
            logger.error(f"Error in market sentiment analysis: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _get_social_sentiment_from_db(self, symbols: List[str]) -> List[float]:
        """Helper method to get social sentiment scores from database for given symbols"""
        try:
            db = SessionLocal()
            try:
                # Get social sentiment data for the specified symbols from the last 24 hours
                social_sentiments = db.query(SocialSentiment).filter(
                    SocialSentiment.symbol.in_(symbols),
                    SocialSentiment.timestamp >= datetime.utcnow() - timedelta(hours=24)
                ).all()

                # Extract sentiment scores
                scores = [float(sent.sentiment_score) for sent in social_sentiments if sent.sentiment_score is not None]

                logger.info(f"Fetched {len(scores)} social sentiment records for symbols: {symbols}")

                return scores
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error fetching social sentiment from database: {str(e)}")
            return []

    async def process_technical_indicators(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process technical indicators using AI"""
        try:
            # Extract price data
            prices = market_data.get("prices", [])
            volumes = market_data.get("volumes", [])
            
            if not prices:
                return {
                    "success": False,
                    "error": "No price data provided"
                }
            
            # Convert to pandas DataFrame for easier manipulation
            df = pd.DataFrame(prices)
            
            # Calculate technical indicators
            # Moving averages
            df['sma_20'] = df['close'].rolling(window=20).mean()
            df['sma_50'] = df['close'].rolling(window=50).mean()
            df['ema_12'] = df['close'].ewm(span=12).mean()
            df['ema_26'] = df['close'].ewm(span=26).mean()
            
            # MACD
            df['macd'] = df['ema_12'] - df['ema_26']
            df['macd_signal'] = df['macd'].ewm(span=9).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']
            
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # Bollinger Bands
            df['bb_middle'] = df['close'].rolling(window=20).mean()
            bb_std = df['close'].rolling(window=20).std()
            df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
            df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
            
            # Stochastic Oscillator
            low_14 = df['low'].rolling(window=14).min()
            high_14 = df['high'].rolling(window=14).max()
            df['stoch_k'] = 100 * ((df['close'] - low_14) / (high_14 - low_14))
            df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()
            
            # Volume indicators
            if volumes:
                vol_df = pd.DataFrame(volumes)
                df['volume_sma'] = vol_df['volume'].rolling(window=20).mean()
                df['volume_ratio'] = df['volume'] / df['volume_sma']
            
            # AI-based interpretation of indicators
            latest_data = df.iloc[-1]
            
            # Determine trend based on moving averages
            trend = "NEUTRAL"
            if latest_data['close'] > latest_data['sma_20'] > latest_data['sma_50']:
                trend = "BULLISH"
            elif latest_data['close'] < latest_data['sma_20'] < latest_data['sma_50']:
                trend = "BEARISH"
            
            # Determine momentum based on RSI and MACD
            momentum = "NEUTRAL"
            if latest_data['rsi'] > 70:
                momentum = "OVERBOUGHT"
            elif latest_data['rsi'] < 30:
                momentum = "OVERSOLD"
            
            # MACD crossover detection
            macd_signal = "HOLD"
            if latest_data['macd'] > latest_data['macd_signal']:
                macd_signal = "BUY"
            elif latest_data['macd'] < latest_data['macd_signal']:
                macd_signal = "SELL"
            
            # Bollinger Bands position
            bb_position = "NEUTRAL"
            if latest_data['close'] > latest_data['bb_upper']:
                bb_position = "OVERBOUGHT"
            elif latest_data['close'] < latest_data['bb_lower']:
                bb_position = "OVERSOLD"
            
            technical_analysis = {
                "trend": trend,
                "momentum": momentum,
                "macd_signal": macd_signal,
                "bollinger_position": bb_position,
                "indicators": {
                    "sma_20": latest_data['sma_20'],
                    "sma_50": latest_data['sma_50'],
                    "rsi": latest_data['rsi'],
                    "macd": latest_data['macd'],
                    "macd_signal": latest_data['macd_signal'],
                    "bb_upper": latest_data['bb_upper'],
                    "bb_middle": latest_data['bb_middle'],
                    "bb_lower": latest_data['bb_lower'],
                    "stoch_k": latest_data['stoch_k'],
                    "stoch_d": latest_data['stoch_d']
                },
                "confidence": 0.8,  # Would be calculated based on model confidence
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info("Processed technical indicators with AI analysis")
            
            return {
                "success": True,
                "technical_analysis": technical_analysis
            }
        except Exception as e:
            logger.error(f"Error processing technical indicators: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def perform_fundamental_analysis(self, fundamentals_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform fundamental analysis using AI"""
        try:
            # Extract fundamental metrics
            pe_ratio = fundamentals_data.get("pe_ratio", 0)
            pb_ratio = fundamentals_data.get("pb_ratio", 0)
            roe = fundamentals_data.get("roe", 0)
            debt_to_equity = fundamentals_data.get("debt_to_equity", 0)
            eps_growth = fundamentals_data.get("eps_growth", 0)
            revenue_growth = fundamentals_data.get("revenue_growth", 0)
            market_cap = fundamentals_data.get("market_cap", 0)
            dividend_yield = fundamentals_data.get("dividend_yield", 0)
            
            # AI-based fundamental scoring
            # These are simplified rules - in reality, this would use ML models
            
            # Valuation score (lower P/E and P/B are better)
            valuation_score = 0
            if pe_ratio > 0:
                if pe_ratio < 15:
                    valuation_score += 25
                elif pe_ratio < 20:
                    valuation_score += 15
                elif pe_ratio < 25:
                    valuation_score += 5
                else:
                    valuation_score -= 10
            
            if pb_ratio > 0:
                if pb_ratio < 1.5:
                    valuation_score += 20
                elif pb_ratio < 2.5:
                    valuation_score += 10
                elif pb_ratio < 3.5:
                    valuation_score += 5
                else:
                    valuation_score -= 15
            
            # Profitability score (higher ROE is better)
            profitability_score = 0
            if roe > 0:
                if roe > 0.20:
                    profitability_score += 25
                elif roe > 0.15:
                    profitability_score += 20
                elif roe > 0.10:
                    profitability_score += 15
                elif roe > 0.05:
                    profitability_score += 10
                else:
                    profitability_score -= 10
            
            # Financial health score (lower debt-to-equity is better)
            health_score = 0
            if debt_to_equity >= 0:
                if debt_to_equity < 0.3:
                    health_score += 20
                elif debt_to_equity < 0.5:
                    health_score += 15
                elif debt_to_equity < 0.7:
                    health_score += 10
                else:
                    health_score -= 15
            
            # Growth score (higher growth rates are better)
            growth_score = 0
            if eps_growth > 0:
                if eps_growth > 0.20:
                    growth_score += 20
                elif eps_growth > 0.15:
                    growth_score += 15
                elif eps_growth > 0.10:
                    growth_score += 10
                elif eps_growth > 0.05:
                    growth_score += 5
            
            if revenue_growth > 0:
                if revenue_growth > 0.20:
                    growth_score += 15
                elif revenue_growth > 0.15:
                    growth_score += 10
                elif revenue_growth > 0.10:
                    growth_score += 5
            
            # Size and stability factor
            size_score = 0
            if market_cap > 50000000000:  # > 50B
                size_score += 10
            elif market_cap > 10000000000:  # > 10B
                size_score += 5
            elif market_cap < 1000000000:  # < 1B
                size_score -= 10
            
            # Dividend factor
            dividend_score = 0
            if dividend_yield > 0.04:  # > 4%
                dividend_score += 10
            elif dividend_yield > 0.02:  # > 2%
                dividend_score += 5
            elif dividend_yield == 0:
                dividend_score -= 5
            
            # Calculate overall fundamental score
            total_score = valuation_score + profitability_score + health_score + growth_score + size_score + dividend_score
            # Normalize to -100 to 100 scale
            normalized_score = max(-100, min(100, total_score))
            
            # Determine recommendation based on score
            recommendation = "HOLD"
            if normalized_score > 50:
                recommendation = "STRONG_BUY"
            elif normalized_score > 20:
                recommendation = "BUY"
            elif normalized_score < -20:
                recommendation = "SELL"
            elif normalized_score < -50:
                recommendation = "STRONG_SELL"
            
            fundamental_analysis = {
                "recommendation": recommendation,
                "overall_score": normalized_score,
                "valuation_score": valuation_score,
                "profitability_score": profitability_score,
                "health_score": health_score,
                "growth_score": growth_score,
                "size_score": size_score,
                "dividend_score": dividend_score,
                "metrics": {
                    "pe_ratio": pe_ratio,
                    "pb_ratio": pb_ratio,
                    "roe": roe,
                    "debt_to_equity": debt_to_equity,
                    "eps_growth": eps_growth,
                    "revenue_growth": revenue_growth,
                    "market_cap": market_cap,
                    "dividend_yield": dividend_yield
                },
                "confidence": 0.75,  # Would be calculated based on model confidence
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info("Performed fundamental analysis with AI evaluation")
            
            return {
                "success": True,
                "fundamental_analysis": fundamental_analysis
            }
        except Exception as e:
            logger.error(f"Error in fundamental analysis: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def detect_patterns(self, price_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect patterns in price data using AI"""
        try:
            if not price_data:
                return {
                    "success": False,
                    "error": "No price data provided"
                }
            
            # Convert to DataFrame
            df = pd.DataFrame(price_data)
            
            # Calculate additional features for pattern detection
            df['high_low_pct'] = (df['high'] - df['low']) / df['close']
            df['body_pct'] = abs(df['open'] - df['close']) / df['close']
            df['upper_shadow'] = (df['high'] - df[['open', 'close']].max(axis=1)) / df['close']
            df['lower_shadow'] = (df[['open', 'close']].min(axis=1) - df['low']) / df['close']
            
            # Detect common candlestick patterns
            patterns = []
            
            # Hammer pattern
            for i in range(len(df)):
                if i >= 2:  # Need at least 2 previous candles
                    # Hammer: long lower shadow, small body, little or no upper shadow
                    if (df.iloc[i]['lower_shadow'] > 2 * df.iloc[i]['body_pct'] and 
                        df.iloc[i]['upper_shadow'] < df.iloc[i]['body_pct'] and
                        df.iloc[i]['body_pct'] > 0.01):  # At least 1% body
                        patterns.append({
                            "type": "hammer",
                            "confidence": 0.7,
                            "timestamp": df.iloc[i]['timestamp'],
                            "direction": "bullish"
                        })
                    
                    # Shooting star pattern
                    if (df.iloc[i]['upper_shadow'] > 2 * df.iloc[i]['body_pct'] and 
                        df.iloc[i]['lower_shadow'] < df.iloc[i]['body_pct'] and
                        df.iloc[i]['body_pct'] > 0.01):
                        patterns.append({
                            "type": "shooting_star",
                            "confidence": 0.7,
                            "timestamp": df.iloc[i]['timestamp'],
                            "direction": "bearish"
                        })
            
            # Detect trend patterns using moving averages
            df['sma_20'] = df['close'].rolling(window=20).mean()
            df['sma_50'] = df['close'].rolling(window=50).mean()
            
            # Golden cross / Death cross detection
            for i in range(1, len(df)):
                prev_sma_20 = df.iloc[i-1]['sma_20']
                curr_sma_20 = df.iloc[i]['sma_20']
                prev_sma_50 = df.iloc[i-1]['sma_50']
                curr_sma_50 = df.iloc[i]['sma_50']
                
                if pd.notna(prev_sma_20) and pd.notna(curr_sma_20) and pd.notna(prev_sma_50) and pd.notna(curr_sma_50):
                    # Golden cross (bullish)
                    if prev_sma_20 <= prev_sma_50 and curr_sma_20 > curr_sma_50:
                        patterns.append({
                            "type": "golden_cross",
                            "confidence": 0.8,
                            "timestamp": df.iloc[i]['timestamp'],
                            "direction": "bullish"
                        })
                    
                    # Death cross (bearish)
                    elif prev_sma_20 >= prev_sma_50 and curr_sma_20 < curr_sma_50:
                        patterns.append({
                            "type": "death_cross",
                            "confidence": 0.8,
                            "timestamp": df.iloc[i]['timestamp'],
                            "direction": "bearish"
                        })
            
            # Use Isolation Forest for anomaly detection (potential pattern breaks)
            scaler = StandardScaler()
            features = df[['open', 'high', 'low', 'close', 'volume']].fillna(0)
            scaled_features = scaler.fit_transform(features)
            
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            anomalies = iso_forest.fit_predict(scaled_features)
            
            for i, anomaly in enumerate(anomalies):
                if anomaly == -1:  # Anomaly detected
                    patterns.append({
                        "type": "anomaly",
                        "confidence": 0.6,
                        "timestamp": df.iloc[i]['timestamp'],
                        "direction": "neutral"
                    })
            
            pattern_analysis = {
                "detected_patterns": patterns,
                "pattern_count": len(patterns),
                "confidence": 0.7,  # Average confidence
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Detected {len(patterns)} patterns in price data")
            
            return {
                "success": True,
                "pattern_analysis": pattern_analysis
            }
        except Exception as e:
            logger.error(f"Error detecting patterns: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def assess_risk(self, market_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk using AI models"""
        try:
            # Extract market conditions
            volatility = market_conditions.get("volatility", 0.2)  # 20% default
            correlation = market_conditions.get("correlation", 0.5)  # 50% default
            volume = market_conditions.get("volume", 0)
            price_level = market_conditions.get("price_level", 0)
            trend_strength = market_conditions.get("trend_strength", 0.5)
            market_regime = market_conditions.get("market_regime", "normal")
            
            # Calculate various risk metrics
            
            # Volatility-based risk
            volatility_risk = volatility * 100  # Scale to percentage
            
            # Correlation risk (higher correlation means higher systemic risk)
            correlation_risk = correlation * 50  # Scale appropriately
            
            # Liquidity risk based on volume
            liquidity_risk = 0
            if volume > 0:
                # Lower volume indicates higher liquidity risk
                # This is a simplified calculation
                avg_volume = market_conditions.get("average_volume", volume)
                if avg_volume > 0:
                    volume_ratio = volume / avg_volume
                    if volume_ratio < 0.5:  # Much below average
                        liquidity_risk = 30
                    elif volume_ratio < 0.8:  # Below average
                        liquidity_risk = 15
            
            # Trend risk (strong trends can reverse suddenly)
            trend_risk = abs(trend_strength) * 25
            
            # Regime-specific risk adjustments
            regime_risk = 0
            if market_regime == "high_volatility":
                regime_risk = 40
            elif market_regime == "crisis":
                regime_risk = 60
            elif market_regime == "bubble":
                regime_risk = 50
            elif market_regime == "distressed":
                regime_risk = 35
            
            # Calculate composite risk score
            composite_risk = (
                volatility_risk * 0.3 +
                correlation_risk * 0.2 +
                liquidity_risk * 0.2 +
                trend_risk * 0.15 +
                regime_risk * 0.15
            )
            
            # Normalize to 0-100 scale
            risk_level = min(100, max(0, composite_risk))
            
            # Determine risk category
            risk_category = "LOW"
            if risk_level > 70:
                risk_category = "HIGH"
            elif risk_level > 40:
                risk_category = "MEDIUM"
            
            # Calculate Value at Risk (VaR) approximation
            var_95 = price_level * volatility * 1.645  # 95% confidence
            var_99 = price_level * volatility * 2.33   # 99% confidence
            
            risk_assessment = {
                "risk_level": risk_level,
                "risk_category": risk_category,
                "volatility_risk": volatility_risk,
                "correlation_risk": correlation_risk,
                "liquidity_risk": liquidity_risk,
                "trend_risk": trend_risk,
                "regime_risk": regime_risk,
                "var_95": var_95,
                "var_99": var_99,
                "confidence": 0.8,  # Model confidence
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Assessed market risk: {risk_level} ({risk_category})")
            
            return {
                "success": True,
                "risk_assessment": risk_assessment
            }
        except Exception as e:
            logger.error(f"Error assessing risk: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def generate_signals(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trading signals based on AI analysis"""
        try:
            # Extract analysis results
            sentiment = analysis_data.get("sentiment_analysis", {}).get("overall_sentiment", 0)
            technical = analysis_data.get("technical_analysis", {})
            fundamental = analysis_data.get("fundamental_analysis", {})
            patterns = analysis_data.get("pattern_analysis", {}).get("detected_patterns", [])
            risk = analysis_data.get("risk_assessment", {}).get("risk_level", 50)
            
            # Calculate composite signal
            # Weight different factors
            sentiment_weight = 0.2
            technical_weight = 0.3
            fundamental_weight = 0.2
            pattern_weight = 0.15
            risk_weight = 0.15
            
            # Sentiment signal (convert to -1 to 1 scale)
            sentiment_signal = sentiment  # Already in -1 to 1 scale
            
            # Technical signal based on trend and momentum
            tech_signal = 0
            if technical:
                trend = technical.get("trend", "NEUTRAL")
                momentum = technical.get("momentum", "NEUTRAL")
                
                if trend == "BULLISH":
                    tech_signal += 0.5
                elif trend == "BEARISH":
                    tech_signal -= 0.5
                
                if momentum == "OVERBOUGHT":
                    tech_signal -= 0.3
                elif momentum == "OVERSOLD":
                    tech_signal += 0.3
            
            # Fundamental signal based on recommendation
            fund_signal = 0
            if fundamental:
                rec = fundamental.get("recommendation", "HOLD")
                score = fundamental.get("overall_score", 0) / 100  # Normalize to -1 to 1
                
                if rec == "STRONG_BUY":
                    fund_signal = min(1.0, score + 0.2)
                elif rec == "BUY":
                    fund_signal = min(0.7, score + 0.1)
                elif rec == "STRONG_SELL":
                    fund_signal = max(-1.0, score - 0.2)
                elif rec == "SELL":
                    fund_signal = max(-0.7, score - 0.1)
            
            # Pattern signal (count bullish vs bearish patterns)
            pattern_signal = 0
            if patterns:
                bullish_count = sum(1 for p in patterns if p.get("direction") == "bullish")
                bearish_count = sum(1 for p in patterns if p.get("direction") == "bearish")
                
                if len(patterns) > 0:
                    pattern_signal = (bullish_count - bearish_count) / len(patterns)
            
            # Risk adjustment (reduce signal strength if risk is high)
            risk_adjustment = 1 - (risk / 100) * 0.5  # Reduce signal by up to 50% if risk is very high
            
            # Calculate composite signal
            composite_signal = (
                sentiment_signal * sentiment_weight +
                tech_signal * technical_weight +
                fund_signal * fundamental_weight +
                pattern_signal * pattern_weight
            ) * risk_adjustment
            
            # Determine signal type and strength
            signal_type = "NEUTRAL"
            signal_strength = abs(composite_signal)
            
            if composite_signal > 0.3:
                signal_type = "BUY"
            elif composite_signal > 0.1:
                signal_type = "BUY_WEAK"
            elif composite_signal < -0.3:
                signal_type = "SELL"
            elif composite_signal < -0.1:
                signal_type = "SELL_WEAK"
            
            # Calculate confidence based on agreement among different analysis types
            confidence = 0.5  # Base confidence
            
            # Increase confidence if different analyses agree
            if (sentiment > 0.5 and tech_signal > 0.3) or (sentiment < -0.5 and tech_signal < -0.3):
                confidence += 0.2
            if (sentiment > 0.5 and fund_signal > 0.3) or (sentiment < -0.5 and fund_signal < -0.3):
                confidence += 0.15
            if (tech_signal > 0.3 and fund_signal > 0.3) or (tech_signal < -0.3 and fund_signal < -0.3):
                confidence += 0.15
            
            confidence = min(0.95, confidence)  # Cap at 95%
            
            trading_signal = {
                "signal_type": signal_type,
                "signal_strength": signal_strength,
                "composite_score": composite_signal,
                "confidence": confidence,
                "components": {
                    "sentiment_contribution": sentiment_signal * sentiment_weight,
                    "technical_contribution": tech_signal * technical_weight,
                    "fundamental_contribution": fund_signal * fundamental_weight,
                    "pattern_contribution": pattern_signal * pattern_weight,
                    "risk_adjustment": risk_adjustment
                },
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Generated trading signal: {signal_type} with strength {signal_strength:.2f}")
            
            return {
                "success": True,
                "trading_signal": trading_signal
            }
        except Exception as e:
            logger.error(f"Error generating trading signals: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


# Singleton instance
ai_filter_engine = AIFilterEngine()