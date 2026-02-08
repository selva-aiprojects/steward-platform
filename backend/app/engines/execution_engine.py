"""
Execution Engine for Futures, Options, and Currencies

This module implements the Execution Engine responsible for:
1. Processing trading signals from the AI Filter Engine
2. Executing trades across different asset classes (Futures, Options, Currencies)
3. Managing order routing and execution
4. Handling trade confirmations and settlements
5. Managing execution risk and slippage
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import asyncio
import uuid

logger = logging.getLogger(__name__)


class ExecutionEngineInterface(ABC):
    """Abstract interface for Execution Engine"""

    @abstractmethod
    async def execute_order(self, order_details: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a trading order"""
        pass

    @abstractmethod
    async def route_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Route order to appropriate broker/exchange"""
        pass

    @abstractmethod
    async def manage_execution_risk(self, trade: Dict[str, Any]) -> Dict[str, Any]:
        """Manage execution risk and slippage"""
        pass

    @abstractmethod
    async def confirm_execution(self, execution_id: str) -> Dict[str, Any]:
        """Confirm trade execution"""
        pass

    @abstractmethod
    async def handle_settlement(self, trade_id: str) -> Dict[str, Any]:
        """Handle trade settlement"""
        pass

    @abstractmethod
    async def monitor_execution(self, execution_id: str) -> Dict[str, Any]:
        """Monitor ongoing execution"""
        pass


class ExecutionEngine(ExecutionEngineInterface):
    """
    Main Execution Engine implementation for Futures, Options, and Currencies
    """

    def __init__(self):
        self.order_queue = []
        self.executions = {}
        self.broker_connections = {}
        self.execution_stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "avg_slippage": 0.0,
            "total_volume": 0
        }
        logger.info("Execution Engine initialized")

    async def execute_order(self, order_details: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a trading order"""
        try:
            # Generate unique execution ID
            execution_id = str(uuid.uuid4())
            
            # Validate order details
            validation_result = await self._validate_order(order_details)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": f"Invalid order: {validation_result['errors']}"
                }
            
            # Determine asset class and execution method
            asset_class = order_details.get("asset_class", "equities")
            
            # Route order based on asset class
            if asset_class in ["futures", "options", "currencies"]:
                execution_result = await self._execute_derivative_order(order_details, execution_id)
            else:
                execution_result = await self._execute_equity_order(order_details, execution_id)
            
            if execution_result["success"]:
                # Update execution statistics
                self.execution_stats["total_executions"] += 1
                self.execution_stats["successful_executions"] += 1
                self.execution_stats["total_volume"] += execution_result.get("filled_quantity", 0) * execution_result.get("avg_fill_price", 0)
                
                # Store execution details
                self.executions[execution_id] = {
                    "order_details": order_details,
                    "execution_result": execution_result,
                    "timestamp": datetime.now().isoformat(),
                    "status": "COMPLETED"
                }
                
                logger.info(f"Successfully executed order {execution_id}")
                
                return {
                    "success": True,
                    "execution_id": execution_id,
                    "result": execution_result
                }
            else:
                # Update failure statistics
                self.execution_stats["total_executions"] += 1
                self.execution_stats["failed_executions"] += 1
                
                logger.warning(f"Failed to execute order {execution_id}: {execution_result['error']}")
                
                return {
                    "success": False,
                    "execution_id": execution_id,
                    "error": execution_result["error"]
                }
        except Exception as e:
            logger.error(f"Error executing order: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def route_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Route order to appropriate broker/exchange based on asset class"""
        try:
            asset_class = order.get("asset_class", "equities")
            symbol = order.get("symbol", "")
            
            # Determine the best execution venue based on asset class
            if asset_class == "futures":
                # Route to futures exchange (e.g., NSE, MCX)
                execution_venue = self._select_futures_exchange(symbol)
            elif asset_class == "options":
                # Route to options exchange
                execution_venue = self._select_options_exchange(symbol)
            elif asset_class == "currencies":
                # Route to currency exchange
                execution_venue = self._select_currency_exchange(symbol)
            else:
                # Default to equity exchange
                execution_venue = self._select_equity_exchange(symbol)
            
            # Connect to appropriate broker
            broker = await self._get_broker_connection(execution_venue)
            
            if not broker:
                return {
                    "success": False,
                    "error": f"No broker connection available for {execution_venue}"
                }
            
            # Prepare order for specific venue
            venue_order = await self._prepare_order_for_venue(order, execution_venue)
            
            # Submit order to broker
            submission_result = await broker.submit_order(venue_order)
            
            if submission_result["success"]:
                routing_info = {
                    "execution_venue": execution_venue,
                    "broker_id": broker.id,
                    "order_id": submission_result["order_id"],
                    "timestamp": datetime.now().isoformat(),
                    "routing_fee": submission_result.get("routing_fee", 0)
                }
                
                logger.info(f"Routed order to {execution_venue} via {broker.id}")
                
                return {
                    "success": True,
                    "routing_info": routing_info
                }
            else:
                return {
                    "success": False,
                    "error": submission_result["error"]
                }
        except Exception as e:
            logger.error(f"Error routing order: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def manage_execution_risk(self, trade: Dict[str, Any]) -> Dict[str, Any]:
        """Manage execution risk and slippage"""
        try:
            symbol = trade.get("symbol", "")
            quantity = trade.get("quantity", 0)
            side = trade.get("side", "BUY").upper()
            asset_class = trade.get("asset_class", "equities")
            
            # Calculate execution risk metrics
            market_impact = await self._calculate_market_impact(symbol, quantity, side, asset_class)
            slippage_risk = await self._calculate_slippage_risk(symbol, quantity, side, asset_class)
            timing_risk = await self._calculate_timing_risk(trade)
            
            # Total execution risk
            total_execution_risk = market_impact + slippage_risk + timing_risk
            
            # Recommend execution strategy based on risk
            execution_strategy = "MARKET"
            if total_execution_risk > 0.02:  # More than 2% risk
                execution_strategy = "LIMIT"
            elif total_execution_risk > 0.05:  # More than 5% risk
                execution_strategy = "ICEBERG"
            
            # For high-risk situations, suggest algorithmic execution
            if total_execution_risk > 0.10:  # More than 10% risk
                execution_strategy = "ALGO"  # Use algorithmic execution
            
            risk_management = {
                "market_impact": market_impact,
                "slippage_risk": slippage_risk,
                "timing_risk": timing_risk,
                "total_execution_risk": total_execution_risk,
                "recommended_strategy": execution_strategy,
                "max_slippage_tolerance": trade.get("max_slippage", 0.01),  # 1% default
                "risk_level": "LOW" if total_execution_risk < 0.02 else "MEDIUM" if total_execution_risk < 0.05 else "HIGH",
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Managed execution risk for {symbol}, risk level: {risk_management['risk_level']}")
            
            return {
                "success": True,
                "risk_management": risk_management
            }
        except Exception as e:
            logger.error(f"Error managing execution risk: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def confirm_execution(self, execution_id: str) -> Dict[str, Any]:
        """Confirm trade execution"""
        try:
            if execution_id not in self.executions:
                return {
                    "success": False,
                    "error": f"Execution {execution_id} not found"
                }
            
            execution = self.executions[execution_id]
            
            # Get confirmation from broker
            order_id = execution["execution_result"].get("order_id")
            if not order_id:
                return {
                    "success": False,
                    "error": "No order ID found for execution confirmation"
                }
            
            broker = await self._get_broker_connection(execution["execution_result"]["execution_venue"])
            if not broker:
                return {
                    "success": False,
                    "error": "Unable to connect to broker for confirmation"
                }
            
            confirmation = await broker.get_order_status(order_id)
            
            if confirmation["status"] == "FILLED":
                # Update execution status
                execution["status"] = "CONFIRMED"
                execution["confirmation"] = confirmation
                
                logger.info(f"Confirmed execution {execution_id}")
                
                return {
                    "success": True,
                    "execution_id": execution_id,
                    "confirmation": confirmation
                }
            else:
                return {
                    "success": False,
                    "execution_id": execution_id,
                    "status": confirmation["status"],
                    "message": "Order not yet filled"
                }
        except Exception as e:
            logger.error(f"Error confirming execution {execution_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def handle_settlement(self, trade_id: str) -> Dict[str, Any]:
        """Handle trade settlement"""
        try:
            # In a real implementation, this would interface with clearing houses
            # and settlement systems
            
            # For now, simulate settlement process
            settlement_details = {
                "trade_id": trade_id,
                "settlement_date": (datetime.now().date() + timedelta(days=2)).isoformat(),  # T+2 settlement
                "settlement_status": "PENDING",
                "settlement_amount": 0,
                "fees": 0,
                "taxes": 0,
                "timestamp": datetime.now().isoformat()
            }
            
            # Calculate settlement amount based on execution details
            if trade_id in self.executions:
                execution = self.executions[trade_id]
                result = execution["execution_result"]
                
                quantity = result.get("filled_quantity", 0)
                avg_price = result.get("avg_fill_price", 0)
                asset_class = execution["order_details"].get("asset_class", "equities")
                
                gross_amount = quantity * avg_price
                
                # Calculate fees based on asset class
                fees = self._calculate_settlement_fees(gross_amount, asset_class)
                
                # Calculate taxes based on asset class and holding period
                taxes = self._calculate_settlement_taxes(gross_amount, asset_class, result.get("holding_period", 0))
                
                settlement_details["settlement_amount"] = gross_amount
                settlement_details["fees"] = fees
                settlement_details["taxes"] = taxes
                settlement_details["net_amount"] = gross_amount - fees - taxes
            
            logger.info(f"Initiated settlement for trade {trade_id}")
            
            return {
                "success": True,
                "settlement_details": settlement_details
            }
        except Exception as e:
            logger.error(f"Error handling settlement for trade {trade_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def monitor_execution(self, execution_id: str) -> Dict[str, Any]:
        """Monitor ongoing execution"""
        try:
            if execution_id not in self.executions:
                return {
                    "success": False,
                    "error": f"Execution {execution_id} not found"
                }
            
            execution = self.executions[execution_id]
            
            # Get current status from broker
            order_id = execution["execution_result"].get("order_id")
            if not order_id:
                return {
                    "success": False,
                    "error": "No order ID found for monitoring"
                }
            
            broker = await self._get_broker_connection(execution["execution_result"]["execution_venue"])
            if not broker:
                return {
                    "success": False,
                    "error": "Unable to connect to broker for monitoring"
                }
            
            status = await broker.get_order_status(order_id)
            
            # Update execution with latest status
            execution["last_status_update"] = status
            execution["last_updated"] = datetime.now().isoformat()
            
            monitoring_info = {
                "execution_id": execution_id,
                "status": status["status"],
                "filled_quantity": status.get("filled_quantity", 0),
                "remaining_quantity": status.get("remaining_quantity", 0),
                "avg_fill_price": status.get("avg_fill_price", 0),
                "last_updated": datetime.now().isoformat()
            }
            
            logger.info(f"Monitored execution {execution_id}, status: {status['status']}")
            
            return {
                "success": True,
                "monitoring_info": monitoring_info
            }
        except Exception as e:
            logger.error(f"Error monitoring execution {execution_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _validate_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Validate order details"""
        errors = []
        
        # Required fields check
        required_fields = ["symbol", "quantity", "side", "asset_class"]
        for field in required_fields:
            if field not in order or not order[field]:
                errors.append(f"Missing required field: {field}")
        
        # Quantity validation
        if "quantity" in order:
            if not isinstance(order["quantity"], (int, float)) or order["quantity"] <= 0:
                errors.append("Quantity must be a positive number")
        
        # Side validation
        if "side" in order:
            if order["side"].upper() not in ["BUY", "SELL"]:
                errors.append("Side must be BUY or SELL")
        
        # Asset class validation
        if "asset_class" in order:
            valid_asset_classes = ["equities", "futures", "options", "currencies"]
            if order["asset_class"] not in valid_asset_classes:
                errors.append(f"Asset class must be one of {valid_asset_classes}")
        
        # Price validation for limit orders
        if order.get("order_type", "MARKET").upper() == "LIMIT":
            if "limit_price" not in order or order["limit_price"] <= 0:
                errors.append("Limit price is required for limit orders")
        
        # Options-specific validations
        if order.get("asset_class") == "options":
            if "strike_price" not in order:
                errors.append("Strike price is required for options orders")
            if "option_type" not in order or order["option_type"] not in ["CALL", "PUT"]:
                errors.append("Option type (CALL/PUT) is required for options orders")
        
        # Futures-specific validations
        if order.get("asset_class") == "futures":
            if "expiry_date" not in order:
                errors.append("Expiry date is required for futures orders")
        
        # Currency-specific validations
        if order.get("asset_class") == "currencies":
            if len(order.get("symbol", "")) != 6 or not order["symbol"].endswith("INR"):
                errors.append("Currency symbol should be 6 characters ending with INR (e.g., USDINR)")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    async def _execute_derivative_order(self, order: Dict[str, Any], execution_id: str) -> Dict[str, Any]:
        """Execute derivative orders (Futures, Options, Currencies)"""
        try:
            # Route order to appropriate exchange
            routing_result = await self.route_order(order)
            if not routing_result["success"]:
                return routing_result
            
            # Manage execution risk
            risk_result = await self.manage_execution_risk(order)
            if not risk_result["success"]:
                logger.warning(f"Risk management warning for order {execution_id}: {risk_result.get('error', 'Risk exceeded thresholds')}")
            
            # For derivatives, we often need to calculate margin requirements
            margin_required = await self._calculate_margin_requirement(order)
            
            # Execute the order
            order_details = {
                "symbol": order["symbol"],
                "quantity": order["quantity"],
                "side": order["side"].upper(),
                "order_type": order.get("order_type", "MARKET").upper(),
                "product_type": self._get_product_type(order["asset_class"]),  # NRML for derivatives
                "validity": order.get("validity", "DAY"),
                "disclosed_quantity": order.get("disclosed_quantity", 0),
                "trigger_price": order.get("trigger_price", 0),
                "squareoff": order.get("squareoff", 0),
                "stoploss": order.get("stoploss", 0),
                "trailing_stoploss": order.get("trailing_stoploss", 0),
                "margin_required": margin_required
            }
            
            # Add asset class specific parameters
            if order["asset_class"] == "options":
                order_details.update({
                    "strike_price": order.get("strike_price"),
                    "option_type": order.get("option_type"),
                    "expiry_date": order.get("expiry_date")
                })
            elif order["asset_class"] == "futures":
                order_details.update({
                    "expiry_date": order.get("expiry_date"),
                    "lot_size": order.get("lot_size", 1)
                })
            elif order["asset_class"] == "currencies":
                order_details.update({
                    "transaction_type": order.get("transaction_type", "REGULAR")
                })
            
            # Submit order to broker
            broker = await self._get_broker_connection(routing_result["routing_info"]["execution_venue"])
            execution_result = await broker.place_order(order_details)
            
            return execution_result
        except Exception as e:
            logger.error(f"Error executing derivative order: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _execute_equity_order(self, order: Dict[str, Any], execution_id: str) -> Dict[str, Any]:
        """Execute equity orders"""
        try:
            # Route order to equity exchange
            routing_result = await self.route_order(order)
            if not routing_result["success"]:
                return routing_result
            
            # Execute the order
            order_details = {
                "symbol": order["symbol"],
                "quantity": order["quantity"],
                "side": order["side"].upper(),
                "order_type": order.get("order_type", "MARKET").upper(),
                "product_type": "MIS" if order.get("intraday", False) else "NRML",
                "validity": order.get("validity", "DAY"),
                "disclosed_quantity": order.get("disclosed_quantity", 0),
                "trigger_price": order.get("trigger_price", 0)
            }
            
            # Submit order to broker
            broker = await self._get_broker_connection(routing_result["routing_info"]["execution_venue"])
            execution_result = await broker.place_order(order_details)
            
            return execution_result
        except Exception as e:
            logger.error(f"Error executing equity order: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _calculate_market_impact(self, symbol: str, quantity: int, side: str, asset_class: str) -> float:
        """Calculate market impact for the order"""
        # This would typically use real market microstructure data
        # For now, using simplified calculation
        
        # Get average daily volume for the symbol
        avg_daily_volume = await self._get_average_daily_volume(symbol, asset_class)
        
        if avg_daily_volume == 0:
            return 0.02  # Default 2% impact if no volume data
        
        # Calculate participation rate
        participation_rate = (quantity * 100) / avg_daily_volume
        
        # Market impact formula (simplified)
        # Impact increases with participation rate and volatility
        volatility = await self._get_volatility(symbol, asset_class)
        
        market_impact = 0.001 * (participation_rate ** 0.6) * (volatility ** 0.5)
        
        # Adjust for asset class
        if asset_class in ["futures", "options"]:
            market_impact *= 1.2  # Higher impact for derivatives
        elif asset_class == "currencies":
            market_impact *= 0.8  # Lower impact for currencies
        
        return min(0.10, market_impact)  # Cap at 10%

    async def _calculate_slippage_risk(self, symbol: str, quantity: int, side: str, asset_class: str) -> float:
        """Calculate potential slippage risk"""
        # Get bid-ask spread
        spread = await self._get_bid_ask_spread(symbol, asset_class)
        
        # Calculate slippage based on order size relative to market depth
        depth_factor = min(1.0, (quantity / 10000))  # Simplified depth calculation
        
        slippage_risk = spread * depth_factor
        
        # Add additional slippage for volatile markets
        volatility = await self._get_volatility(symbol, asset_class)
        slippage_risk += 0.0005 * volatility  # Additional slippage in volatile markets
        
        return min(0.05, slippage_risk)  # Cap at 5%

    async def _calculate_timing_risk(self, trade: Dict[str, Any]) -> float:
        """Calculate timing risk based on market conditions"""
        # Timing risk is higher during market open/close and low liquidity periods
        current_time = datetime.now()
        
        # Higher risk during market opening/closing hours
        hour = current_time.hour
        minute = current_time.minute
        
        timing_risk = 0
        if (9 <= hour <= 10) or (15 <= hour <= 16):  # Market opening/closing
            timing_risk = 0.01
        elif 12 <= hour <= 13:  # Lunch break period
            timing_risk = 0.005
        else:
            timing_risk = 0.002  # Base timing risk
        
        # Add risk for volatile market conditions
        symbol = trade.get("symbol", "")
        asset_class = trade.get("asset_class", "equities")
        volatility = await self._get_volatility(symbol, asset_class)
        
        timing_risk += 0.001 * volatility
        
        return min(0.03, timing_risk)  # Cap at 3%

    def _get_product_type(self, asset_class: str) -> str:
        """Get appropriate product type for asset class"""
        if asset_class in ["futures", "options", "currencies"]:
            return "NRML"  # Normal product for derivatives
        else:
            return "MIS"  # Margin intraday square-off for equities

    async def _get_broker_connection(self, venue: str):
        """Get broker connection for the specified venue"""
        # In a real implementation, this would return actual broker connection objects
        # For now, returning a mock object
        if venue not in self.broker_connections:
            # Initialize broker connection
            from app.services.broker.live import LiveBrokerAdapter
            self.broker_connections[venue] = LiveBrokerAdapter()
        
        return self.broker_connections[venue]

    def _select_futures_exchange(self, symbol: str) -> str:
        """Select appropriate futures exchange"""
        if symbol.endswith("FUT"):
            return "NSE_FO"  # NSE Futures & Options
        else:
            return "MCX"  # MCX for commodities

    def _select_options_exchange(self, symbol: str) -> str:
        """Select appropriate options exchange"""
        return "NSE_FO"  # NSE Futures & Options

    def _select_currency_exchange(self, symbol: str) -> str:
        """Select appropriate currency exchange"""
        return "NSE_CURRENCY"  # NSE Currency

    def _select_equity_exchange(self, symbol: str) -> str:
        """Select appropriate equity exchange"""
        return "NSE_EQ"  # NSE Equity

    async def _prepare_order_for_venue(self, order: Dict[str, Any], venue: str) -> Dict[str, Any]:
        """Prepare order for specific execution venue"""
        # This would format the order according to the specific requirements of each venue
        # For now, returning the order as is
        return order.copy()

    async def _calculate_margin_requirement(self, order: Dict[str, Any]) -> float:
        """Calculate margin requirement for derivative orders"""
        # This would use actual margin calculation formulas
        # For now, using simplified calculation
        
        symbol = order["symbol"]
        quantity = order["quantity"]
        asset_class = order["asset_class"]
        
        # Get current price
        from app.services.kite_service import kite_service
        quote = kite_service.get_quote(symbol)
        current_price = quote.get("last_price", 0) if quote else 0
        
        if asset_class == "futures":
            # For futures, margin is typically a percentage of contract value
            contract_value = quantity * current_price
            margin_percentage = 0.06  # 6% for most futures
            return contract_value * margin_percentage
        
        elif asset_class == "options":
            # For options, margin depends on whether buying or selling
            if order["side"].upper() == "BUY":
                # For buying options, margin is premium paid
                return quantity * current_price  # Premium
            else:
                # For selling options, margin is higher
                if order.get("option_type") == "CALL":
                    # Short call margin
                    return max(0.07 * current_price * quantity, 0.03 * current_price * quantity)
                else:
                    # Short put margin
                    return max(0.07 * current_price * quantity, 0.03 * current_price * quantity)
        
        elif asset_class == "currencies":
            # Currency margin calculation
            contract_value = quantity * current_price
            margin_percentage = 0.04  # 4% for currency derivatives
            return contract_value * margin_percentage
        
        return 0

    async def _get_average_daily_volume(self, symbol: str, asset_class: str) -> int:
        """Get average daily volume for the symbol"""
        # In a real implementation, this would fetch from market data
        # For now, returning a mock value
        return 1000000  # 1 million shares

    async def _get_volatility(self, symbol: str, asset_class: str) -> float:
        """Get volatility for the symbol"""
        # In a real implementation, this would calculate from historical data
        # For now, returning a mock value
        return 0.20  # 20% volatility

    async def _get_bid_ask_spread(self, symbol: str, asset_class: str) -> float:
        """Get bid-ask spread for the symbol"""
        # In a real implementation, this would fetch from market data
        # For now, returning a mock value
        return 0.001  # 0.1% spread

    async def _calculate_settlement_fees(self, gross_amount: float, asset_class: str) -> float:
        """Calculate settlement fees based on asset class"""
        # Fee structure varies by asset class
        if asset_class == "equities":
            return gross_amount * 0.0000325  # 0.00325% for equities
        elif asset_class in ["futures", "currencies"]:
            return gross_amount * 0.0001  # 0.01% for futures/currencies
        elif asset_class == "options":
            return gross_amount * 0.0005  # 0.05% for options
        else:
            return gross_amount * 0.0000325  # Default

    async def _calculate_settlement_taxes(self, gross_amount: float, asset_class: str, holding_period: int) -> float:
        """Calculate settlement taxes based on asset class and holding period"""
        # Tax calculation varies by asset class and holding period
        if asset_class == "equities":
            if holding_period < 365:  # STT for short term
                return gross_amount * 0.00025  # 0.025% for delivery
            else:
                return 0  # No STT for long term
        elif asset_class in ["futures", "currencies"]:
            return gross_amount * 0.0001  # Transaction tax
        elif asset_class == "options":
            return gross_amount * 0.0005  # Higher tax for options
        else:
            return 0


# Singleton instance
execution_engine = ExecutionEngine()