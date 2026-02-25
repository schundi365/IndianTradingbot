"""
Bot Controller Service
Manages bot lifecycle and monitoring
"""

import logging
import threading
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.indian_trading_bot import IndianTradingBot
from src.adapters.broker_adapter import BrokerAdapter
from .activity_logger import ActivityLogger

logger = logging.getLogger(__name__)


class BotController:
    """Controls bot lifecycle and provides monitoring"""
    
    def __init__(self):
        self.bot = None
        self.bot_thread = None
        self.is_running = False
        self.start_time = None
        self.config = None
        self.broker_adapter = None
        self.stop_requested = False
        self.activity_logger = ActivityLogger()
    
    def start(self, config: Dict, broker_adapter: BrokerAdapter) -> tuple[bool, str]:
        """
        Start the trading bot
        
        Args:
            config: Bot configuration dictionary
            broker_adapter: Connected broker adapter
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if self.is_running:
                return False, "Bot is already running"
            
            if not broker_adapter or not broker_adapter.is_connected():
                return False, "Broker not connected"
            
            logger.info("Starting trading bot...")
            
            # Store config and adapter
            self.config = config
            self.broker_adapter = broker_adapter
            
            # Create bot instance
            self.bot = IndianTradingBot(config, broker_adapter)
            
            # Pass activity logger to bot
            if hasattr(self.bot, 'set_activity_logger'):
                self.bot.set_activity_logger(self.activity_logger)
            
            # Log bot startup configuration
            self.activity_logger.log_bot_start(config)
            
            # Connect bot
            if not self.bot.connect():
                return False, "Failed to connect bot to broker"
            
            # Validate instruments
            if not self.bot.validate_instruments():
                return False, "Instrument validation failed"
            
            # Start bot in separate thread
            self.stop_requested = False
            self.bot_thread = threading.Thread(target=self._run_bot, daemon=True)
            self.bot_thread.start()
            
            self.is_running = True
            self.start_time = datetime.now()
            
            # Log successful start
            symbols = config.get('symbols', [])
            self.activity_logger.log_analysis(
                symbol=None,
                message=f"Bot started successfully - Monitoring {len(symbols)} instruments",
                data={'symbols': symbols}
            )
            
            logger.info("Trading bot started successfully")
            return True, "Bot started successfully"
            
        except Exception as e:
            error_msg = f"Error starting bot: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
    
    def _run_bot(self):
        """Run bot in thread"""
        try:
            logger.info("Bot thread started")
            self.bot.run()
        except Exception as e:
            logger.error(f"Bot thread error: {e}", exc_info=True)
        finally:
            self.is_running = False
            logger.info("Bot thread stopped")

    def stop(self) -> tuple[bool, str]:
        """
        Stop the trading bot
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if not self.is_running:
                return False, "Bot is not running"
            
            logger.info("Stopping trading bot...")
            
            # Log bot stop
            self.activity_logger.log_analysis(
                symbol=None,
                message="Trading bot stopping...",
                data={}
            )
            
            # Request stop
            self.stop_requested = True
            
            # Disconnect bot
            if self.bot:
                self.bot.disconnect()
            
            # Wait for thread to finish (with timeout)
            if self.bot_thread and self.bot_thread.is_alive():
                self.bot_thread.join(timeout=5.0)
            
            self.is_running = False
            self.bot = None
            self.bot_thread = None
            self.start_time = None
            
            logger.info("Trading bot stopped")
            return True, "Bot stopped successfully"
            
        except Exception as e:
            error_msg = f"Error stopping bot: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
    
    def restart(self) -> tuple[bool, str]:
        """
        Restart the trading bot
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Stop if running
            if self.is_running:
                success, msg = self.stop()
                if not success:
                    return False, f"Failed to stop bot: {msg}"
            
            # Start with saved config
            if not self.config or not self.broker_adapter:
                return False, "No configuration available for restart"
            
            return self.start(self.config, self.broker_adapter)
            
        except Exception as e:
            error_msg = f"Error restarting bot: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
    
    def get_status(self) -> Dict:
        """
        Get bot status
        
        Returns:
            Dictionary with bot status information
        """
        status = {
            'running': self.is_running,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'uptime_seconds': None,
            'config_loaded': self.config is not None,
            'broker_connected': self.broker_adapter is not None and self.broker_adapter.is_connected() if self.broker_adapter else False
        }
        
        if self.is_running and self.start_time:
            uptime = datetime.now() - self.start_time
            status['uptime_seconds'] = int(uptime.total_seconds())
        
        return status
    
    def get_account_info(self) -> Optional[Dict]:
        """
        Get account information from broker
        
        Returns:
            Account info dictionary or None
        """
        try:
            if not self.broker_adapter or not self.broker_adapter.is_connected():
                return None
            
            account_info = self.broker_adapter.get_account_info()
            return account_info
            
        except Exception as e:
            logger.error(f"Error getting account info: {e}", exc_info=True)
            return None
    
    def get_positions(self) -> List[Dict]:
        """
        Get current positions
        
        Returns:
            List of position dictionaries
        """
        try:
            if not self.broker_adapter or not self.broker_adapter.is_connected():
                return []
            
            positions = self.broker_adapter.get_positions()
            return positions if positions else []
            
        except Exception as e:
            logger.error(f"Error getting positions: {e}", exc_info=True)
            return []
    
    def get_trades(self, from_date: str = None, to_date: str = None) -> List[Dict]:
        """
        Get trade history
        
        Args:
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            
        Returns:
            List of trade dictionaries
        """
        try:
            if not self.broker_adapter or not self.broker_adapter.is_connected():
                return []
            
            # Get orders (trades)
            orders = self.broker_adapter.get_orders()
            
            if not orders:
                return []
            
            # Filter by date if provided
            if from_date or to_date:
                filtered_orders = []
                for order in orders:
                    order_date = order.get('order_timestamp', '')
                    if from_date and order_date < from_date:
                        continue
                    if to_date and order_date > to_date:
                        continue
                    filtered_orders.append(order)
                return filtered_orders
            
            return orders
            
        except Exception as e:
            logger.error(f"Error getting trades: {e}", exc_info=True)
            return []
    
    def close_position(self, symbol: str) -> tuple[bool, str]:
        """
        Close a specific position
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if not self.broker_adapter or not self.broker_adapter.is_connected():
                return False, "Broker not connected"
            
            # Get current position
            positions = self.broker_adapter.get_positions(symbol)
            if not positions:
                return False, f"No position found for {symbol}"
            
            position = positions[0]
            quantity = abs(position.get('quantity', 0))
            
            if quantity == 0:
                return False, f"No open position for {symbol}"
            
            # Determine transaction type (opposite of current position)
            current_side = position.get('side', '')
            transaction_type = 'SELL' if current_side == 'BUY' else 'BUY'
            
            # Place market order to close
            order = self.broker_adapter.place_order(
                symbol=symbol,
                quantity=quantity,
                order_type='MARKET',
                transaction_type=transaction_type,
                product='MIS'
            )
            
            if order:
                logger.info(f"Closed position for {symbol}")
                return True, f"Position closed for {symbol}"
            else:
                return False, f"Failed to close position for {symbol}"
                
        except Exception as e:
            error_msg = f"Error closing position: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
    
    def get_bot_config(self) -> Optional[Dict]:
        """
        Get current bot configuration
        
        Returns:
            Configuration dictionary or None
        """
        return self.config
    
    def is_bot_running(self) -> bool:
        """
        Check if bot is running
        
        Returns:
            True if running, False otherwise
        """
        return self.is_running
    
    def get_activities(self, limit: int = 100, activity_type: str = None) -> List[Dict]:
        """
        Get recent bot activities
        
        Args:
            limit: Maximum number of activities to return
            activity_type: Filter by activity type (optional)
            
        Returns:
            List of activity dictionaries
        """
        return self.activity_logger.get_recent(limit=limit, activity_type=activity_type)
    
    def clear_activities(self):
        """Clear all bot activities"""
        self.activity_logger.clear()
