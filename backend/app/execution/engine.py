"""
Advanced Execution Engine for Algorithmic Trading Orders
"""
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import asyncio
import time
import random


@dataclass
class Order:
    """
    Represents a trading order with all necessary attributes
    """
    symbol: str
    side: str  # 'BUY' or 'SELL'
    quantity: int
    price: float
    order_type: str  # 'MARKET', 'LIMIT', 'STOP', 'STOP_LIMIT', 'TRAILING_STOP'
    user_id: int
    strategy_id: Optional[int] = None
    timestamp: datetime = None
    filled_quantity: int = 0
    average_fill_price: float = 0.0
    status: str = 'PENDING'  # PENDING, PARTIALLY_FILLED, FILLED, CANCELLED
    stop_price: Optional[float] = None  # For stop orders
    trailing_percent: Optional[float] = None  # For trailing stops
    time_in_force: str = 'DAY'  # DAY, GTC, IOC, FOK
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class Fill:
    """
    Represents a fill of an order
    """
    order_id: str
    symbol: str
    side: str
    quantity: int
    price: float
    timestamp: datetime
    fees: float = 0.0


class ExecutionEngine:
    """
    Advanced execution engine with multiple order types and smart routing
    """
    
    def __init__(self):
        self.orders: Dict[str, Order] = {}
        self.fills: List[Fill] = []
        self.execution_stats = {
            'total_orders': 0,
            'total_fills': 0,
            'avg_execution_time': 0.0,
            'slippage_metrics': []
        }
        
        # Execution algorithms
        self.algorithms = {
            'TWAP': self._execute_twap,
            'VWAP': self._execute_vwap,
            'PARTICIPATE': self._execute_participate,
            'MIDPOINT': self._execute_midpoint
        }
        
    async def place_order(self, order: Order) -> Dict[str, Any]:
        """
        Place an order with the execution engine
        """
        order_id = f"ORDER_{int(time.time() * 1000000)}"
        order.order_id = order_id
        self.orders[order_id] = order
        
        # Process the order based on type
        if order.order_type == 'MARKET':
            result = await self._execute_market_order(order)
        elif order.order_type == 'LIMIT':
            result = await self._execute_limit_order(order)
        elif order.order_type == 'STOP':
            result = await self._execute_stop_order(order)
        elif order.order_type == 'TRAILING_STOP':
            result = await self._execute_trailing_stop_order(order)
        elif order.order_type == 'ALGO':
            # Algorithmic order execution
            algo_type = getattr(order, 'algo_type', 'TWAP')
            result = await self.execute_algorithmic_order(order, algo_type)
        else:
            result = {
                'status': 'REJECTED',
                'reason': f'Unsupported order type: {order.order_type}',
                'order_id': order_id
            }
        
        # Update execution statistics
        self.execution_stats['total_orders'] += 1
        
        return result
    
    async def _execute_market_order(self, order: Order) -> Dict[str, Any]:
        """
        Execute a market order
        """
        # Simulate market execution with realistic slippage
        market_price = await self._get_current_price(order.symbol)
        
        # Apply slippage based on order size and market liquidity
        slippage = self._calculate_slippage(order.quantity, market_price, order.side)
        execution_price = market_price * (1 + slippage) if order.side == 'BUY' else market_price * (1 - slippage)
        
        # Execute the fill
        fill = Fill(
            order_id=order.order_id,
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=execution_price,
            timestamp=datetime.now()
        )
        
        self.fills.append(fill)
        
        # Update order status
        order.filled_quantity = order.quantity
        order.average_fill_price = execution_price
        order.status = 'FILLED'
        
        # Calculate fees
        fees = self._calculate_fees(order.quantity, execution_price)
        fill.fees = fees
        
        return {
            'status': 'FILLED',
            'order_id': order.order_id,
            'filled_quantity': order.quantity,
            'average_fill_price': execution_price,
            'fees': fees,
            'execution_time': (datetime.now() - order.timestamp).total_seconds()
        }
    
    async def _execute_limit_order(self, order: Order) -> Dict[str, Any]:
        """
        Execute a limit order
        """
        # Check if limit price is hit
        current_price = await self._get_current_price(order.symbol)
        
        if (order.side == 'BUY' and current_price <= order.price) or \
           (order.side == 'SELL' and current_price >= order.price):
            
            # Execute at limit price or better
            fill = Fill(
                order_id=order.order_id,
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                price=min(current_price, order.price) if order.side == 'BUY' else max(current_price, order.price),
                timestamp=datetime.now()
            )
            
            self.fills.append(fill)
            
            # Update order status
            order.filled_quantity = order.quantity
            order.average_fill_price = fill.price
            order.status = 'FILLED'
            
            # Calculate fees
            fees = self._calculate_fees(order.quantity, fill.price)
            fill.fees = fees
            
            return {
                'status': 'FILLED',
                'order_id': order.order_id,
                'filled_quantity': order.quantity,
                'average_fill_price': fill.price,
                'fees': fees,
                'execution_time': (datetime.now() - order.timestamp).total_seconds()
            }
        else:
            # Order remains pending
            return {
                'status': 'PENDING',
                'order_id': order.order_id,
                'filled_quantity': 0,
                'average_fill_price': 0.0,
                'message': f'Limit price not reached. Current: {current_price}, Limit: {order.price}'
            }
    
    async def _execute_stop_order(self, order: Order) -> Dict[str, Any]:
        """
        Execute a stop order
        """
        if not order.stop_price:
            return {
                'status': 'REJECTED',
                'reason': 'Stop price not specified',
                'order_id': order.order_id
            }
        
        current_price = await self._get_current_price(order.symbol)
        
        # Check if stop price is triggered
        if (order.side == 'BUY' and current_price >= order.stop_price) or \
           (order.side == 'SELL' and current_price <= order.stop_price):
            
            # Convert to market order and execute
            market_order = Order(
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                price=current_price,
                order_type='MARKET',
                user_id=order.user_id,
                strategy_id=order.strategy_id
            )
            
            return await self._execute_market_order(market_order)
        else:
            # Stop not triggered yet
            return {
                'status': 'PENDING',
                'order_id': order.order_id,
                'filled_quantity': 0,
                'average_fill_price': 0.0,
                'message': f'Stop price not triggered. Current: {current_price}, Stop: {order.stop_price}'
            }
    
    async def _execute_trailing_stop_order(self, order: Order) -> Dict[str, Any]:
        """
        Execute a trailing stop order
        """
        if not order.trailing_percent:
            return {
                'status': 'REJECTED',
                'reason': 'Trailing percent not specified',
                'order_id': order.order_id
            }
        
        current_price = await self._get_current_price(order.symbol)
        
        # Calculate trailing stop price based on direction
        if order.side == 'BUY':
            # For sell orders with trailing stop, we trail below market
            trail_price = current_price * (1 - order.trailing_percent)
        else:  # SELL
            # For buy orders with trailing stop, we trail above market
            trail_price = current_price * (1 + order.trailing_percent)
        
        # Check if trailing stop is triggered
        if (order.side == 'BUY' and current_price <= trail_price) or \
           (order.side == 'SELL' and current_price >= trail_price):
            
            # Execute market order
            market_order = Order(
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                price=current_price,
                order_type='MARKET',
                user_id=order.user_id,
                strategy_id=order.strategy_id
            )
            
            return await self._execute_market_order(market_order)
        else:
            # Trailing stop not triggered yet
            return {
                'status': 'PENDING',
                'order_id': order.order_id,
                'filled_quantity': 0,
                'average_fill_price': 0.0,
                'message': f'Trailing stop not triggered. Current: {current_price}, Trail: {trail_price}'
            }
    
    async def execute_algorithmic_order(self, order: Order, algo_type: str) -> Dict[str, Any]:
        """
        Execute an algorithmic order using specified algorithm
        """
        if algo_type not in self.algorithms:
            return {
                'status': 'REJECTED',
                'reason': f'Unknown algorithm: {algo_type}',
                'order_id': order.order_id
            }
        
        # Execute the specific algorithm
        return await self.algorithms[algo_type](order)
    
    async def _execute_twap(self, order: Order) -> Dict[str, Any]:
        """
        Time Weighted Average Price execution algorithm
        """
        # Split the order into smaller chunks over time
        num_intervals = 10  # Execute over 10 intervals
        interval_duration = 30  # seconds between intervals
        chunk_size = order.quantity // num_intervals
        remaining_quantity = order.quantity
        
        fills = []
        total_cost = 0
        
        for i in range(num_intervals):
            if remaining_quantity <= 0:
                break
                
            # Calculate current chunk size
            current_chunk = min(chunk_size, remaining_quantity)
            if i == num_intervals - 1:  # Last interval gets remainder
                current_chunk = remaining_quantity
            
            # Get current price
            current_price = await self._get_current_price(order.symbol)
            
            # Execute chunk
            chunk_fill = Fill(
                order_id=order.order_id,
                symbol=order.symbol,
                side=order.side,
                quantity=current_chunk,
                price=current_price,
                timestamp=datetime.now()
            )
            
            fills.append(chunk_fill)
            total_cost += current_chunk * current_price
            remaining_quantity -= current_chunk
            
            # Wait for next interval (unless this is the last one)
            if i < num_intervals - 1:
                await asyncio.sleep(interval_duration)
        
        # Calculate average fill price
        avg_price = total_cost / order.quantity if order.quantity > 0 else 0
        
        # Update order
        order.filled_quantity = order.quantity
        order.average_fill_price = avg_price
        order.status = 'FILLED'
        
        # Add all fills to history
        self.fills.extend(fills)
        
        return {
            'status': 'FILLED',
            'order_id': order.order_id,
            'filled_quantity': order.quantity,
            'average_fill_price': avg_price,
            'num_chunks': len(fills),
            'execution_time': (datetime.now() - order.timestamp).total_seconds()
        }
    
    async def _execute_vwap(self, order: Order) -> Dict[str, Any]:
        """
        Volume Weighted Average Price execution algorithm
        """
        # For simplicity, this is similar to TWAP but would use volume data in practice
        # In a real implementation, this would use historical volume patterns
        return await self._execute_twap(order)
    
    async def _execute_participate(self, order: Order) -> Dict[str, Any]:
        """
        Participate in market algorithm - matches market participation rate
        """
        # This algorithm participates in market volume at a specified rate
        # For now, implement as a modified TWAP
        return await self._execute_twap(order)
    
    async def _execute_midpoint(self, order: Order) -> Dict[str, Any]:
        """
        Midpoint execution algorithm - executes at midpoint of bid/ask
        """
        # In a real implementation, this would get bid/ask data
        # For now, simulate with slight improvement over market price
        market_price = await self._get_current_price(order.symbol)
        
        # Assume midpoint is slightly better than market price
        midpoint_price = market_price * 0.999 if order.side == 'BUY' else market_price * 1.001
        
        fill = Fill(
            order_id=order.order_id,
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=midpoint_price,
            timestamp=datetime.now()
        )
        
        self.fills.append(fill)
        
        # Update order status
        order.filled_quantity = order.quantity
        order.average_fill_price = midpoint_price
        order.status = 'FILLED'
        
        # Calculate fees
        fees = self._calculate_fees(order.quantity, midpoint_price)
        fill.fees = fees
        
        return {
            'status': 'FILLED',
            'order_id': order.order_id,
            'filled_quantity': order.quantity,
            'average_fill_price': midpoint_price,
            'fees': fees,
            'execution_time': (datetime.now() - order.timestamp).total_seconds()
        }
    
    async def _get_current_price(self, symbol: str) -> float:
        """
        Get current market price for a symbol (simulated)
        """
        # In a real implementation, this would fetch from market data feed
        # Fetch live price from TrueData API
        from app.services.true_data_service import true_data_service
        live_price = await true_data_service.get_quote(symbol, exchange)
        if live_price and 'last_price' in live_price:
            return live_price['last_price']
        
        # If TrueData API fails, return None to indicate no price available
        return None
    
    def _calculate_slippage(self, quantity: int, price: float, side: str) -> float:
        """
        Calculate slippage based on order size and market conditions
        """
        # Simple slippage model - increases with order size
        order_value = quantity * price
        base_slippage = 0.0005  # 0.05% base slippage
        
        # Scale with order size (larger orders have more slippage)
        size_factor = min(order_value / 1000000, 1.0)  # Cap at 100% of base slippage for very large orders
        
        # Directional slippage (buy orders typically have worse slippage)
        direction_factor = 1.2 if side == 'BUY' else 1.0
        
        return base_slippage * size_factor * direction_factor
    
    def _calculate_fees(self, quantity: int, price: float) -> float:
        """
        Calculate transaction fees
        """
        # Simple fee model: 0.01% of transaction value
        transaction_value = quantity * price
        return transaction_value * 0.0001  # 0.01% fee
    
    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """
        Cancel an outstanding order
        """
        if order_id not in self.orders:
            return {
                'status': 'ERROR',
                'reason': f'Order {order_id} not found'
            }
        
        order = self.orders[order_id]
        if order.status in ['FILLED', 'CANCELLED']:
            return {
                'status': 'ERROR',
                'reason': f'Order {order_id} already {order.status}'
            }
        
        # Update order status
        order.status = 'CANCELLED'
        
        return {
            'status': 'CANCELLED',
            'order_id': order_id,
            'cancelled_at': datetime.now()
        }
    
    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """
        Get status of an order
        """
        if order_id not in self.orders:
            return {
                'status': 'ERROR',
                'reason': f'Order {order_id} not found'
            }
        
        order = self.orders[order_id]
        return {
            'order_id': order_id,
            'status': order.status,
            'symbol': order.symbol,
            'side': order.side,
            'quantity': order.quantity,
            'filled_quantity': order.filled_quantity,
            'remaining_quantity': order.quantity - order.filled_quantity,
            'price': order.price,
            'average_fill_price': order.average_fill_price,
            'timestamp': order.timestamp
        }
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """
        Get execution performance statistics
        """
        if not self.fills:
            return self.execution_stats
        
        # Calculate average execution time
        exec_times = [(f.timestamp - self.orders[f.order_id].timestamp).total_seconds() 
                     for f in self.fills if f.order_id in self.orders]
        
        if exec_times:
            self.execution_stats['avg_execution_time'] = sum(exec_times) / len(exec_times)
        
        # Calculate average slippage
        if self.execution_stats['slippage_metrics']:
            avg_slippage = sum(self.execution_stats['slippage_metrics']) / len(self.execution_stats['slippage_metrics'])
            self.execution_stats['avg_slippage'] = avg_slippage
        
        return self.execution_stats


# Execution algorithms for different market conditions
class ExecutionAlgorithms:
    """
    Collection of execution algorithms for different market conditions
    """
    
    @staticmethod
    def adaptive_execution(order: Order, market_conditions: Dict) -> Order:
        """
        Adaptive execution that adjusts based on market conditions
        """
        # Adjust order parameters based on volatility, liquidity, etc.
        volatility = market_conditions.get('volatility', 0.2)
        
        if volatility > 0.3:  # High volatility
            # Use more conservative execution
            order.time_in_force = 'IOC'  # Immediate or cancel
        elif volatility < 0.1:  # Low volatility
            # Can use more aggressive execution
            order.time_in_force = 'GTC'  # Good till cancelled
        
        return order
    
    @staticmethod
    def dark_pool_execution(order: Order) -> Order:
        """
        Execute order through dark pool if beneficial
        """
        # In a real implementation, this would route to dark pools
        # For now, just return the order as-is
        return order