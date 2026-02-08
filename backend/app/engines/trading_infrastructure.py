"""
Main Trading Infrastructure for Futures, Options, and Currencies

This module implements the core trading infrastructure that integrates:
1. Strategy Engine
2. Parameter Engine
3. Risk Engine
4. AI Filter Engine
5. Execution Engine
6. Version Control Engine
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import asyncio
import uuid

logger = logging.getLogger(__name__)

# Import the individual engines
from app.engines.strategy_engine import strategy_engine
from app.engines.param_engine import param_engine
from app.engines.risk_engine import risk_engine
from app.engines.ai_filter_engine import ai_filter_engine
from app.engines.execution_engine import execution_engine
from app.engines.version_control_engine import version_control_engine


class TradingInfrastructure:
    """
    Main Trading Infrastructure that orchestrates all trading engines
    for Futures, Options, and Currencies
    """

    def __init__(self):
        self.strategy_engine = strategy_engine
        self.param_engine = param_engine
        self.risk_engine = risk_engine
        self.ai_filter_engine = ai_filter_engine
        self.execution_engine = execution_engine
        self.version_control_engine = version_control_engine
        
        # Track active trading sessions
        self.active_sessions = {}
        
        # Track performance metrics
        self.performance_metrics = {
            "total_trades": 0,
            "successful_trades": 0,
            "failed_trades": 0,
            "total_pnl": 0.0,
            "avg_execution_time": 0.0
        }
        
        logger.info("Trading Infrastructure initialized with all engines")

    async def initialize_trading_session(self, user_id: str, asset_class: str, initial_capital: float) -> Dict[str, Any]:
        """Initialize a new trading session"""
        try:
            session_id = str(uuid.uuid4())
            
            session_data = {
                "session_id": session_id,
                "user_id": user_id,
                "asset_class": asset_class,
                "initial_capital": initial_capital,
                "current_capital": initial_capital,
                "positions": {},
                "trades": [],
                "start_time": datetime.now().isoformat(),
                "status": "ACTIVE",
                "risk_limits": await self._get_default_risk_limits(asset_class)
            }
            
            self.active_sessions[session_id] = session_data
            
            logger.info(f"Initialized trading session {session_id} for user {user_id}")
            
            return {
                "success": True,
                "session_id": session_id,
                "message": f"Trading session initialized for {asset_class}"
            }
        except Exception as e:
            logger.error(f"Error initializing trading session: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def execute_trading_cycle(self, session_id: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a complete trading cycle"""
        try:
            if session_id not in self.active_sessions:
                return {
                    "success": False,
                    "error": f"Session {session_id} not found"
                }
            
            session = self.active_sessions[session_id]
            
            # Step 1: AI Market Analysis
            ai_analysis_start = datetime.now()
            ai_result = await self.ai_filter_engine.analyze_market_sentiment(
                market_data.get("news", []),
                market_data.get("social", [])
            )
            ai_analysis_time = (datetime.now() - ai_analysis_start).total_seconds()
            
            if not ai_result["success"]:
                return {
                    "success": False,
                    "error": f"AI analysis failed: {ai_result['error']}"
                }
            
            # Step 2: Strategy Selection & Configuration
            strategy_selection_start = datetime.now()
            selected_strategy = await self._select_strategy(session, ai_result["analysis"])
            strategy_selection_time = (datetime.now() - strategy_selection_start).total_seconds()
            
            if not selected_strategy["success"]:
                return {
                    "success": False,
                    "error": f"Strategy selection failed: {selected_strategy['error']}"
                }
            
            # Step 3: Parameter Optimization
            param_opt_start = datetime.now()
            optimized_params = await self.param_engine.optimize_parameters(
                selected_strategy["strategy_id"],
                selected_strategy["optimization_config"]
            )
            param_opt_time = (datetime.now() - param_opt_start).total_seconds()
            
            if not optimized_params["success"]:
                return {
                    "success": False,
                    "error": f"Parameter optimization failed: {optimized_params['error']}"
                }
            
            # Step 4: Risk Assessment
            risk_assessment_start = datetime.now()
            risk_result = await self.risk_engine.check_risk_limits({
                "strategy_id": selected_strategy["strategy_id"],
                "parameters": optimized_params["optimized_parameters"],
                "market_data": market_data,
                "session_capital": session["current_capital"]
            })
            risk_assessment_time = (datetime.now() - risk_assessment_start).total_seconds()
            
            if not risk_result["success"]:
                return {
                    "success": False,
                    "error": f"Risk check failed: {risk_result['error']}"
                }
            
            # Step 5: Signal Generation
            signal_gen_start = datetime.now()
            signal_result = await self.ai_filter_engine.generate_signals({
                "market_data": market_data,
                "strategy_config": optimized_params["optimized_parameters"],
                "risk_assessment": risk_result["assessment"]
            })
            signal_gen_time = (datetime.now() - signal_gen_start).total_seconds()
            
            if not signal_result["success"]:
                return {
                    "success": False,
                    "error": f"Signal generation failed: {signal_result['error']}"
                }
            
            # Step 6: Order Execution
            execution_start = datetime.now()
            execution_result = await self.execution_engine.execute_order({
                "signal": signal_result["signal"],
                "parameters": optimized_params["optimized_parameters"],
                "risk_limits": risk_result["assessment"],
                "session_id": session_id
            })
            execution_time = (datetime.now() - execution_start).total_seconds()
            
            if not execution_result["success"]:
                return {
                    "success": False,
                    "error": f"Order execution failed: {execution_result['error']}"
                }
            
            # Update performance metrics
            self.performance_metrics["total_trades"] += 1
            if execution_result.get("status") == "FILLED":
                self.performance_metrics["successful_trades"] += 1
                self.performance_metrics["total_pnl"] += execution_result.get("pnl", 0)
            
            # Calculate average execution time
            total_execution_time = ai_analysis_time + strategy_selection_time + param_opt_time + risk_assessment_time + signal_gen_time + execution_time
            self.performance_metrics["avg_execution_time"] = (
                (self.performance_metrics["avg_execution_time"] * (self.performance_metrics["total_trades"] - 1) + total_execution_time) /
                self.performance_metrics["total_trades"]
            )
            
            trading_cycle_result = {
                "session_id": session_id,
                "cycle_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "ai_analysis_time": ai_analysis_time,
                "strategy_selection_time": strategy_selection_time,
                "param_optimization_time": param_opt_time,
                "risk_assessment_time": risk_assessment_time,
                "signal_generation_time": signal_gen_time,
                "execution_time": execution_time,
                "total_cycle_time": total_execution_time,
                "ai_analysis": ai_result["analysis"],
                "selected_strategy": selected_strategy["strategy"],
                "optimized_parameters": optimized_params["optimized_parameters"],
                "risk_assessment": risk_result["assessment"],
                "trading_signal": signal_result["signal"],
                "execution_result": execution_result["result"],
                "capital_before": session["current_capital"],
                "capital_after": session["current_capital"] + execution_result.get("pnl", 0)
            }
            
            # Update session with trade result
            session["current_capital"] += execution_result.get("pnl", 0)
            session["trades"].append(trading_cycle_result)
            
            logger.info(f"Completed trading cycle for session {session_id}")
            
            return {
                "success": True,
                "trading_cycle_result": trading_cycle_result
            }
        except Exception as e:
            logger.error(f"Error in trading cycle: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def backtest_strategy(self, strategy_config: Dict[str, Any], historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Backtest a strategy using historical data"""
        try:
            # Create temporary strategy
            strategy_creation = await self.strategy_engine.create_strategy(strategy_config)
            if not strategy_creation["success"]:
                return strategy_creation
            
            strategy_id = strategy_creation["strategy_id"]
            
            # Run backtest through the strategy engine
            backtest_result = await self.strategy_engine.backtest_strategy(strategy_id, historical_data)
            
            # Clean up temporary strategy
            await self.strategy_engine.delete_strategy(strategy_id)
            
            return backtest_result
        except Exception as e:
            logger.error(f"Error in backtesting: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def optimize_strategy_parameters(self, strategy_id: str, optimization_config: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize strategy parameters using historical data"""
        try:
            # Use the parameter engine to optimize parameters
            optimization_result = await self.param_engine.optimize_parameters(strategy_id, optimization_config)
            
            if optimization_result["success"]:
                # Update strategy with optimized parameters
                update_result = await self.strategy_engine.update_strategy(
                    strategy_id,
                    optimization_result["optimized_parameters"]
                )
                
                if update_result["success"]:
                    return {
                        "success": True,
                        "strategy_id": strategy_id,
                        "optimized_parameters": optimization_result["optimized_parameters"],
                        "message": "Parameters optimized and strategy updated"
                    }
                else:
                    return update_result
            else:
                return optimization_result
        except Exception as e:
            logger.error(f"Error optimizing strategy parameters: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def monitor_portfolio_risk(self, session_id: str) -> Dict[str, Any]:
        """Monitor overall portfolio risk"""
        try:
            if session_id not in self.active_sessions:
                return {
                    "success": False,
                    "error": f"Session {session_id} not found"
                }
            
            session = self.active_sessions[session_id]
            
            # Get all current positions
            positions = session["positions"]
            
            # Calculate portfolio risk
            risk_result = await self.risk_engine.calculate_portfolio_risk(positions)
            
            if risk_result["success"]:
                # Check against session risk limits
                portfolio_risk = risk_result["portfolio_risk"]
                
                risk_alerts = []
                risk_limits = session["risk_limits"]
                
                if portfolio_risk["total_value"] > risk_limits["max_portfolio_value"]:
                    risk_alerts.append({
                        "type": "PORTFOLIO_SIZE_EXCEEDED",
                        "level": "WARNING",
                        "message": f"Portfolio value {portfolio_risk['total_value']} exceeds limit {risk_limits['max_portfolio_value']}"
                    })
                
                if portfolio_risk["total_risk"] > risk_limits["max_portfolio_risk"]:
                    risk_alerts.append({
                        "type": "PORTFOLIO_RISK_EXCEEDED",
                        "level": "CRITICAL",
                        "message": f"Portfolio risk {portfolio_risk['total_risk']} exceeds limit {risk_limits['max_portfolio_risk']}"
                    })
                
                if portfolio_risk["max_drawdown"] > risk_limits["max_drawdown"]:
                    risk_alerts.append({
                        "type": "MAX_DRAWDOWN_EXCEEDED",
                        "level": "CRITICAL",
                        "message": f"Portfolio drawdown {portfolio_risk['max_drawdown']} exceeds limit {risk_limits['max_drawdown']}"
                    })
                
                return {
                    "success": True,
                    "portfolio_risk": portfolio_risk,
                    "risk_alerts": risk_alerts,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return risk_result
        except Exception as e:
            logger.error(f"Error monitoring portfolio risk: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def generate_trading_report(self, session_id: str, report_type: str = "daily") -> Dict[str, Any]:
        """Generate trading reports"""
        try:
            if session_id not in self.active_sessions:
                return {
                    "success": False,
                    "error": f"Session {session_id} not found"
                }
            
            session = self.active_sessions[session_id]
            
            # Calculate report based on type
            if report_type == "daily":
                report = await self._generate_daily_report(session)
            elif report_type == "weekly":
                report = await self._generate_weekly_report(session)
            elif report_type == "monthly":
                report = await self._generate_monthly_report(session)
            elif report_type == "performance":
                report = await self._generate_performance_report(session)
            else:
                return {
                    "success": False,
                    "error": f"Unknown report type: {report_type}"
                }
            
            return {
                "success": True,
                "report_type": report_type,
                "report_data": report,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error generating trading report: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def terminate_trading_session(self, session_id: str) -> Dict[str, Any]:
        """Terminate a trading session"""
        try:
            if session_id not in self.active_sessions:
                return {
                    "success": False,
                    "error": f"Session {session_id} not found"
                }
            
            session = self.active_sessions[session_id]
            
            # Close all positions
            for symbol, position in session["positions"].items():
                if position["quantity"] != 0:
                    # Close position
                    close_result = await self.execution_engine.execute_order({
                        "symbol": symbol,
                        "quantity": abs(position["quantity"]),
                        "side": "BUY" if position["quantity"] < 0 else "SELL",
                        "order_type": "MARKET",
                        "session_id": session_id
                    })
            
            # Update session status
            session["status"] = "TERMINATED"
            session["end_time"] = datetime.now().isoformat()
            
            logger.info(f"Terminated trading session {session_id}")
            
            return {
                "success": True,
                "session_id": session_id,
                "message": f"Trading session {session_id} terminated"
            }
        except Exception as e:
            logger.error(f"Error terminating trading session: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _select_strategy(self, session: Dict[str, Any], market_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Select appropriate strategy based on market conditions and session parameters"""
        try:
            # Determine market regime from analysis
            market_regime = market_analysis.get("market_regime", "NORMAL")
            volatility = market_analysis.get("volatility", 0.2)
            trend_strength = market_analysis.get("trend_strength", 0.5)
            
            # Select strategy based on market conditions and asset class
            asset_class = session["asset_class"]
            
            if asset_class == "futures":
                if market_regime == "HIGH_VOLATILITY":
                    strategy_type = "BREAKOUT"
                elif trend_strength > 0.7:
                    strategy_type = "TREND_FOLLOWING"
                else:
                    strategy_type = "MEAN_REVERSION"
            elif asset_class == "options":
                if volatility > 0.3:
                    strategy_type = "VOLATILITY"
                elif market_regime == "RANGE_BOUND":
                    strategy_type = "IRON_CONDOR"
                else:
                    strategy_type = "COVERED_CALL"
            elif asset_class == "currencies":
                if trend_strength > 0.6:
                    strategy_type = "MOMENTUM"
                elif market_regime == "HIGH_VOLATILITY":
                    strategy_type = "CARRY"
                else:
                    strategy_type = "MEAN_REVERSION"
            else:  # equities
                if trend_strength > 0.7:
                    strategy_type = "TREND_FOLLOWING"
                elif market_regime == "HIGH_VOLATILITY":
                    strategy_type = "BREAKOUT"
                else:
                    strategy_type = "MEAN_REVERSION"
            
            # Create strategy configuration
            strategy_config = {
                "strategy_type": strategy_type,
                "asset_class": asset_class,
                "risk_tolerance": session.get("risk_tolerance", "MODERATE"),
                "capital_allocation": session.get("capital_allocation", 0.1),  # 10% of capital
                "market_analysis": market_analysis
            }
            
            # Create the strategy
            strategy_creation = await self.strategy_engine.create_strategy(strategy_config)
            
            if strategy_creation["success"]:
                return {
                    "success": True,
                    "strategy_id": strategy_creation["strategy_id"],
                    "strategy": strategy_creation["strategy"],
                    "optimization_config": {
                        "method": "genetic_algorithm",
                        "bounds": self._get_optimization_bounds(strategy_type, asset_class),
                        "max_iterations": 100
                    }
                }
            else:
                return strategy_creation
        except Exception as e:
            logger.error(f"Error selecting strategy: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _get_optimization_bounds(self, strategy_type: str, asset_class: str) -> Dict[str, Any]:
        """Get optimization bounds for different strategy types"""
        bounds = {
            "entry_threshold": (0.001, 0.05),  # 0.1% to 5%
            "exit_threshold": (0.001, 0.03),  # 0.1% to 3%
            "stop_loss": (0.01, 0.15),        # 1% to 15%
            "take_profit": (0.02, 0.30),      # 2% to 30%
            "position_size": (1000, 100000)   # Rs. 1,000 to Rs. 1,00,000
        }
        
        # Adjust bounds based on strategy type
        if strategy_type in ["MEAN_REVERSION", "BREAKOUT"]:
            bounds["entry_threshold"] = (0.005, 0.03)
            bounds["exit_threshold"] = (0.001, 0.02)
        
        elif strategy_type in ["TREND_FOLLOWING", "MOMENTUM"]:
            bounds["entry_threshold"] = (0.01, 0.05)
            bounds["exit_threshold"] = (0.005, 0.03)
        
        elif strategy_type == "VOLATILITY":
            bounds["entry_threshold"] = (0.02, 0.10)
            bounds["exit_threshold"] = (0.01, 0.05)
        
        # Adjust for asset class
        if asset_class == "options":
            bounds["stop_loss"] = (0.05, 0.40)  # Higher stops for options
            bounds["take_profit"] = (0.10, 0.60)  # Higher targets for options
        
        elif asset_class == "currencies":
            bounds["entry_threshold"] = (0.0005, 0.02)  # Smaller moves in forex
            bounds["exit_threshold"] = (0.0002, 0.01)
        
        return bounds

    async def _get_default_risk_limits(self, asset_class: str) -> Dict[str, Any]:
        """Get default risk limits based on asset class"""
        if asset_class == "futures":
            return {
                "max_portfolio_value": 5000000,  # 50 Lakhs
                "max_portfolio_risk": 500000,   # 5 Lakhs
                "max_position_size": 1000000,   # 10 Lakhs per position
                "max_daily_loss": 200000,       # 2 Lakhs daily loss limit
                "max_drawdown": 0.15,           # 15% max drawdown
                "max_leverage": 5               # 5x max leverage
            }
        elif asset_class == "options":
            return {
                "max_portfolio_value": 2000000,  # 20 Lakhs
                "max_portfolio_risk": 300000,   # 3 Lakhs
                "max_position_size": 500000,    # 5 Lakhs per position
                "max_daily_loss": 100000,       # 1 Lakh daily loss
                "max_drawdown": 0.20,           # 20% max drawdown
                "max_leverage": 10              # 10x max leverage
            }
        elif asset_class == "currencies":
            return {
                "max_portfolio_value": 3000000,  # 30 Lakhs
                "max_portfolio_risk": 400000,   # 4 Lakhs
                "max_position_size": 800000,    # 8 Lakhs per position
                "max_daily_loss": 150000,       # 1.5 Lakhs daily loss
                "max_drawdown": 0.12,           # 12% max drawdown
                "max_leverage": 20              # 20x max leverage
            }
        else:  # equities
            return {
                "max_portfolio_value": 10000000, # 1 Crore
                "max_portfolio_risk": 1000000,  # 10 Lakhs
                "max_position_size": 2000000,   # 20 Lakhs per position
                "max_daily_loss": 500000,       # 5 Lakhs daily loss
                "max_drawdown": 0.10,           # 10% max drawdown
                "max_leverage": 2               # 2x max leverage
            }

    async def _generate_daily_report(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Generate daily trading report"""
        # Calculate daily metrics
        today_trades = [trade for trade in session["trades"] 
                       if datetime.fromisoformat(trade["timestamp"]).date() == datetime.now().date()]
        
        daily_pnl = sum(trade.get("execution_result", {}).get("pnl", 0) for trade in today_trades)
        daily_trades = len(today_trades)
        
        return {
            "report_type": "daily",
            "date": datetime.now().date().isoformat(),
            "session_id": session["session_id"],
            "daily_pnl": daily_pnl,
            "daily_trades": daily_trades,
            "winning_trades": len([t for t in today_trades if t.get("execution_result", {}).get("pnl", 0) > 0]),
            "total_capital": session["current_capital"],
            "positions": session["positions"]
        }

    async def _generate_weekly_report(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Generate weekly trading report"""
        # Calculate weekly metrics
        week_start = datetime.now().date() - timedelta(days=datetime.now().weekday())
        week_trades = [trade for trade in session["trades"] 
                      if datetime.fromisoformat(trade["timestamp"]).date() >= week_start]
        
        weekly_pnl = sum(trade.get("execution_result", {}).get("pnl", 0) for trade in week_trades)
        weekly_trades = len(week_trades)
        
        return {
            "report_type": "weekly",
            "week_start": week_start.isoformat(),
            "week_end": datetime.now().date().isoformat(),
            "session_id": session["session_id"],
            "weekly_pnl": weekly_pnl,
            "weekly_trades": weekly_trades,
            "win_rate": len([t for t in week_trades if t.get("execution_result", {}).get("pnl", 0) > 0]) / len(week_trades) if week_trades else 0,
            "total_capital": session["current_capital"],
            "top_performing_symbols": self._get_top_symbols(week_trades, 5)
        }

    async def _generate_monthly_report(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Generate monthly trading report"""
        # Calculate monthly metrics
        month_start = datetime.now().date().replace(day=1)
        month_trades = [trade for trade in session["trades"] 
                       if datetime.fromisoformat(trade["timestamp"]).date() >= month_start]
        
        monthly_pnl = sum(trade.get("execution_result", {}).get("pnl", 0) for trade in month_trades)
        monthly_trades = len(month_trades)
        
        return {
            "report_type": "monthly",
            "month": month_start.strftime("%Y-%m"),
            "session_id": session["session_id"],
            "monthly_pnl": monthly_pnl,
            "monthly_trades": monthly_trades,
            "sharpe_ratio": self._calculate_sharpe_ratio(month_trades),
            "max_drawdown": self._calculate_max_drawdown(month_trades),
            "total_capital": session["current_capital"],
            "profit_factor": self._calculate_profit_factor(month_trades)
        }

    async def _generate_performance_report(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        all_trades = session["trades"]
        
        total_pnl = sum(trade.get("execution_result", {}).get("pnl", 0) for trade in all_trades)
        total_trades = len(all_trades)
        winning_trades = len([t for t in all_trades if t.get("execution_result", {}).get("pnl", 0) > 0])
        
        return {
            "report_type": "performance",
            "session_id": session["session_id"],
            "total_pnl": total_pnl,
            "total_trades": total_trades,
            "win_rate": winning_trades / total_trades if total_trades > 0 else 0,
            "avg_win": sum(t.get("execution_result", {}).get("pnl", 0) for t in all_trades if t.get("execution_result", {}).get("pnl", 0) > 0) / winning_trades if winning_trades > 0 else 0,
            "avg_loss": sum(t.get("execution_result", {}).get("pnl", 0) for t in all_trades if t.get("execution_result", {}).get("pnl", 0) < 0) / (total_trades - winning_trades) if (total_trades - winning_trades) > 0 else 0,
            "sharpe_ratio": self._calculate_sharpe_ratio(all_trades),
            "sortino_ratio": self._calculate_sortino_ratio(all_trades),
            "max_drawdown": self._calculate_max_drawdown(all_trades),
            "profit_factor": self._calculate_profit_factor(all_trades),
            "total_capital": session["current_capital"],
            "return_on_capital": (session["current_capital"] - session["initial_capital"]) / session["initial_capital"] if session["initial_capital"] != 0 else 0
        }

    def _get_top_symbols(self, trades: List[Dict[str, Any]], n: int) -> List[Dict[str, Any]]:
        """Get top performing symbols"""
        symbol_pnls = {}
        for trade in trades:
            symbol = trade.get("execution_result", {}).get("symbol", "UNKNOWN")
            pnl = trade.get("execution_result", {}).get("pnl", 0)
            if symbol in symbol_pnls:
                symbol_pnls[symbol]["pnl"] += pnl
                symbol_pnls[symbol]["trades"] += 1
            else:
                symbol_pnls[symbol] = {"pnl": pnl, "trades": 1}
        
        sorted_symbols = sorted(symbol_pnls.items(), key=lambda x: x[1]["pnl"], reverse=True)
        return [{"symbol": sym, "total_pnl": data["pnl"], "trade_count": data["trades"]} for sym, data in sorted_symbols[:n]]

    def _calculate_sharpe_ratio(self, trades: List[Dict[str, Any]]) -> float:
        """Calculate Sharpe ratio"""
        if len(trades) < 2:
            return 0.0
        
        pnls = [trade.get("execution_result", {}).get("pnl", 0) for trade in trades]
        avg_return = sum(pnls) / len(pnls)
        volatility = (sum([(p - avg_return) ** 2 for p in pnls]) / len(pnls)) ** 0.5
        
        return avg_return / volatility if volatility != 0 else 0.0

    def _calculate_sortino_ratio(self, trades: List[Dict[str, Any]]) -> float:
        """Calculate Sortino ratio"""
        if len(trades) < 2:
            return 0.0
        
        pnls = [trade.get("execution_result", {}).get("pnl", 0) for trade in trades]
        avg_return = sum(pnls) / len(pnls)
        
        # Calculate downside deviation (only negative returns)
        negative_pnls = [p for p in pnls if p < 0]
        if negative_pnls:
            downside_deviation = (sum([p ** 2 for p in negative_pnls]) / len(negative_pnls)) ** 0.5
        else:
            downside_deviation = 0.0
        
        return avg_return / downside_deviation if downside_deviation != 0 else 0.0

    def _calculate_max_drawdown(self, trades: List[Dict[str, Any]]) -> float:
        """Calculate maximum drawdown"""
        if not trades:
            return 0.0
        
        cumulative_pnl = 0
        peak = 0
        max_dd = 0
        
        for trade in trades:
            cumulative_pnl += trade.get("execution_result", {}).get("pnl", 0)
            if cumulative_pnl > peak:
                peak = cumulative_pnl
            drawdown = (peak - cumulative_pnl) / peak if peak != 0 else 0
            if drawdown > max_dd:
                max_dd = drawdown
        
        return max_dd

    def _calculate_profit_factor(self, trades: List[Dict[str, Any]]) -> float:
        """Calculate profit factor"""
        if not trades:
            return 0.0
        
        gross_profit = sum(max(0, trade.get("execution_result", {}).get("pnl", 0)) for trade in trades)
        gross_loss = abs(sum(min(0, trade.get("execution_result", {}).get("pnl", 0)) for trade in trades))
        
        return gross_profit / gross_loss if gross_loss != 0 else float('inf')


# Singleton instance
trading_infrastructure = TradingInfrastructure()