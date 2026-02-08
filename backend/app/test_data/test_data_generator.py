"""
Test Data Generator for Futures, Options, and Currencies

This module generates comprehensive test data for:
1. Futures contracts (Nifty, Bank Nifty, Stock futures)
2. Options contracts (calls, puts, different strikes/expiries)
3. Currency pairs (USDINR, EURINR, GBPINR, JPYINR)
4. Market conditions (bull, bear, sideways, volatile)
5. Trading scenarios (entry, exit, risk events)
"""

import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import uuid
from typing import Dict, List, Any

class TestDataGenerator:
    """Generates test data for Futures, Options, and Currencies"""

    def __init__(self):
        self.futures_symbols = [
            "NIFTY24FEB24F", "BANKNIFTY24FEB24F", "RELIANCE24FEB24F", 
            "TCS24FEB24F", "INFY24FEB24F", "HDFCBANK24FEB24F"
        ]
        
        self.options_underlyings = ["NIFTY", "BANKNIFTY", "RELIANCE", "TCS", "INFY", "HDFCBANK"]
        self.currency_pairs = ["USDINR", "EURINR", "GBPINR", "JPYINR"]
        
        self.current_date = datetime.now()
        self.test_scenarios = [
            "normal_market", "high_volatility", "trending_up", 
            "trending_down", "range_bound", "gap_opening"
        ]

    def generate_futures_data(self, num_records: int = 1000) -> List[Dict[str, Any]]:
        """Generate test data for futures contracts"""
        futures_data = []
        
        for i in range(num_records):
            symbol = random.choice(self.futures_symbols)
            base_price = self._get_base_price(symbol)
            
            # Generate realistic price movements
            open_price = base_price * (1 + random.uniform(-0.02, 0.02))
            high_price = open_price * (1 + random.uniform(0, 0.03))
            low_price = open_price * (1 - random.uniform(0, 0.03))
            close_price = low_price + random.random() * (high_price - low_price)
            
            # Add some market scenarios
            scenario = random.choice(self.test_scenarios)
            if scenario == "high_volatility":
                multiplier = 1.5
                open_price = base_price * (1 + random.uniform(-0.04, 0.04) * multiplier)
                high_price = open_price * (1 + random.uniform(0, 0.06) * multiplier)
                low_price = open_price * (1 - random.uniform(0, 0.06) * multiplier)
            elif scenario == "trending_up":
                trend_factor = random.uniform(0.01, 0.03)
                open_price = base_price * (1 + random.uniform(-0.01, 0.01))
                close_price = open_price * (1 + trend_factor)
                high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.02))
                low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.01))
            elif scenario == "trending_down":
                trend_factor = random.uniform(-0.03, -0.01)
                open_price = base_price * (1 + random.uniform(-0.01, 0.01))
                close_price = open_price * (1 + trend_factor)
                high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.01))
                low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.02))
            
            futures_record = {
                "id": str(uuid.uuid4()),
                "symbol": symbol,
                "timestamp": (self.current_date - timedelta(minutes=i)).isoformat(),
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "volume": random.randint(10000, 1000000),
                "oi": random.randint(50000, 5000000),  # Open interest
                "expiry_date": (self.current_date + timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
                "underlying_price": base_price,
                "scenario": scenario
            }
            
            futures_data.append(futures_record)
        
        return futures_data

    def generate_options_data(self, num_records: int = 1000) -> List[Dict[str, Any]]:
        """Generate test data for options contracts"""
        options_data = []
        
        for i in range(num_records):
            underlying = random.choice(self.options_underlyings)
            base_price = self._get_base_price(underlying)
            
            # Generate option-specific attributes
            expiry_date = self.current_date + timedelta(days=random.randint(7, 45))
            strike_price = round(base_price + random.uniform(-100, 100), -1)  # Round to nearest 10
            option_type = random.choice(["CE", "PE"])  # Call, Put
            
            # Create option symbol
            if underlying in ["NIFTY", "BANKNIFTY"]:
                symbol = f"{underlying}{expiry_date.strftime('%y%b%d').upper()}{int(strike_price)}{option_type}"
            else:
                symbol = f"{underlying}{expiry_date.strftime('%y%b%d').upper()}{int(strike_price)}{option_type}"
            
            # Calculate theoretical option price using simplified model
            time_to_expiry = (expiry_date - self.current_date).days / 365.0
            volatility = random.uniform(0.15, 0.45)  # 15-45% volatility
            
            # Simplified Black-Scholes approximation
            intrinsic_value = max(0, base_price - strike_price) if option_type == "CE" else max(0, strike_price - base_price)
            time_value = volatility * base_price * time_to_expiry ** 0.5
            theoretical_price = intrinsic_value + time_value
            
            # Add market noise
            open_price = theoretical_price * (1 + random.uniform(-0.05, 0.05))
            high_price = open_price * (1 + random.uniform(0, 0.10))
            low_price = open_price * (1 - random.uniform(0, 0.10))
            close_price = low_price + random.random() * (high_price - low_price)
            
            # Adjust for scenario
            scenario = random.choice(self.test_scenarios)
            if scenario == "high_volatility":
                volatility_multiplier = 2.0
                open_price = theoretical_price * (1 + random.uniform(-0.10, 0.10) * volatility_multiplier)
                high_price = open_price * (1 + random.uniform(0, 0.15) * volatility_multiplier)
                low_price = open_price * (1 - random.uniform(0, 0.15) * volatility_multiplier)
            elif scenario == "trending_up" and option_type == "CE":
                # Calls perform better in up trends
                trend_boost = 1.3
                close_price = open_price * trend_boost
            elif scenario == "trending_down" and option_type == "PE":
                # Puts perform better in down trends
                trend_boost = 1.3
                close_price = open_price * trend_boost
            
            options_record = {
                "id": str(uuid.uuid4()),
                "symbol": symbol,
                "underlying": underlying,
                "timestamp": (self.current_date - timedelta(minutes=i)).isoformat(),
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "volume": random.randint(100, 10000),
                "oi": random.randint(1000, 100000),
                "strike_price": strike_price,
                "option_type": option_type,
                "expiry_date": expiry_date.strftime("%Y-%m-%d"),
                "underlying_price": base_price,
                "implied_volatility": round(volatility, 4),
                "delta": round(self._calculate_delta(base_price, strike_price, time_to_expiry, volatility, option_type), 4),
                "gamma": round(self._calculate_gamma(base_price, strike_price, time_to_expiry, volatility), 4),
                "theta": round(self._calculate_theta(base_price, strike_price, time_to_expiry, volatility, option_type), 4),
                "vega": round(self._calculate_vega(base_price, strike_price, time_to_expiry, volatility), 4),
                "rho": round(self._calculate_rho(base_price, strike_price, time_to_expiry, volatility, option_type), 4),
                "scenario": scenario
            }
            
            options_data.append(options_record)
        
        return options_data

    def generate_currency_data(self, num_records: int = 1000) -> List[Dict[str, Any]]:
        """Generate test data for currency pairs"""
        currency_data = []
        
        for i in range(num_records):
            pair = random.choice(self.currency_pairs)
            
            # Base exchange rates
            base_rates = {
                "USDINR": 83.00,
                "EURINR": 90.00,
                "GBPINR": 105.00,
                "JPYINR": 0.55
            }
            
            base_rate = base_rates[pair]
            
            # Generate realistic FX movements (smaller than equity movements)
            open_rate = base_rate * (1 + random.uniform(-0.005, 0.005))
            high_rate = open_rate * (1 + random.uniform(0, 0.008))
            low_rate = open_rate * (1 - random.uniform(0, 0.008))
            close_rate = low_rate + random.random() * (high_rate - low_rate)
            
            # Adjust for scenario
            scenario = random.choice(self.test_scenarios)
            if scenario == "high_volatility":
                fx_multiplier = 2.0
                open_rate = base_rate * (1 + random.uniform(-0.01, 0.01) * fx_multiplier)
                high_rate = open_rate * (1 + random.uniform(0, 0.015) * fx_multiplier)
                low_rate = open_rate * (1 - random.uniform(0, 0.015) * fx_multiplier)
            elif scenario == "trending_up":
                trend_factor = random.uniform(0.001, 0.003)
                open_rate = base_rate * (1 + random.uniform(-0.001, 0.001))
                close_rate = open_rate * (1 + trend_factor)
                high_rate = max(open_rate, close_rate) * (1 + random.uniform(0, 0.002))
                low_rate = min(open_rate, close_rate) * (1 - random.uniform(0, 0.001))
            elif scenario == "trending_down":
                trend_factor = random.uniform(-0.003, -0.001)
                open_rate = base_rate * (1 + random.uniform(-0.001, 0.001))
                close_rate = open_rate * (1 + trend_factor)
                high_rate = max(open_rate, close_rate) * (1 + random.uniform(0, 0.001))
                low_rate = min(open_rate, close_rate) * (1 - random.uniform(0, 0.002))
            
            currency_record = {
                "id": str(uuid.uuid4()),
                "symbol": pair,
                "timestamp": (self.current_date - timedelta(minutes=i)).isoformat(),
                "open": round(open_rate, 4),
                "high": round(high_rate, 4),
                "low": round(low_rate, 4),
                "close": round(close_rate, 4),
                "volume": random.randint(100000, 10000000),  # Higher volumes for FX
                "bid": round(close_rate - random.uniform(0.0001, 0.0005), 4),
                "ask": round(close_rate + random.uniform(0.0001, 0.0005), 4),
                "spread": round((close_rate + random.uniform(0.0001, 0.0005)) - (close_rate - random.uniform(0.0001, 0.0005)), 4),
                "base_currency": pair[:3],
                "quote_currency": pair[3:],
                "scenario": scenario
            }
            
            currency_data.append(currency_record)
        
        return currency_data

    def generate_strategy_configurations(self) -> List[Dict[str, Any]]:
        """Generate test strategy configurations for different asset classes"""
        strategy_configs = []
        
        # Futures strategies
        futures_strategies = [
            {
                "strategy_id": str(uuid.uuid4()),
                "name": "Futures Momentum Strategy",
                "asset_class": "futures",
                "strategy_type": "momentum",
                "parameters": {
                    "entry_threshold": 0.02,
                    "exit_threshold": 0.01,
                    "stop_loss": 0.03,
                    "take_profit": 0.06,
                    "position_size": 0.1,  # 10% of capital
                    "leverage": 2,
                    "lookback_period": 20,
                    "volatility_target": 0.25
                },
                "symbols": ["NIFTY", "BANKNIFTY", "RELIANCE"],
                "risk_limits": {
                    "max_position_size": 500000,
                    "max_daily_loss": 100000,
                    "max_drawdown": 0.15
                }
            },
            {
                "strategy_id": str(uuid.uuid4()),
                "name": "Futures Mean Reversion",
                "asset_class": "futures",
                "strategy_type": "mean_reversion",
                "parameters": {
                    "entry_threshold": -2.0,  # Deviation in standard deviations
                    "exit_threshold": -0.5,
                    "stop_loss": 2.5,
                    "take_profit": 4.0,
                    "position_size": 0.05,
                    "leverage": 1,
                    "lookback_period": 30,
                    "z_score_threshold": 2.0
                },
                "symbols": ["NIFTY", "INFY", "HDFCBANK"],
                "risk_limits": {
                    "max_position_size": 300000,
                    "max_daily_loss": 75000,
                    "max_drawdown": 0.10
                }
            }
        ]
        
        # Options strategies
        options_strategies = [
            {
                "strategy_id": str(uuid.uuid4()),
                "name": "Options Covered Call",
                "asset_class": "options",
                "strategy_type": "covered_call",
                "parameters": {
                    "entry_threshold": 0.01,
                    "exit_threshold": 0.005,
                    "stop_loss": 0.05,
                    "take_profit": 0.15,
                    "position_size": 0.2,
                    "leverage": 1,
                    "strike_selection": "atm",
                    "expiry_days": 30,
                    "premium_capture_ratio": 0.7
                },
                "symbols": ["RELIANCE", "TCS"],
                "risk_limits": {
                    "max_position_size": 1000000,
                    "max_daily_loss": 200000,
                    "max_vega_exposure": 0.5,
                    "max_theta_positive": 1000
                }
            },
            {
                "strategy_id": str(uuid.uuid4()),
                "name": "Options Straddle",
                "asset_class": "options",
                "strategy_type": "straddle",
                "parameters": {
                    "entry_threshold": 0.02,
                    "exit_threshold": 0.01,
                    "stop_loss": 0.30,
                    "take_profit": 0.50,
                    "position_size": 0.08,
                    "leverage": 3,
                    "atm_tolerance": 0.05,
                    "volatility_threshold": 0.25,
                    "time_decay_factor": 0.7
                },
                "symbols": ["NIFTY", "BANKNIFTY"],
                "risk_limits": {
                    "max_position_size": 800000,
                    "max_daily_loss": 150000,
                    "max_vega_exposure": 1.0,
                    "max_gamma_exposure": 0.8
                }
            }
        ]
        
        # Currency strategies
        currency_strategies = [
            {
                "strategy_id": str(uuid.uuid4()),
                "name": "Forex Carry Trade",
                "asset_class": "currencies",
                "strategy_type": "carry",
                "parameters": {
                    "entry_threshold": 0.001,  # Small threshold for FX
                    "exit_threshold": 0.0005,
                    "stop_loss": 0.005,
                    "take_profit": 0.015,
                    "position_size": 0.15,
                    "leverage": 10,
                    "interest_rate_diff_threshold": 0.02,
                    "volatility_filter": 0.15,
                    "correlation_threshold": 0.7
                },
                "symbols": ["USDINR", "EURINR"],
                "risk_limits": {
                    "max_position_size": 5000000,  # Larger for FX
                    "max_daily_loss": 500000,
                    "max_correlation_risk": 0.6,
                    "max_leverage": 20
                }
            },
            {
                "strategy_id": str(uuid.uuid4()),
                "name": "FX Momentum Strategy",
                "asset_class": "currencies",
                "strategy_type": "momentum",
                "parameters": {
                    "entry_threshold": 0.002,
                    "exit_threshold": 0.001,
                    "stop_loss": 0.008,
                    "take_profit": 0.025,
                    "position_size": 0.12,
                    "leverage": 8,
                    "lookback_period": 14,
                    "rsi_threshold": 70
                },
                "symbols": ["USDINR", "GBPINR", "JPYINR"],
                "risk_limits": {
                    "max_position_size": 3000000,
                    "max_daily_loss": 300000,
                    "max_correlation_risk": 0.5,
                    "max_leverage": 15
                }
            }
        ]
        
        strategy_configs.extend(futures_strategies)
        strategy_configs.extend(options_strategies)
        strategy_configs.extend(currency_strategies)
        
        return strategy_configs

    def generate_risk_scenarios(self) -> List[Dict[str, Any]]:
        """Generate risk scenarios for testing"""
        risk_scenarios = [
            {
                "scenario_id": str(uuid.uuid4()),
                "name": "High Volatility Event",
                "type": "volatility_spike",
                "description": "Sudden increase in market volatility",
                "impact": "high",
                "affected_assets": ["futures", "options"],
                "parameters": {
                    "volatility_multiplier": 3.0,
                    "duration_minutes": 60,
                    "probability": 0.1
                }
            },
            {
                "scenario_id": str(uuid.uuid4()),
                "name": "Liquidity Crisis",
                "type": "liquidity_shock",
                "description": "Sharp decrease in market liquidity",
                "impact": "high",
                "affected_assets": ["all"],
                "parameters": {
                    "volume_reduction": 0.7,
                    "spread_widening": 2.0,
                    "duration_minutes": 120,
                    "probability": 0.05
                }
            },
            {
                "scenario_id": str(uuid.uuid4()),
                "name": "Interest Rate Shock",
                "type": "rate_change",
                "description": "Unexpected interest rate change affecting currencies",
                "impact": "medium",
                "affected_assets": ["currencies"],
                "parameters": {
                    "rate_change_bp": 25,
                    "direction": "positive",
                    "duration_hours": 24,
                    "probability": 0.15
                }
            },
            {
                "scenario_id": str(uuid.uuid4()),
                "name": "Correlation Breakdown",
                "type": "correlation_shift",
                "description": "Unexpected change in asset correlations",
                "impact": "medium",
                "affected_assets": ["futures", "equities"],
                "parameters": {
                    "correlation_change": 0.5,
                    "affected_pairs": ["NIFTY-BANKNIFTY", "RELIANCE-INFY"],
                    "duration_days": 5,
                    "probability": 0.2
                }
            }
        ]
        
        return risk_scenarios

    def generate_market_news(self) -> List[Dict[str, Any]]:
        """Generate market news for sentiment analysis"""
        news_categories = [
            "earnings", "policy", "global", "sector", "commodity", 
            "currency", "derivatives", "macro"
        ]
        
        news_items = []
        
        for i in range(50):
            category = random.choice(news_categories)
            sentiment = random.choice(["positive", "negative", "neutral"])
            
            news_item = {
                "id": str(uuid.uuid4()),
                "timestamp": (self.current_date - timedelta(hours=i)).isoformat(),
                "category": category,
                "headline": self._generate_headline(category, sentiment),
                "content": self._generate_content(category, sentiment),
                "sentiment_score": self._get_sentiment_score(sentiment),
                "relevance_score": random.uniform(0.3, 1.0),
                "tickers_affected": self._get_affected_tickers(category),
                "source": random.choice(["economic_times", "business_standard", "reuters", "bloomberg"])
            }
            
            news_items.append(news_item)
        
        return news_items

    def _get_base_price(self, symbol: str) -> float:
        """Get base price for a symbol"""
        base_prices = {
            "NIFTY": 22000,
            "BANKNIFTY": 52000,
            "RELIANCE": 2500,
            "TCS": 3800,
            "INFY": 1500,
            "HDFCBANK": 1700,
            "USDINR": 83.00,
            "EURINR": 90.00,
            "GBPINR": 105.00,
            "JPYINR": 0.55
        }
        
        # Extract base symbol if it's a futures/option symbol
        if symbol.endswith(('F', 'CE', 'PE')):
            for base_sym in base_prices:
                if base_sym in symbol:
                    return base_prices[base_sym]
        
        return base_prices.get(symbol, 1000)

    def _calculate_delta(self, spot: float, strike: float, time: float, vol: float, opt_type: str) -> float:
        """Calculate option delta (simplified)"""
        import math
        
        if opt_type == "CE":
            # Call delta approximation
            d1 = (math.log(spot/strike) + (0.21/2) * time) / (vol * math.sqrt(time))
            return 0.5 + 0.5 * math.erf(d1 / math.sqrt(2))
        else:
            # Put delta approximation
            d1 = (math.log(spot/strike) + (0.21/2) * time) / (vol * math.sqrt(time))
            return -0.5 + 0.5 * math.erf(-d1 / math.sqrt(2))

    def _calculate_gamma(self, spot: float, strike: float, time: float, vol: float) -> float:
        """Calculate option gamma (simplified)"""
        import math
        
        d1 = (math.log(spot/strike) + (0.21/2) * time) / (vol * math.sqrt(time))
        gamma = (math.exp(-d1**2/2)) / (spot * vol * math.sqrt(2 * math.pi * time))
        return gamma

    def _calculate_theta(self, spot: float, strike: float, time: float, vol: float, opt_type: str) -> float:
        """Calculate option theta (simplified)"""
        import math
        
        d1 = (math.log(spot/strike) + (0.21/2) * time) / (vol * math.sqrt(time))
        d2 = d1 - vol * math.sqrt(time)
        
        if opt_type == "CE":
            theta = -(spot * vol * math.exp(-d1**2/2)) / (2 * math.sqrt(2 * math.pi * time))
        else:
            theta = -(spot * vol * math.exp(-d1**2/2)) / (2 * math.sqrt(2 * math.pi * time))
        
        return theta

    def _calculate_vega(self, spot: float, strike: float, time: float, vol: float) -> float:
        """Calculate option vega (simplified)"""
        import math
        
        d1 = (math.log(spot/strike) + (0.21/2) * time) / (vol * math.sqrt(time))
        vega = spot * math.sqrt(time) * math.exp(-d1**2/2) / math.sqrt(2 * math.pi)
        return vega

    def _calculate_rho(self, spot: float, strike: float, time: float, vol: float, opt_type: str) -> float:
        """Calculate option rho (simplified)"""
        import math
        
        d2 = (math.log(spot/strike) - (0.21/2) * time) / (vol * math.sqrt(time))
        
        if opt_type == "CE":
            rho = strike * time * math.exp(-0.1 * time) * (0.5 + 0.5 * math.erf(d2 / math.sqrt(2)))
        else:
            rho = -strike * time * math.exp(-0.1 * time) * (0.5 + 0.5 * math.erf(-d2 / math.sqrt(2)))
        
        return rho

    def _generate_headline(self, category: str, sentiment: str) -> str:
        """Generate news headline"""
        headlines = {
            "earnings": {
                "positive": [
                    "TCS Q4 Results Beat Expectations, Revenue Up 15%",
                    "HDFC Bank Reports Strong Growth, Net Interest Income Rises",
                    "Infosys Delivers Robust Performance, Digital Revenue Soars"
                ],
                "negative": [
                    "Reliance Q4 Profits Fall 12% Amid Rising Costs",
                    "ICICI Bank Misses Estimates, Bad Loan Concerns Rise",
                    "Wipro Reports Disappointing Q4 Results, Guidance Cut"
                ],
                "neutral": [
                    "IT Major Reports Mixed Q4 Results, Guidance Unchanged",
                    "Banking Sector Shows Moderate Growth in Q4",
                    "Pharma Companies Post Steady Growth in Quarterly Results"
                ]
            },
            "policy": {
                "positive": [
                    "Government Announces New Infrastructure Package Worth ₹1 Lakh Cr",
                    "RBI Keeps Key Rates Unchanged, Maintains Accommodative Stance",
                    "Budget 2024 Focuses on Capital Expenditure, Boost for Infrastructure"
                ],
                "negative": [
                    "RBI Raises Repo Rate by 25 bps, Tightening Monetary Policy",
                    "New Tax Rules May Impact FII Flows to Indian Markets",
                    "Government Increases Import Duty on Gold, Pressure on Rupee"
                ],
                "neutral": [
                    "Policy Committee Meeting Concludes, Decision Expected Tomorrow",
                    "Government Reviews FDI Policy for Technology Sector",
                    "RBI Governor Speaks on Financial Stability Measures"
                ]
            },
            "global": {
                "positive": [
                    "Fed Holds Rates Steady, Signals Possible Pause in Hiking Cycle",
                    "China Reopens Economy, Boost for Global Markets",
                    "Oil Prices Decline on Supply Concerns, Relief for India"
                ],
                "negative": [
                    "US Inflation Data Surprises Upside, Fed Hike Fears Rise",
                    "China Economic Growth Slows, Impact on Commodity Prices",
                    "Geopolitical Tensions Escalate, Pressure on Oil Prices"
                ],
                "neutral": [
                    "Global Markets Await US Jobs Data for Direction",
                    "European Central Bank Meeting Concludes with Mixed Signals",
                    "Asian Markets Show Mixed Sentiment Ahead of US Open"
                ]
            }
        }
        
        category_headlines = headlines.get(category, headlines["global"])
        sentiment_headlines = category_headlines.get(sentiment, category_headlines["neutral"])
        
        return random.choice(sentiment_headlines)

    def _generate_content(self, category: str, sentiment: str) -> str:
        """Generate news content"""
        content_templates = {
            "earnings": "The company reported strong quarterly results with revenue growth driven by digital transformation initiatives...",
            "policy": "The policy decision comes amid concerns about inflation and economic growth. Market participants are analyzing the implications...",
            "global": "International developments are impacting domestic markets as investors assess the global economic outlook..."
        }
        
        return content_templates.get(category, content_templates["global"])

    def _get_sentiment_score(self, sentiment: str) -> float:
        """Get sentiment score"""
        scores = {"positive": 0.8, "negative": -0.8, "neutral": 0.0}
        return scores.get(sentiment, 0.0)

    def _get_affected_tickers(self, category: str) -> List[str]:
        """Get affected tickers based on news category"""
        ticker_map = {
            "earnings": ["TCS", "INFY", "HDFCBANK", "RELIANCE"],
            "policy": ["NIFTY", "BANKNIFTY", "ALL"],
            "global": ["NIFTY", "USDINR", "CRUDEOIL"],
            "sector": ["NIFTYIT", "NIFTYBANK", "NIFTYAUTO"],
            "commodity": ["GOLD", "SILVER", "CRUDEOIL"],
            "currency": ["USDINR", "EURINR", "GBPINR"],
            "derivatives": ["NIFTY24FEB24F", "BANKNIFTY24FEB24F"],
            "macro": ["NIFTY", "BANKNIFTY", "INFLATION", "GDP"]
        }
        
        return ticker_map.get(category, ["NIFTY", "BANKNIFTY"])

    def save_test_data(self, data: List[Dict[str, Any]], filename: str):
        """Save test data to file"""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)


# Create test data generator instance
test_data_gen = TestDataGenerator()

# Generate and save test data
if __name__ == "__main__":
    # Generate futures data
    futures_data = test_data_gen.generate_futures_data(1000)
    test_data_gen.save_test_data(futures_data, "futures_test_data.json")
    
    # Generate options data
    options_data = test_data_gen.generate_options_data(1000)
    test_data_gen.save_test_data(options_data, "options_test_data.json")
    
    # Generate currency data
    currency_data = test_data_gen.generate_currency_data(1000)
    test_data_gen.save_test_data(currency_data, "currency_test_data.json")
    
    # Generate strategy configurations
    strategies = test_data_gen.generate_strategy_configurations()
    test_data_gen.save_test_data(strategies, "strategy_configs.json")
    
    # Generate risk scenarios
    risk_scenarios = test_data_gen.generate_risk_scenarios()
    test_data_gen.save_test_data(risk_scenarios, "risk_scenarios.json")
    
    # Generate market news
    market_news = test_data_gen.generate_market_news()
    test_data_gen.save_test_data(market_news, "market_news.json")
    
    print("Test data generation completed!")