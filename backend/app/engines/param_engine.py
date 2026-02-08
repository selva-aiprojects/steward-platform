"""
Parameter Engine for Futures, Options, and Currencies

This module implements the Parameter Engine responsible for:
1. Managing strategy parameters for different asset classes (Futures, Options, Currencies)
2. Validating parameter combinations
3. Parameter optimization and tuning
4. Parameter version control and history
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import uuid

logger = logging.getLogger(__name__)


class ParameterEngineInterface(ABC):
    """Abstract interface for Parameter Engine"""

    @abstractmethod
    async def set_parameters(self, strategy_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set parameters for a strategy"""
        pass

    @abstractmethod
    async def get_parameters(self, strategy_id: str) -> Dict[str, Any]:
        """Get parameters for a strategy"""
        pass

    @abstractmethod
    async def validate_parameters(self, strategy_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate parameters for a strategy"""
        pass

    @abstractmethod
    async def optimize_parameters(self, strategy_id: str, optimization_config: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize parameters for a strategy"""
        pass

    @abstractmethod
    async def get_parameter_history(self, strategy_id: str) -> List[Dict[str, Any]]:
        """Get parameter history for a strategy"""
        pass


class ParameterEngine(ParameterEngineInterface):
    """
    Main Parameter Engine implementation for Futures, Options, and Currencies
    """

    def __init__(self):
        self.parameters = {}
        self.parameter_history = {}
        logger.info("Parameter Engine initialized")

    async def set_parameters(self, strategy_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set parameters for a strategy"""
        try:
            # Validate parameters before setting
            validation_result = await self.validate_parameters(strategy_id, params)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": f"Invalid parameters: {validation_result['errors']}"
                }

            # Generate parameter version
            param_version = str(uuid.uuid4())[:8]
            
            # Create parameter record
            param_record = {
                "version": param_version,
                "parameters": params,
                "updated_at": datetime.now().isoformat(),
                "strategy_id": strategy_id
            }
            
            # Store current parameters
            self.parameters[strategy_id] = param_record
            
            # Add to history
            if strategy_id not in self.parameter_history:
                self.parameter_history[strategy_id] = []
            self.parameter_history[strategy_id].append(param_record)
            
            logger.info(f"Set parameters for strategy {strategy_id}, version {param_version}")
            
            return {
                "success": True,
                "strategy_id": strategy_id,
                "version": param_version,
                "message": f"Parameters set successfully for strategy {strategy_id}"
            }
        except Exception as e:
            logger.error(f"Error setting parameters for strategy {strategy_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_parameters(self, strategy_id: str) -> Dict[str, Any]:
        """Get parameters for a strategy"""
        try:
            if strategy_id not in self.parameters:
                return {
                    "success": False,
                    "error": f"No parameters found for strategy {strategy_id}"
                }
            
            param_record = self.parameters[strategy_id]
            
            return {
                "success": True,
                "strategy_id": strategy_id,
                "parameters": param_record["parameters"],
                "version": param_record["version"],
                "updated_at": param_record["updated_at"]
            }
        except Exception as e:
            logger.error(f"Error getting parameters for strategy {strategy_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def validate_parameters(self, strategy_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate parameters for a strategy"""
        try:
            errors = []
            
            # Validate common parameters
            if "entry_threshold" in params:
                if not isinstance(params["entry_threshold"], (int, float)) or params["entry_threshold"] <= 0:
                    errors.append("Entry threshold must be a positive number")
            
            if "exit_threshold" in params:
                if not isinstance(params["exit_threshold"], (int, float)) or params["exit_threshold"] <= 0:
                    errors.append("Exit threshold must be a positive number")
            
            if "stop_loss" in params:
                if not isinstance(params["stop_loss"], (int, float)) or params["stop_loss"] <= 0:
                    errors.append("Stop loss must be a positive number")
            
            if "take_profit" in params:
                if not isinstance(params["take_profit"], (int, float)) or params["take_profit"] <= 0:
                    errors.append("Take profit must be a positive number")
            
            if "position_size" in params:
                if not isinstance(params["position_size"], (int, float)) or params["position_size"] <= 0:
                    errors.append("Position size must be a positive number")
            
            if "leverage" in params:
                if not isinstance(params["leverage"], (int, float)) or params["leverage"] <= 0:
                    errors.append("Leverage must be a positive number")
            
            # Validate asset class specific parameters
            asset_class = params.get("asset_class", "equities")
            
            if asset_class == "options":
                if "strike_price" in params:
                    if not isinstance(params["strike_price"], (int, float)) or params["strike_price"] <= 0:
                        errors.append("Strike price must be a positive number")
                
                if "option_type" in params:
                    if params["option_type"] not in ["CALL", "PUT"]:
                        errors.append("Option type must be CALL or PUT")
                
                if "expiry_date" in params:
                    try:
                        datetime.fromisoformat(params["expiry_date"].replace("Z", "+00:00"))
                    except ValueError:
                        errors.append("Expiry date must be in ISO format")
            
            elif asset_class == "futures":
                if "expiry_date" in params:
                    try:
                        datetime.fromisoformat(params["expiry_date"].replace("Z", "+00:00"))
                    except ValueError:
                        errors.append("Expiry date must be in ISO format")
                
                if "lot_size" in params:
                    if not isinstance(params["lot_size"], int) or params["lot_size"] <= 0:
                        errors.append("Lot size must be a positive integer")
            
            elif asset_class == "currencies":
                if "currency_pair" in params:
                    if not isinstance(params["currency_pair"], str) or len(params["currency_pair"]) != 6:
                        errors.append("Currency pair must be a 6-character string (e.g., USDINR)")
            
            # Validate parameter relationships
            if "entry_threshold" in params and "exit_threshold" in params:
                if params["entry_threshold"] <= params["exit_threshold"]:
                    errors.append("Entry threshold must be greater than exit threshold")
            
            if "stop_loss" in params and "take_profit" in params:
                if params["stop_loss"] >= params["take_profit"]:
                    errors.append("Stop loss must be less than take profit")
            
            # Check for required parameters based on strategy type
            strategy_type = params.get("strategy_type", "mean_reversion")
            
            if strategy_type == "options_spread":
                required_params = ["leg1_strike", "leg2_strike", "leg1_type", "leg2_type"]
                for param in required_params:
                    if param not in params:
                        errors.append(f"Missing required parameter for options spread: {param}")
            
            elif strategy_type == "forex_carry":
                required_params = ["base_currency", "quote_currency", "carry_rate"]
                for param in required_params:
                    if param not in params:
                        errors.append(f"Missing required parameter for forex carry: {param}")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors
            }
        except Exception as e:
            logger.error(f"Error validating parameters for strategy {strategy_id}: {str(e)}")
            return {
                "valid": False,
                "errors": [str(e)]
            }

    async def optimize_parameters(self, strategy_id: str, optimization_config: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize parameters for a strategy"""
        try:
            if strategy_id not in self.parameters:
                return {
                    "success": False,
                    "error": f"No parameters found for strategy {strategy_id}"
                }
            
            # Get current parameters
            current_params = self.parameters[strategy_id]["parameters"]
            
            # Get optimization bounds
            param_bounds = optimization_config.get("bounds", {})
            optimization_method = optimization_config.get("method", "grid_search")
            max_iterations = optimization_config.get("max_iterations", 100)
            
            # Perform optimization based on method
            if optimization_method == "grid_search":
                optimized_params = await self._grid_search_optimization(current_params, param_bounds, max_iterations)
            elif optimization_method == "genetic_algorithm":
                optimized_params = await self._genetic_algorithm_optimization(current_params, param_bounds, max_iterations)
            elif optimization_method == "particle_swarm":
                optimized_params = await self._particle_swarm_optimization(current_params, param_bounds, max_iterations)
            else:
                # Default to grid search
                optimized_params = await self._grid_search_optimization(current_params, param_bounds, max_iterations)
            
            # Validate optimized parameters
            validation_result = await self.validate_parameters(strategy_id, optimized_params)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": f"Optimized parameters are invalid: {validation_result['errors']}"
                }
            
            # Update parameters with optimized values
            result = await self.set_parameters(strategy_id, optimized_params)
            
            return {
                "success": True,
                "strategy_id": strategy_id,
                "optimized_parameters": optimized_params,
                "optimization_method": optimization_method,
                "result": result
            }
        except Exception as e:
            logger.error(f"Error optimizing parameters for strategy {strategy_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_parameter_history(self, strategy_id: str) -> List[Dict[str, Any]]:
        """Get parameter history for a strategy"""
        try:
            if strategy_id not in self.parameter_history:
                return {
                    "success": False,
                    "error": f"No parameter history found for strategy {strategy_id}"
                }
            
            history = self.parameter_history[strategy_id]
            
            return {
                "success": True,
                "strategy_id": strategy_id,
                "history": history
            }
        except Exception as e:
            logger.error(f"Error getting parameter history for strategy {strategy_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _grid_search_optimization(self, current_params: Dict[str, Any], param_bounds: Dict[str, Any], max_iterations: int) -> Dict[str, Any]:
        """Perform grid search optimization"""
        # This is a simplified implementation
        # In a real system, this would connect to a backtesting engine to evaluate parameter sets
        optimized_params = current_params.copy()
        
        # For now, just return the current parameters as "optimized"
        # In a real implementation, this would iterate through parameter combinations
        # and select the one with the best backtest results
        
        logger.info(f"Performed grid search optimization for strategy parameters")
        return optimized_params

    async def _genetic_algorithm_optimization(self, current_params: Dict[str, Any], param_bounds: Dict[str, Any], max_iterations: int) -> Dict[str, Any]:
        """Perform genetic algorithm optimization"""
        # This is a simplified implementation
        # In a real system, this would implement a genetic algorithm for parameter optimization
        optimized_params = current_params.copy()
        
        logger.info(f"Performed genetic algorithm optimization for strategy parameters")
        return optimized_params

    async def _particle_swarm_optimization(self, current_params: Dict[str, Any], param_bounds: Dict[str, Any], max_iterations: int) -> Dict[str, Any]:
        """Perform particle swarm optimization"""
        # This is a simplified implementation
        # In a real system, this would implement a particle swarm optimization algorithm
        optimized_params = current_params.copy()
        
        logger.info(f"Performed particle swarm optimization for strategy parameters")
        return optimized_params


# Singleton instance
param_engine = ParameterEngine()