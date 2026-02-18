"""
Trading Decision Logger

This module provides comprehensive logging for all trading decisions including
signals, order placements, position updates, and exits with P&L.

Validates: Requirement 12.5
"""

import logging
from typing import Dict, Optional, Any
from datetime import datetime
import json
from pathlib import Path


class TradingDecisionLogger:
    """
    Logger for all trading decisions and actions.
    
    This class logs:
    - Signal generation with timestamp and reasoning
    - Order placements with all parameters
    - Position updates (trailing stops, modifications)
    - Position exits with P&L calculations
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None, log_file: Optional[str] = None):
        """
        Initialize trading decision logger.
        
        Args:
            logger: Logger instance (creates new one if None)
            log_file: Optional separate file for trading decisions
        """
        self.logger = logger or logging.getLogger(__name__)
        self.log_file = log_file
        
        # Setup separate file handler if specified
        if log_file:
            self._setup_file_handler(log_file)
        
        # Track decision counts
        self.decision_counts = {
            'signals': 0,
            'orders': 0,
            'position_updates': 0,
            'exits': 0
        }
    
    def _setup_file_handler(self, log_file: str):
        """Setup separate file handler for trading decisions"""
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def log_signal(
        self,
        symbol: str,
        signal_type: str,
        direction: int,
        reasoning: Dict[str, Any],
        price: float,
        indicators: Optional[Dict[str, float]] = None
    ):
        """
        Log signal generation with timestamp and reasoning.
        
        Validates: Requirement 12.5
        
        Args:
            symbol: Instrument symbol
            signal_type: Type of signal (e.g., "MA_CROSSOVER", "MOMENTUM", "PULLBACK")
            direction: Signal direction (1 for buy, -1 for sell, 0 for no signal)
            reasoning: Dictionary explaining why signal was generated
            price: Current price when signal generated
            indicators: Optional dictionary of indicator values
        """
        self.decision_counts['signals'] += 1
        
        signal_str = "BUY" if direction == 1 else "SELL" if direction == -1 else "NO_SIGNAL"
        
        log_parts = [
            f"SIGNAL | {symbol} | {signal_str} | {signal_type}",
            f"Price: {price:.2f}",
            f"Reasoning: {json.dumps(reasoning)}"
        ]
        
        if indicators:
            log_parts.append(f"Indicators: {json.dumps(indicators)}")
        
        log_message = " | ".join(log_parts)
        self.logger.info(log_message)
    
    def log_order_placement(
        self,
        symbol: str,
        direction: int,
        quantity: float,
        order_type: str,
        price: Optional[float] = None,
        trigger_price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        order_id: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """
        Log order placement with all parameters.
        
        Validates: Requirement 12.5
        
        Args:
            symbol: Instrument symbol
            direction: Trade direction (1 for buy, -1 for sell)
            quantity: Order quantity
            order_type: Order type (MARKET, LIMIT, SL, SL-M)
            price: Limit price (if applicable)
            trigger_price: Trigger price (if applicable)
            stop_loss: Stop loss price
            take_profit: Take profit price
            order_id: Order ID returned by broker
            success: Whether order placement succeeded
            error_message: Error message if order failed
        """
        self.decision_counts['orders'] += 1
        
        direction_str = "BUY" if direction == 1 else "SELL"
        status = "SUCCESS" if success else "FAILED"
        
        log_parts = [
            f"ORDER | {symbol} | {direction_str} | {order_type} | {status}",
            f"Qty: {quantity}"
        ]
        
        if price is not None:
            log_parts.append(f"Price: {price:.2f}")
        
        if trigger_price is not None:
            log_parts.append(f"Trigger: {trigger_price:.2f}")
        
        if stop_loss is not None:
            log_parts.append(f"SL: {stop_loss:.2f}")
        
        if take_profit is not None:
            log_parts.append(f"TP: {take_profit:.2f}")
        
        if order_id:
            log_parts.append(f"OrderID: {order_id}")
        
        if error_message:
            log_parts.append(f"Error: {error_message}")
        
        log_message = " | ".join(log_parts)
        
        if success:
            self.logger.info(log_message)
        else:
            self.logger.error(log_message)
    
    def log_position_update(
        self,
        symbol: str,
        update_type: str,
        old_value: Optional[float] = None,
        new_value: Optional[float] = None,
        current_price: Optional[float] = None,
        pnl: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log position updates (trailing stops, modifications, etc.).
        
        Validates: Requirement 12.5
        
        Args:
            symbol: Instrument symbol
            update_type: Type of update (e.g., "TRAILING_STOP", "BREAK_EVEN", "PARTIAL_CLOSE")
            old_value: Previous value (e.g., old stop loss)
            new_value: New value (e.g., new stop loss)
            current_price: Current market price
            pnl: Current P&L
            details: Additional details about the update
        """
        self.decision_counts['position_updates'] += 1
        
        log_parts = [
            f"POSITION_UPDATE | {symbol} | {update_type}"
        ]
        
        if old_value is not None and new_value is not None:
            log_parts.append(f"Changed: {old_value:.2f} -> {new_value:.2f}")
        elif new_value is not None:
            log_parts.append(f"Value: {new_value:.2f}")
        
        if current_price is not None:
            log_parts.append(f"Price: {current_price:.2f}")
        
        if pnl is not None:
            log_parts.append(f"P&L: {pnl:.2f}")
        
        if details:
            log_parts.append(f"Details: {json.dumps(details)}")
        
        log_message = " | ".join(log_parts)
        self.logger.info(log_message)
    
    def log_position_exit(
        self,
        symbol: str,
        direction: int,
        quantity: float,
        entry_price: float,
        exit_price: float,
        pnl: float,
        pnl_percent: float,
        exit_reason: str,
        hold_time: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log position exit with P&L.
        
        Validates: Requirement 12.5
        
        Args:
            symbol: Instrument symbol
            direction: Position direction (1 for long, -1 for short)
            quantity: Position quantity
            entry_price: Entry price
            exit_price: Exit price
            pnl: Profit/Loss in currency
            pnl_percent: Profit/Loss percentage
            exit_reason: Reason for exit (e.g., "STOP_LOSS", "TAKE_PROFIT", "TIME_EXIT")
            hold_time: How long position was held
            details: Additional details about the exit
        """
        self.decision_counts['exits'] += 1
        
        direction_str = "LONG" if direction == 1 else "SHORT"
        pnl_sign = "+" if pnl >= 0 else ""
        
        log_parts = [
            f"EXIT | {symbol} | {direction_str} | {exit_reason}",
            f"Qty: {quantity}",
            f"Entry: {entry_price:.2f}",
            f"Exit: {exit_price:.2f}",
            f"P&L: {pnl_sign}{pnl:.2f} ({pnl_sign}{pnl_percent:.2f}%)"
        ]
        
        if hold_time:
            log_parts.append(f"Hold: {hold_time}")
        
        if details:
            log_parts.append(f"Details: {json.dumps(details)}")
        
        log_message = " | ".join(log_parts)
        
        # Use different log level based on P&L
        if pnl >= 0:
            self.logger.info(log_message)
        else:
            self.logger.warning(log_message)
    
    def log_market_status(self, status: str, message: str):
        """
        Log market status changes.
        
        Args:
            status: Market status (e.g., "OPEN", "CLOSED", "HALT")
            message: Status message
        """
        self.logger.info(f"MARKET_STATUS | {status} | {message}")
    
    def log_bot_action(self, action: str, details: Optional[Dict[str, Any]] = None):
        """
        Log bot-level actions (start, stop, error recovery, etc.).
        
        Args:
            action: Action type (e.g., "START", "STOP", "ERROR_RECOVERY")
            details: Additional details
        """
        log_parts = [f"BOT_ACTION | {action}"]
        
        if details:
            log_parts.append(f"Details: {json.dumps(details)}")
        
        log_message = " | ".join(log_parts)
        self.logger.info(log_message)
    
    def get_decision_summary(self) -> Dict[str, int]:
        """
        Get summary of decision counts.
        
        Returns:
            Dictionary with counts of each decision type
        """
        return self.decision_counts.copy()
    
    def reset_decision_counts(self):
        """Reset decision count tracking"""
        for key in self.decision_counts:
            self.decision_counts[key] = 0
    
    def log_daily_summary(
        self,
        total_trades: int,
        winning_trades: int,
        losing_trades: int,
        total_pnl: float,
        win_rate: float,
        largest_win: float,
        largest_loss: float
    ):
        """
        Log daily trading summary.
        
        Args:
            total_trades: Total number of trades
            winning_trades: Number of winning trades
            losing_trades: Number of losing trades
            total_pnl: Total P&L for the day
            win_rate: Win rate percentage
            largest_win: Largest winning trade
            largest_loss: Largest losing trade
        """
        self.logger.info("=" * 80)
        self.logger.info("DAILY SUMMARY")
        self.logger.info("=" * 80)
        self.logger.info(f"Total Trades: {total_trades}")
        self.logger.info(f"Winning Trades: {winning_trades}")
        self.logger.info(f"Losing Trades: {losing_trades}")
        self.logger.info(f"Win Rate: {win_rate:.2f}%")
        self.logger.info(f"Total P&L: {total_pnl:+.2f}")
        self.logger.info(f"Largest Win: +{largest_win:.2f}")
        self.logger.info(f"Largest Loss: {largest_loss:.2f}")
        self.logger.info("=" * 80)
