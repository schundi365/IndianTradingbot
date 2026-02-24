"""
Paper Trading Module
Simulates order execution without calling broker API
Validates: Requirements 15.1, 15.2
"""

import logging
from datetime import datetime
from typing import Dict, Optional, List
import uuid


class PaperTradingEngine:
    """
    Simulates order execution for paper trading mode.
    Tracks simulated positions and calculates P&L without real broker API calls.
    """
    
    def __init__(self, initial_balance: float = 100000.0):
        """
        Initialize paper trading engine.
        
        Args:
            initial_balance: Starting balance for paper trading account
        """
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.equity = initial_balance
        self.positions = {}  # symbol -> position dict
        self.orders = {}  # order_id -> order dict
        self.order_counter = 0
        self.trades = []  # List of completed trades
        
        logging.info(f"Paper Trading Engine initialized with balance: Rs.{initial_balance:,.2f}")
    
    def generate_order_id(self) -> str:
        """
        Generate a simulated order ID.
        
        Returns:
            Unique order ID string
        """
        self.order_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"PAPER_{timestamp}_{self.order_counter:06d}"
    
    def place_order(
        self,
        symbol: str,
        direction: int,
        quantity: float,
        order_type: str,
        price: Optional[float] = None,
        trigger_price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        product_type: str = "MIS",
        current_price: float = None
    ) -> Optional[str]:
        """
        Simulate order placement.
        
        Args:
            symbol: Instrument symbol
            direction: 1 for buy, -1 for sell
            quantity: Order quantity
            order_type: "MARKET", "LIMIT", "SL", "SL-M"
            price: Limit price (for LIMIT orders)
            trigger_price: Trigger price (for SL orders)
            stop_loss: Stop loss price
            take_profit: Take profit price
            product_type: "MIS" or "NRML"
            current_price: Current market price for execution
        
        Returns:
            Simulated order ID if successful, None otherwise
        """
        # Generate order ID
        order_id = self.generate_order_id()
        
        # For market orders, execute immediately at current price
        if order_type == "MARKET" and current_price is not None:
            execution_price = current_price
            
            # Check if we have sufficient margin
            required_margin = execution_price * quantity
            if required_margin > self.balance:
                logging.warning(
                    f"🧪 PAPER TRADE REJECTED: Insufficient margin. "
                    f"Required: Rs.{required_margin:,.2f}, Available: Rs.{self.balance:,.2f}"
                )
                return None
            
            # Create position
            position_key = f"{symbol}_{order_id}"
            self.positions[position_key] = {
                'symbol': symbol,
                'direction': direction,
                'quantity': quantity,
                'entry_price': execution_price,
                'current_price': execution_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'order_id': order_id,
                'entry_time': datetime.now(),
                'pnl': 0.0,
                'pnl_percent': 0.0
            }
            
            # Update balance (deduct margin)
            self.balance -= required_margin
            
            # Log the simulated order (Requirement 15.2)
            logging.info("="*80)
            logging.info("🧪 PAPER TRADE EXECUTED")
            logging.info(f"Order ID: {order_id}")
            logging.info(f"Symbol: {symbol}")
            logging.info(f"Direction: {'BUY' if direction == 1 else 'SELL'}")
            logging.info(f"Quantity: {quantity}")
            logging.info(f"Entry Price: Rs.{execution_price:.2f}")
            logging.info(f"Order Type: {order_type}")
            logging.info(f"Product Type: {product_type}")
            if stop_loss:
                logging.info(f"Stop Loss: Rs.{stop_loss:.2f}")
            if take_profit:
                logging.info(f"Take Profit: Rs.{take_profit:.2f}")
            logging.info(f"Margin Used: Rs.{required_margin:,.2f}")
            logging.info(f"Remaining Balance: Rs.{self.balance:,.2f}")
            logging.info("="*80)
            
            return order_id
        
        # For other order types, store as pending order
        self.orders[order_id] = {
            'order_id': order_id,
            'symbol': symbol,
            'direction': direction,
            'quantity': quantity,
            'order_type': order_type,
            'price': price,
            'trigger_price': trigger_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'product_type': product_type,
            'status': 'PENDING',
            'created_time': datetime.now()
        }
        
        logging.info(f"🧪 PAPER ORDER PLACED: {order_id} - {order_type} {symbol}")
        return order_id
    
    def update_positions(self, symbol: str, current_price: float):
        """
        Update position prices and calculate P&L.
        
        Args:
            symbol: Instrument symbol
            current_price: Current market price
        """
        for position_key, position in self.positions.items():
            if position['symbol'] == symbol:
                position['current_price'] = current_price
                
                # Calculate P&L
                if position['direction'] == 1:  # Long position
                    pnl = (current_price - position['entry_price']) * position['quantity']
                else:  # Short position
                    pnl = (position['entry_price'] - current_price) * position['quantity']
                
                position['pnl'] = pnl
                position['pnl_percent'] = (pnl / (position['entry_price'] * position['quantity'])) * 100
                
                # Update equity
                self.equity = self.balance + sum(p['pnl'] for p in self.positions.values())
    
    def close_position(self, order_id: str, current_price: float) -> bool:
        """
        Close a simulated position.
        
        Args:
            order_id: Order ID of position to close
            current_price: Current market price for exit
        
        Returns:
            True if position closed successfully, False otherwise
        """
        # Find position by order_id
        position_key = None
        for key, position in self.positions.items():
            if position['order_id'] == order_id:
                position_key = key
                break
        
        if position_key is None:
            logging.warning(f"🧪 PAPER TRADE: Position not found for order {order_id}")
            return False
        
        position = self.positions[position_key]
        
        # Calculate final P&L
        if position['direction'] == 1:  # Long position
            pnl = (current_price - position['entry_price']) * position['quantity']
        else:  # Short position
            pnl = (position['entry_price'] - current_price) * position['quantity']
        
        pnl_percent = (pnl / (position['entry_price'] * position['quantity'])) * 100
        
        # Return margin to balance
        margin_released = position['entry_price'] * position['quantity']
        self.balance += margin_released + pnl
        self.equity = self.balance + sum(p['pnl'] for p in self.positions.values() if p['order_id'] != order_id)
        
        # Record trade
        trade = {
            'symbol': position['symbol'],
            'direction': position['direction'],
            'quantity': position['quantity'],
            'entry_price': position['entry_price'],
            'exit_price': current_price,
            'entry_time': position['entry_time'],
            'exit_time': datetime.now(),
            'pnl': pnl,
            'pnl_percent': pnl_percent
        }
        self.trades.append(trade)
        
        # Log the simulated exit (Requirement 15.2)
        logging.info("="*80)
        logging.info("🧪 PAPER TRADE CLOSED")
        logging.info(f"Order ID: {order_id}")
        logging.info(f"Symbol: {position['symbol']}")
        logging.info(f"Direction: {'BUY' if position['direction'] == 1 else 'SELL'}")
        logging.info(f"Quantity: {position['quantity']}")
        logging.info(f"Entry Price: Rs.{position['entry_price']:.2f}")
        logging.info(f"Exit Price: Rs.{current_price:.2f}")
        logging.info(f"P&L: Rs.{pnl:,.2f} ({pnl_percent:+.2f}%)")
        logging.info(f"New Balance: Rs.{self.balance:,.2f}")
        logging.info(f"New Equity: Rs.{self.equity:,.2f}")
        logging.info("="*80)
        
        # Remove position
        del self.positions[position_key]
        
        return True
    
    def get_positions(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        Get simulated positions.
        
        Args:
            symbol: Filter by symbol (optional)
        
        Returns:
            List of position dictionaries
        """
        positions = []
        for position in self.positions.values():
            if symbol is None or position['symbol'] == symbol:
                positions.append({
                    'symbol': position['symbol'],
                    'direction': position['direction'],
                    'quantity': position['quantity'],
                    'entry_price': position['entry_price'],
                    'current_price': position['current_price'],
                    'pnl': position['pnl'],
                    'pnl_percent': position['pnl_percent'],
                    'order_id': position['order_id']
                })
        return positions
    
    def get_account_info(self) -> Dict:
        """
        Get simulated account information.
        
        Returns:
            Dictionary with balance, equity, margin info
        """
        # Calculate used margin
        margin_used = sum(
            pos['entry_price'] * pos['quantity'] 
            for pos in self.positions.values()
        )
        
        return {
            'balance': self.balance,
            'equity': self.equity,
            'margin_available': self.balance,
            'margin_used': margin_used
        }
    
    def modify_order(
        self,
        order_id: str,
        quantity: Optional[float] = None,
        price: Optional[float] = None,
        trigger_price: Optional[float] = None
    ) -> bool:
        """
        Modify a simulated pending order.
        
        Args:
            order_id: Order ID to modify
            quantity: New quantity (optional)
            price: New price (optional)
            trigger_price: New trigger price (optional)
        
        Returns:
            True if modification successful, False otherwise
        """
        if order_id not in self.orders:
            logging.warning(f"🧪 PAPER TRADE: Order {order_id} not found")
            return False
        
        order = self.orders[order_id]
        
        if quantity is not None:
            order['quantity'] = quantity
        if price is not None:
            order['price'] = price
        if trigger_price is not None:
            order['trigger_price'] = trigger_price
        
        logging.info(f"🧪 PAPER ORDER MODIFIED: {order_id}")
        return True
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel a simulated pending order.
        
        Args:
            order_id: Order ID to cancel
        
        Returns:
            True if cancellation successful, False otherwise
        """
        if order_id not in self.orders:
            logging.warning(f"🧪 PAPER TRADE: Order {order_id} not found")
            return False
        
        del self.orders[order_id]
        logging.info(f"🧪 PAPER ORDER CANCELLED: {order_id}")
        return True
    
    def get_trade_statistics(self) -> Dict:
        """
        Get statistics for completed trades.
        
        Returns:
            Dictionary with trade statistics
        """
        if not self.trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'total_pnl': 0.0,
                'average_pnl': 0.0,
                'largest_win': 0.0,
                'largest_loss': 0.0
            }
        
        winning_trades = [t for t in self.trades if t['pnl'] > 0]
        losing_trades = [t for t in self.trades if t['pnl'] <= 0]
        
        total_pnl = sum(t['pnl'] for t in self.trades)
        
        return {
            'total_trades': len(self.trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': (len(winning_trades) / len(self.trades)) * 100 if self.trades else 0.0,
            'total_pnl': total_pnl,
            'average_pnl': total_pnl / len(self.trades) if self.trades else 0.0,
            'largest_win': max((t['pnl'] for t in winning_trades), default=0.0),
            'largest_loss': min((t['pnl'] for t in losing_trades), default=0.0),
            'return_percent': ((self.equity - self.initial_balance) / self.initial_balance) * 100
        }
    def get_orders(self) -> List[Dict]:
        """
        Get all simulated orders.
        
        Returns:
            List of order dictionaries
        """
        result = []
        # Add pending orders
        for order_id, order in self.orders.items():
            result.append({
                'order_id': order['order_id'],
                'symbol': order['symbol'],
                'status': order['status'],
                'direction': 'BUY' if order['direction'] == 1 else 'SELL',
                'quantity': order['quantity'],
                'filled_quantity': 0,
                'average_price': 0,
                'order_timestamp': order['created_time'].strftime("%Y-%m-%d %H:%M:%S")
            })
            
        # Add executed orders from positions
        for pos in self.positions.values():
            result.append({
                'order_id': pos['order_id'],
                'symbol': pos['symbol'],
                'status': 'COMPLETE',
                'direction': 'BUY' if pos['direction'] == 1 else 'SELL',
                'quantity': pos['quantity'],
                'filled_quantity': pos['quantity'],
                'average_price': pos['entry_price'],
                'order_timestamp': pos['entry_time'].strftime("%Y-%m-%d %H:%M:%S")
            })
            
        # Add completed trades (exit orders)
        for trade in self.trades:
            # We don't have order_ids for exits in trades list currently, 
            # but we can return them as completed orders
            result.append({
                'order_id': f"EXIT_{trade['entry_time'].strftime('%H%M%S')}",
                'symbol': trade['symbol'],
                'status': 'COMPLETE',
                'direction': 'SELL' if trade['direction'] == 1 else 'BUY',
                'quantity': trade['quantity'],
                'filled_quantity': trade['quantity'],
                'average_price': trade['exit_price'],
                'order_timestamp': trade['exit_time'].strftime("%Y-%m-%d %H:%M:%S")
            })
            
        return result
