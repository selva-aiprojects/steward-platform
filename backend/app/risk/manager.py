"""
Advanced Risk Management System for Algorithmic Trading
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from enum import Enum


class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    EXTREME = "EXTREME"


@dataclass
class RiskMetrics:
    var_95: float  # Value at Risk at 95% confidence
    var_99: float  # Value at Risk at 99% confidence
    max_position_size: float
    concentration_limit: float
    volatility: float
    beta: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    risk_level: RiskLevel


@dataclass
class PositionRisk:
    symbol: str
    position_size: float
    market_value: float
    pnl: float
    volatility: float
    beta: float
    contribution_to_var: float
    concentration_risk: float


class RiskManager:
    """
    Advanced risk management system with real-time monitoring and controls
    """
    
    def __init__(self, initial_capital: float = 100000.0):
        self.initial_capital = initial_capital
        self.position_limits = {
            'max_single_position': 0.10,  # Max 10% in single position
            'max_sector_exposure': 0.20,  # Max 20% in single sector
            'max_daily_loss': 0.02,       # Max 2% daily loss
            'max_total_exposure': 0.80     # Max 80% of capital exposed
        }
        
        # Risk thresholds
        self.var_threshold = 0.05  # 5% VaR limit
        self.max_drawdown_threshold = 0.15  # 15% max drawdown
        self.correlation_threshold = 0.7    # Max correlation between positions
        
        # Historical data for risk calculations
        self.historical_returns = {}
        self.portfolio_history = []
        
    def calculate_position_risk(self, symbol: str, quantity: int, price: float, 
                               portfolio_value: float) -> PositionRisk:
        """
        Calculate risk metrics for a specific position
        """
        market_value = quantity * price
        position_size = market_value / portfolio_value if portfolio_value > 0 else 0
        
        # Calculate volatility (simplified - in reality would use historical data)
        volatility = self._get_asset_volatility(symbol)
        
        # Calculate beta (simplified)
        beta = self._get_asset_beta(symbol)
        
        # Contribution to portfolio VaR (simplified)
        contribution_to_var = position_size * volatility
        
        # Concentration risk
        concentration_risk = position_size / self.position_limits['max_single_position']
        
        return PositionRisk(
            symbol=symbol,
            position_size=position_size,
            market_value=market_value,
            pnl=0,  # Would be calculated based on avg cost
            volatility=volatility,
            beta=beta,
            contribution_to_var=contribution_to_var,
            concentration_risk=concentration_risk
        )
    
    def calculate_portfolio_risk(self, positions: Dict[str, Dict], 
                                 portfolio_value: float) -> RiskMetrics:
        """
        Calculate overall portfolio risk metrics
        """
        if not positions:
            return RiskMetrics(
                var_95=0, var_99=0, max_position_size=0, 
                concentration_limit=0, volatility=0, beta=0,
                sharpe_ratio=0, sortino_ratio=0, max_drawdown=0,
                risk_level=RiskLevel.LOW
            )
        
        # Calculate position weights
        total_value = sum(pos['market_value'] for pos in positions.values())
        weights = {sym: pos['market_value']/total_value for sym, pos in positions.items()}
        
        # Calculate portfolio volatility
        portfolio_vol = self._calculate_portfolio_volatility(positions, weights)
        
        # Calculate Value at Risk (simplified)
        var_95 = portfolio_vol * 1.645  # 95% VaR assuming normal distribution
        var_99 = portfolio_vol * 2.33   # 99% VaR
        
        # Calculate other metrics
        max_pos_size = max(weights.values()) if weights else 0
        concentration_limit = max_pos_size / self.position_limits['max_single_position']
        
        # Beta (weighted average)
        portfolio_beta = sum(weights[sym] * self._get_asset_beta(sym) for sym in weights.keys())
        
        # Sharpe ratio (simplified - would need actual returns data)
        sharpe_ratio = 0  # Placeholder
        sortino_ratio = 0  # Placeholder
        max_drawdown = 0   # Placeholder
        
        # Determine risk level
        risk_level = self._determine_risk_level(var_95, max_pos_size, concentration_limit)
        
        return RiskMetrics(
            var_95=var_95,
            var_99=var_99,
            max_position_size=max_pos_size,
            concentration_limit=concentration_limit,
            volatility=portfolio_vol,
            beta=portfolio_beta,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown=max_drawdown,
            risk_level=risk_level
        )
    
    def check_trade_risk(self, symbol: str, quantity: int, price: float, 
                         current_positions: Dict[str, Dict], 
                         portfolio_value: float) -> Tuple[bool, str, Dict]:
        """
        Check if a trade passes risk controls
        """
        # Calculate position risk
        pos_risk = self.calculate_position_risk(symbol, quantity, price, portfolio_value)
        
        # Calculate new portfolio risk with proposed trade
        new_positions = current_positions.copy()
        new_market_value = quantity * price
        new_positions[symbol] = {
            'market_value': new_market_value,
            'quantity': quantity,
            'avg_price': price
        }
        
        portfolio_risk = self.calculate_portfolio_risk(new_positions, portfolio_value)
        
        # Check various risk limits
        checks = {
            'position_size_limit': pos_risk.position_size <= self.position_limits['max_single_position'],
            'concentration_limit': pos_risk.concentration_risk <= 1.0,
            'var_limit': portfolio_risk.var_95 <= self.var_threshold,
            'total_exposure_limit': sum(p['market_value'] for p in new_positions.values()) / portfolio_value <= self.position_limits['max_total_exposure']
        }
        
        # Determine if trade passes
        trade_approved = all(checks.values())
        
        # Generate reason for rejection if any check fails
        reasons = []
        if not checks['position_size_limit']:
            reasons.append(f"Position size {pos_risk.position_size:.2%} exceeds limit {self.position_limits['max_single_position']:.2%}")
        if not checks['concentration_limit']:
            reasons.append(f"Concentration risk {pos_risk.concentration_risk:.2f} exceeds 1.0")
        if not checks['var_limit']:
            reasons.append(f"Portfolio VaR {portfolio_risk.var_95:.2%} exceeds threshold {self.var_threshold:.2%}")
        if not checks['total_exposure_limit']:
            exposure = sum(p['market_value'] for p in new_positions.values()) / portfolio_value
            reasons.append(f"Total exposure {exposure:.2%} exceeds limit {self.position_limits['max_total_exposure']:.2%}")
        
        reason = "; ".join(reasons) if reasons else "Trade approved"
        
        return trade_approved, reason, {
            'position_risk': pos_risk,
            'portfolio_risk': portfolio_risk,
            'checks': checks,
            'reasons': reasons
        }
    
    def monitor_real_time_risk(self, positions: Dict[str, Dict], 
                              portfolio_value: float, timestamp: datetime) -> Dict:
        """
        Monitor real-time risk metrics and trigger alerts if needed
        """
        portfolio_risk = self.calculate_portfolio_risk(positions, portfolio_value)
        
        alerts = []
        
        # Check for VaR breaches
        if portfolio_risk.var_95 > self.var_threshold:
            alerts.append({
                'level': 'WARNING',
                'message': f"Portfolio VaR {portfolio_risk.var_95:.2%} approaching threshold {self.var_threshold:.2%}",
                'timestamp': timestamp
            })
        
        if portfolio_risk.var_99 > self.var_threshold * 1.5:
            alerts.append({
                'level': 'CRITICAL',
                'message': f"Portfolio VaR 99% {portfolio_risk.var_99:.2%} significantly exceeding threshold",
                'timestamp': timestamp
            })
        
        # Check for concentration risks
        if portfolio_risk.max_position_size > self.position_limits['max_single_position'] * 0.8:
            alerts.append({
                'level': 'WARNING',
                'message': f"Single position concentration {portfolio_risk.max_position_size:.2%} approaching limit {self.position_limits['max_single_position']:.2%}",
                'timestamp': timestamp
            })
        
        # Check for drawdown
        if portfolio_risk.max_drawdown > self.max_drawdown_threshold * 0.8:
            alerts.append({
                'level': 'WARNING',
                'message': f"Portfolio drawdown {portfolio_risk.max_drawdown:.2%} approaching limit {self.max_drawdown_threshold:.2%}",
                'timestamp': timestamp
            })
        
        return {
            'portfolio_risk': portfolio_risk,
            'alerts': alerts,
            'timestamp': timestamp
        }
    
    def _get_asset_volatility(self, symbol: str) -> float:
        """
        Get asset volatility (placeholder - would use historical data in practice)
        """
        # In a real implementation, this would fetch from historical data
        # For now, return a reasonable default based on asset class
        if 'NIFTY' in symbol or 'SENSEX' in symbol:
            return 0.18  # 18% annual volatility for indices
        elif 'BANK' in symbol or 'FIN' in symbol:
            return 0.25  # 25% for financial stocks
        else:
            return 0.30  # 30% for other stocks
        
    def _get_asset_beta(self, symbol: str) -> float:
        """
        Get asset beta (placeholder)
        """
        # In a real implementation, this would calculate beta against market index
        if 'NIFTY' in symbol or 'SENSEX' in symbol:
            return 1.0  # Market beta
        elif 'BANK' in symbol or 'FIN' in symbol:
            return 1.2  # Higher beta for financials
        else:
            return 1.0  # Default beta
        
    def _calculate_portfolio_volatility(self, positions: Dict[str, Dict], 
                                       weights: Dict[str, float]) -> float:
        """
        Calculate portfolio volatility (simplified - assumes zero correlation for now)
        """
        weighted_vols = []
        for symbol, weight in weights.items():
            vol = self._get_asset_volatility(symbol)
            weighted_vols.append(weight * vol)
        
        # Simplified calculation (would need covariance matrix for accurate calculation)
        return sum(weighted_vols)
    
    def _determine_risk_level(self, var_95: float, max_pos_size: float, 
                             concentration_limit: float) -> RiskLevel:
        """
        Determine overall risk level based on multiple factors
        """
        # Weighted scoring system
        var_score = min(var_95 / self.var_threshold, 2.0)  # Cap at 2.0
        pos_score = min(max_pos_size / self.position_limits['max_single_position'], 2.0)
        conc_score = min(concentration_limit, 2.0)
        
        avg_score = (var_score + pos_score + conc_score) / 3
        
        if avg_score <= 0.5:
            return RiskLevel.LOW
        elif avg_score <= 1.0:
            return RiskLevel.MEDIUM
        elif avg_score <= 1.5:
            return RiskLevel.HIGH
        else:
            return RiskLevel.EXTREME


# Advanced order types
class AdvancedOrderTypes:
    """
    Implementation of advanced order types for algorithmic trading
    """
    
    @staticmethod
    def create_oco_order(orders: List[Dict]) -> Dict:
        """
        Create One-Cancels-Other order group
        """
        return {
            'type': 'OCO',
            'orders': orders,
            'status': 'ACTIVE',
            'created_at': datetime.now()
        }
    
    @staticmethod
    def create_bracket_order(entry_order: Dict, stop_loss: float, 
                           take_profit: float) -> Dict:
        """
        Create bracket order (entry + stop loss + take profit)
        """
        return {
            'type': 'BRACKET',
            'entry': entry_order,
            'stop_loss': {
                'symbol': entry_order['symbol'],
                'side': 'SELL' if entry_order['side'] == 'BUY' else 'BUY',
                'quantity': entry_order['quantity'],
                'price': stop_loss,
                'order_type': 'STOP'
            },
            'take_profit': {
                'symbol': entry_order['symbol'],
                'side': 'SELL' if entry_order['side'] == 'BUY' else 'BUY',
                'quantity': entry_order['quantity'],
                'price': take_profit,
                'order_type': 'LIMIT'
            },
            'status': 'ACTIVE',
            'created_at': datetime.now()
        }
    
    @staticmethod
    def create_trailing_stop_order(symbol: str, side: str, quantity: int, 
                                 trail_percent: float) -> Dict:
        """
        Create trailing stop order
        """
        return {
            'type': 'TRAILING_STOP',
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'trail_percent': trail_percent,
            'activation_price': None,  # Will be set when position is established
            'status': 'PENDING',
            'created_at': datetime.now()
        }