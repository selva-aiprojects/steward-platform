"""
Strategy Engine for Futures, Options, and Currencies

This module implements the Strategy Engine responsible for:
1. Managing trading strategies for different asset classes (Futures, Options, Currencies)
2. Handling strategy lifecycle (creation, modification, deletion)
3. Strategy backtesting and optimization
4. Strategy performance tracking
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import uuid

logger = logging.getLogger(__name__)


class AssetClass(Enum):
    """Enumeration of supported asset classes"""
    FUTURES = "futures"
    OPTIONS = "options"
    CURRENCIES = "currencies"
    EQUITIES = "equities"


class StrategyType(Enum):
    """Enumeration of strategy types"""
    MEAN_REVERSION = "mean_reversion"
    MOMENTUM = "momentum"
    ARBITRAGE = "arbitrage"
    TREND_FOLLOWING = "trend_following"
    BREAKOUT = "breakout"
    OPTIONS_SPREAD = "options_spread"
    FOREX_CARRY = "forex_carry"
    VOLATILITY = "volatility"


class StrategyEngineInterface(ABC):
    """Abstract interface for Strategy Engine"""

    @abstractmethod
    async def create_strategy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new trading strategy"""
        pass

    @abstractmethod
    async def update_strategy(self, strategy_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing strategy"""
        pass

    @abstractmethod
    async def delete_strategy(self, strategy_id: str) -> bool:
        """Delete a strategy"""
        pass

    @abstractmethod
    async def execute_strategy(self, strategy_id: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a strategy based on market data"""
        pass

    @abstractmethod
    async def backtest_strategy(self, strategy_id: str, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Backtest a strategy using historical data"""
        pass

    @abstractmethod
    async def optimize_strategy(self, strategy_id: str, params_range: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize strategy parameters"""
        pass


class StrategyEngine(StrategyEngineInterface):
    """
    Main Strategy Engine implementation for Futures, Options, and Currencies
    """

    def __init__(self):
        self.strategies = {}
        self.active_strategies = set()
        logger.info("Strategy Engine initialized")

    async def create_strategy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new trading strategy"""
        try:
            # Generate unique strategy ID
            strategy_id = str(uuid.uuid4())
            
            # Create strategy object
            strategy_obj = {
                "id": strategy_id,
                "asset_class": params.get("asset_class", "equities"),
                "strategy_type": params.get("strategy_type", "mean_reversion"),
                "symbol": params.get("symbol", ""),
                "parameters": {
                    "entry_threshold": params.get("entry_threshold", 0.02),
                    "exit_threshold": params.get("exit_threshold", 0.01),
                    "stop_loss": params.get("stop_loss", 0.05),
                    "take_profit": params.get("take_profit", 0.10),
                    "position_size": params.get("position_size", 10000),
                    "leverage": params.get("leverage", 1.0),
                    "expiry_date": params.get("expiry_date"),
                    "strike_price": params.get("strike_price"),
                    "option_type": params.get("option_type"),
                    "lot_size": params.get("lot_size", 1)
                },
                "created_at": datetime.now().isoformat(),
                "status": "ACTIVE",
                "performance": {
                    "total_trades": 0,
                    "win_rate": 0.0,
                    "pnl": 0.0,
                    "sharpe_ratio": 0.0
                }
            }
            
            self.strategies[strategy_id] = strategy_obj
            self.active_strategies.add(strategy_id)
            
            logger.info(f"Created strategy {strategy_id} for {params.get('symbol', 'unknown')}")
            
            return {
                "success": True,
                "strategy_id": strategy_id,
                "message": f"Strategy created successfully for {params.get('symbol', 'unknown')}"
            }
        except Exception as e:
            logger.error(f"Error creating strategy: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def update_strategy(self, strategy_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing strategy"""
        try:
            if strategy_id not in self.strategies:
                return {
                    "success": False,
                    "error": f"Strategy {strategy_id} not found"
                }
            
            # Update strategy parameters
            strategy = self.strategies[strategy_id]
            strategy["parameters"].update({
                "entry_threshold": params.get("entry_threshold", strategy["parameters"]["entry_threshold"]),
                "exit_threshold": params.get("exit_threshold", strategy["parameters"]["exit_threshold"]),
                "stop_loss": params.get("stop_loss", strategy["parameters"]["stop_loss"]),
                "take_profit": params.get("take_profit", strategy["parameters"]["take_profit"]),
                "position_size": params.get("position_size", strategy["parameters"]["position_size"]),
                "leverage": params.get("leverage", strategy["parameters"]["leverage"]),
                "expiry_date": params.get("expiry_date", strategy["parameters"]["expiry_date"]),
                "strike_price": params.get("strike_price", strategy["parameters"]["strike_price"]),
                "option_type": params.get("option_type", strategy["parameters"]["option_type"]),
                "lot_size": params.get("lot_size", strategy["parameters"]["lot_size"])
            })
            
            logger.info(f"Updated strategy {strategy_id}")
            
            return {
                "success": True,
                "strategy_id": strategy_id,
                "message": f"Strategy {strategy_id} updated successfully"
            }
        except Exception as e:
            logger.error(f"Error updating strategy {strategy_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def delete_strategy(self, strategy_id: str) -> bool:
        """Delete a strategy"""
        try:
            if strategy_id in self.strategies:
                del self.strategies[strategy_id]
                self.active_strategies.discard(strategy_id)
                
                logger.info(f"Deleted strategy {strategy_id}")
                return True
            else:
                logger.warning(f"Attempted to delete non-existent strategy {strategy_id}")
                return False
        except Exception as e:
            logger.error(f"Error deleting strategy {strategy_id}: {str(e)}")
            return False

    async def execute_strategy(self, strategy_id: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a strategy based on market data"""
        try:
            if strategy_id not in self.strategies:
                return {
                    "success": False,
                    "error": f"Strategy {strategy_id} not found"
                }
            
            strategy = self.strategies[strategy_id]
            if strategy["status"] != "ACTIVE":
                return {
                    "success": False,
                    "error": f"Strategy {strategy_id} is not active"
                }
            
            # Determine action based on strategy type and market data
            action = await self._determine_action(strategy, market_data)
            
            if action:
                # Update performance metrics
                await self._update_performance(strategy_id, action)
                
                logger.info(f"Executed action {action['action']} for strategy {strategy_id}")
                
                return {
                    "success": True,
                    "strategy_id": strategy_id,
                    "action": action,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": True,
                    "strategy_id": strategy_id,
                    "action": None,
                    "message": "No action taken based on current market conditions"
                }
        except Exception as e:
            logger.error(f"Error executing strategy {strategy_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def backtest_strategy(self, strategy_id: str, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Backtest a strategy using historical data"""
        try:
            if strategy_id not in self.strategies:
                return {
                    "success": False,
                    "error": f"Strategy {strategy_id} not found"
                }
            
            strategy = self.strategies[strategy_id]
            
            # Initialize backtest results
            backtest_results = {
                "strategy_id": strategy_id,
                "total_trades": 0,
                "successful_trades": 0,
                "total_pnl": 0.0,
                "max_drawdown": 0.0,
                "sharpe_ratio": 0.0,
                "win_rate": 0.0,
                "trades": []
            }
            
            # Simulate strategy execution on historical data
            position = None
            entry_price = 0
            total_pnl = 0
            
            for i, candle in enumerate(historical_data):
                # Determine if we should enter/exit based on strategy logic
                action = await self._simulate_action(strategy, candle, position)
                
                if action and action["action"] == "ENTRY":
                    # Enter position
                    position = {
                        "entry_price": candle["close"],
                        "timestamp": candle["timestamp"],
                        "quantity": action["quantity"]
                    }
                    entry_price = candle["close"]
                elif position and action and action["action"] == "EXIT":
                    # Exit position and calculate PnL
                    exit_price = candle["close"]
                    pnl = (exit_price - entry_price) * position["quantity"]
                    if strategy["parameters"].get("option_type") == "PUT":
                        pnl = (entry_price - exit_price) * position["quantity"]
                    
                    total_pnl += pnl
                    
                    backtest_results["trades"].append({
                        "entry_timestamp": position["timestamp"],
                        "exit_timestamp": candle["timestamp"],
                        "entry_price": entry_price,
                        "exit_price": exit_price,
                        "quantity": position["quantity"],
                        "pnl": pnl,
                        "pnl_pct": (pnl / (entry_price * position["quantity"])) * 100 if entry_price * position["quantity"] != 0 else 0
                    })
                    
                    backtest_results["total_trades"] += 1
                    if pnl > 0:
                        backtest_results["successful_trades"] += 1
                    
                    position = None
            
            # Calculate final metrics
            backtest_results["total_pnl"] = total_pnl
            if backtest_results["total_trades"] > 0:
                backtest_results["win_rate"] = backtest_results["successful_trades"] / backtest_results["total_trades"]
            
            # Calculate Sharpe ratio (simplified)
            if len(backtest_results["trades"]) > 1:
                returns = [trade["pnl_pct"] for trade in backtest_results["trades"]]
                avg_return = sum(returns) / len(returns)
                volatility = (sum([(r - avg_return) ** 2 for r in returns]) / len(returns)) ** 0.5
                backtest_results["sharpe_ratio"] = avg_return / volatility if volatility != 0 else 0
            
            logger.info(f"Backtested strategy {strategy_id}")
            
            return {
                "success": True,
                "strategy_id": strategy_id,
                "results": backtest_results
            }
        except Exception as e:
            logger.error(f"Error backtesting strategy {strategy_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def optimize_strategy(self, strategy_id: str, params_range: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize strategy parameters"""
        try:
            if strategy_id not in self.strategies:
                return {
                    "success": False,
                    "error": f"Strategy {strategy_id} not found"
                }
            
            # For now, return the current parameters as optimal
            # In a real implementation, this would run optimization algorithms
            strategy = self.strategies[strategy_id]
            
            optimization_results = {
                "strategy_id": strategy_id,
                "optimized_parameters": strategy["parameters"],
                "optimization_method": "grid_search",  # Could be genetic_algorithm, particle_swarm, etc.
                "best_score": 0.0,  # Would be calculated based on backtest results
                "iterations": 0
            }
            
            logger.info(f"Optimized strategy {strategy_id}")
            
            return {
                "success": True,
                "strategy_id": strategy_id,
                "results": optimization_results
            }
        except Exception as e:
            logger.error(f"Error optimizing strategy {strategy_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _validate_strategy_parameters(self, params: Dict[str, Any]) -> bool:
        """Validate strategy parameters based on asset class"""
        # Common validations
        if params.get("entry_threshold", 0) <= 0 or params.get("exit_threshold", 0) <= 0:
            raise ValueError("Threshold values must be positive")
        
        if params.get("stop_loss", 0) <= 0:
            raise ValueError("Stop loss must be positive")
        
        if params.get("take_profit", 0) <= 0:
            raise ValueError("Take profit must be positive")
        
        # Asset class specific validations
        if params.get("asset_class") == "options":
            if params.get("strike_price") is None:
                raise ValueError("Strike price is required for options strategies")
            if params.get("option_type") not in ["CALL", "PUT"]:
                raise ValueError("Option type must be CALL or PUT")
        
        if params.get("asset_class") == "futures":
            if params.get("expiry_date") is None:
                raise ValueError("Expiry date is required for futures strategies")
        
        return True

    async def _determine_action(self, strategy: Dict[str, Any], market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Determine trading action based on strategy and market data"""
        try:
            current_price = market_data.get("last_price") or market_data.get("close")
            if not current_price:
                return None
            
            # Get strategy parameters
            params = strategy["parameters"]
            
            # Different logic based on strategy type
            action = None
            
            if strategy["strategy_type"] == "mean_reversion":
                # Mean reversion logic
                if current_price < params["entry_threshold"]:
                    action = {
                        "action": "BUY",
                        "symbol": strategy["symbol"],
                        "quantity": int(params["position_size"] / current_price),
                        "price": current_price,
                        "strategy": strategy["strategy_type"]
                    }
                elif current_price > params["exit_threshold"]:
                    action = {
                        "action": "SELL",
                        "symbol": strategy["symbol"],
                        "quantity": int(params["position_size"] / current_price),
                        "price": current_price,
                        "strategy": strategy["strategy_type"]
                    }
            
            elif strategy["strategy_type"] == "trend_following":
                # Trend following logic
                moving_avg = market_data.get("moving_average", current_price)
                if current_price > moving_avg * (1 + params["entry_threshold"]/100):
                    action = {
                        "action": "BUY",
                        "symbol": strategy["symbol"],
                        "quantity": int(params["position_size"] / current_price),
                        "price": current_price,
                        "strategy": strategy["strategy_type"]
                    }
                elif current_price < moving_avg * (1 - params["exit_threshold"]/100):
                    action = {
                        "action": "SELL",
                        "symbol": strategy["symbol"],
                        "quantity": int(params["position_size"] / current_price),
                        "price": current_price,
                        "strategy": strategy["strategy_type"]
                    }
            
            elif strategy["strategy_type"] == "volatility":
                # Volatility-based logic
                volatility = market_data.get("volatility", 0)
                if volatility > params["entry_threshold"]:
                    # High volatility - could be options strategy
                    action = {
                        "action": "BUY" if params["option_type"] == "CALL" else "SELL",
                        "symbol": strategy["symbol"],
                        "quantity": params["lot_size"] or 1,
                        "price": current_price,
                        "strategy": strategy["strategy_type"]
                    }
            
            # Add stop loss and take profit checks
            if action:
                # Check if stop loss or take profit conditions are met
                entry_price = market_data.get("entry_price", current_price)
                if entry_price:
                    pnl_pct = ((current_price - entry_price) / entry_price) * 100
                    if abs(pnl_pct) >= params["stop_loss"] or abs(pnl_pct) >= params["take_profit"]:
                        action["action"] = "SELL" if action["action"] == "BUY" else "BUY"
            
            return action
        except Exception as e:
            logger.error(f"Error determining action: {str(e)}")
            return None

    async def _simulate_action(self, strategy: Dict[str, Any], candle: Dict[str, Any], position: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Simulate action for backtesting"""
        # Similar to _determine_action but for backtesting purposes
        current_price = candle.get("close")
        if not current_price:
            return None
        
        params = strategy["parameters"]
        
        # Simple entry/exit logic for backtesting
        if not position:
            # Look for entry condition
            if strategy["strategy_type"] == "mean_reversion":
                if current_price < params["entry_threshold"]:
                    return {
                        "action": "ENTRY",
                        "quantity": int(params["position_size"] / current_price)
                    }
        else:
            # Look for exit condition
            entry_price = position["entry_price"]
            pnl_pct = ((current_price - entry_price) / entry_price) * 100
            
            if abs(pnl_pct) >= params["take_profit"] or abs(pnl_pct) >= params["stop_loss"]:
                return {
                    "action": "EXIT",
                    "quantity": position["quantity"]
                }
        
        return None

    async def _update_performance(self, strategy_id: str, action: Dict[str, Any]) -> None:
        """Update strategy performance metrics"""
        if strategy_id in self.strategies:
            # In a real implementation, this would update actual performance metrics
            # based on trade results
            pass


# Singleton instance
strategy_engine = StrategyEngine()