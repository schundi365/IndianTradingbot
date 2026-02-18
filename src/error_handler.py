"""
Comprehensive error handling for Indian Market Broker Integration

This module provides centralized error handling, logging, and retry logic
for all broker operations.
"""

import logging
import time
from typing import Optional, Callable, Any, Dict
from functools import wraps
from datetime import datetime


class BrokerError(Exception):
    """Base exception for broker-related errors"""
    def __init__(self, message: str, error_code: Optional[str] = None, context: Optional[Dict] = None):
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        super().__init__(self.message)


class AuthenticationError(BrokerError):
    """Authentication-related errors"""
    pass


class ConnectionError(BrokerError):
    """Connection-related errors"""
    pass


class DataError(BrokerError):
    """Data fetching and processing errors"""
    pass


class OrderError(BrokerError):
    """Order placement and management errors"""
    pass


class MarketError(BrokerError):
    """Market status errors (closed, halt, circuit breaker)"""
    pass


class ValidationError(BrokerError):
    """Parameter validation errors"""
    pass


class ErrorHandler:
    """Centralized error handling and logging"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.error_counts = {}
        
    def log_error(self, error: Exception, context: Optional[Dict] = None):
        """
        Log error with full context
        
        Args:
            error: The exception that occurred
            context: Additional context information
        """
        error_type = type(error).__name__
        error_msg = str(error)
        
        # Track error counts
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        self.error_counts[error_type] += 1
        
        # Build log message
        log_parts = [f"Error: {error_type} - {error_msg}"]
        
        if isinstance(error, BrokerError):
            if error.error_code:
                log_parts.append(f"Code: {error.error_code}")
            if error.context:
                log_parts.append(f"Context: {error.context}")
        
        if context:
            log_parts.append(f"Additional Context: {context}")
        
        log_message = " | ".join(log_parts)
        
        # Log with appropriate level
        if isinstance(error, (AuthenticationError, MarketError)):
            self.logger.error(log_message)
        elif isinstance(error, (ConnectionError, DataError)):
            self.logger.warning(log_message)
        else:
            self.logger.error(log_message, exc_info=True)
    
    def handle_authentication_error(self, error: Exception, token_file: str = "kite_token.json"):
        """
        Handle authentication errors with clear instructions
        
        Args:
            error: The authentication error
            token_file: Path to token file
        """
        self.logger.error("=" * 80)
        self.logger.error("AUTHENTICATION FAILED")
        self.logger.error("=" * 80)
        self.logger.error(f"Error: {error}")
        self.logger.error("")
        self.logger.error("To fix this issue:")
        self.logger.error(f"1. Run: python kite_login.py")
        self.logger.error(f"2. Complete the authentication flow in your browser")
        self.logger.error(f"3. Verify {token_file} is created with today's date")
        self.logger.error(f"4. Restart the trading bot")
        self.logger.error("")
        self.logger.error("Note: Kite Connect tokens expire daily and must be refreshed")
        self.logger.error("=" * 80)
        
        raise AuthenticationError(
            "Authentication failed. Please run kite_login.py to re-authenticate.",
            error_code="AUTH_FAILED",
            context={"token_file": token_file, "original_error": str(error)}
        )
    
    def handle_connection_error(self, error: Exception, operation: str, retry_count: int = 0):
        """
        Handle connection errors with retry logic
        
        Args:
            error: The connection error
            operation: The operation that failed
            retry_count: Current retry attempt number
        """
        self.log_error(error, {"operation": operation, "retry_count": retry_count})
        
        if retry_count > 0:
            self.logger.info(f"Retrying {operation} (attempt {retry_count + 1})...")
        
        raise ConnectionError(
            f"Connection failed during {operation}",
            error_code="CONN_FAILED",
            context={"operation": operation, "retry_count": retry_count, "original_error": str(error)}
        )
    
    def handle_data_error(self, error: Exception, symbol: str, timeframe: str, operation: str):
        """
        Handle data fetching errors
        
        Args:
            error: The data error
            symbol: Instrument symbol
            timeframe: Timeframe requested
            operation: The operation that failed
        """
        self.log_error(error, {
            "symbol": symbol,
            "timeframe": timeframe,
            "operation": operation
        })
        
        raise DataError(
            f"Data error for {symbol} ({timeframe}): {error}",
            error_code="DATA_FAILED",
            context={
                "symbol": symbol,
                "timeframe": timeframe,
                "operation": operation,
                "original_error": str(error)
            }
        )
    
    def handle_order_error(self, error: Exception, order_params: Dict):
        """
        Handle order placement/modification errors with descriptive messages
        
        Args:
            error: The order error
            order_params: Order parameters that caused the error
        """
        error_msg = str(error).lower()
        
        # Provide specific guidance based on error type
        if "margin" in error_msg or "insufficient" in error_msg:
            guidance = "Insufficient margin. Reduce position size or add funds to your account."
        elif "invalid" in error_msg and "symbol" in error_msg:
            guidance = f"Invalid symbol: {order_params.get('symbol')}. Check instrument name and exchange."
        elif "invalid" in error_msg and ("price" in error_msg or "quantity" in error_msg):
            guidance = "Invalid order parameters. Check price tick size and quantity lot size."
        elif "rejected" in error_msg:
            guidance = "Order rejected by broker. Check order parameters and market conditions."
        elif "limit" in error_msg:
            guidance = "Position or order limit exceeded. Close existing positions or reduce order count."
        else:
            guidance = "Order failed. Check broker API status and order parameters."
        
        self.logger.error(f"Order Error: {error}")
        self.logger.error(f"Order Parameters: {order_params}")
        self.logger.error(f"Guidance: {guidance}")
        
        raise OrderError(
            f"Order failed: {error}. {guidance}",
            error_code="ORDER_FAILED",
            context={"order_params": order_params, "guidance": guidance, "original_error": str(error)}
        )
    
    def handle_market_error(self, error: Exception, market_status: str):
        """
        Handle market status errors (closed, halt, circuit breaker)
        
        Args:
            error: The market error
            market_status: Current market status
        """
        status_messages = {
            "closed": "Market is closed. Trading will resume during market hours (9:15 AM - 3:30 PM IST).",
            "halt": "Trading is halted. Wait for market to resume normal operations.",
            "circuit_breaker": "Circuit breaker triggered. Trading is temporarily suspended.",
            "holiday": "Market is closed for holiday. Check NSE holiday calendar."
        }
        
        message = status_messages.get(market_status, f"Market error: {market_status}")
        
        self.logger.warning(f"Market Status: {market_status}")
        self.logger.warning(message)
        
        raise MarketError(
            message,
            error_code="MARKET_ERROR",
            context={"market_status": market_status, "original_error": str(error)}
        )
    
    def handle_validation_error(self, param_name: str, param_value: Any, expected: str):
        """
        Handle parameter validation errors
        
        Args:
            param_name: Name of invalid parameter
            param_value: Invalid value
            expected: Expected format/value
        """
        message = f"Invalid {param_name}: {param_value}. Expected: {expected}"
        self.logger.error(message)
        
        raise ValidationError(
            message,
            error_code="VALIDATION_FAILED",
            context={"param_name": param_name, "param_value": param_value, "expected": expected}
        )
    
    def retry_with_backoff(
        self,
        func: Callable,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0,
        exceptions: tuple = (Exception,)
    ) -> Any:
        """
        Execute function with exponential backoff retry logic
        
        Args:
            func: Function to execute
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            backoff_factor: Multiplier for delay on each retry
            exceptions: Tuple of exceptions to catch and retry
            
        Returns:
            Result of function execution
            
        Raises:
            Last exception if all retries fail
        """
        delay = initial_delay
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return func()
            except exceptions as e:
                last_exception = e
                
                if attempt < max_retries:
                    # Check if it's a rate limit error
                    if "rate limit" in str(e).lower() or "429" in str(e):
                        self.logger.warning(f"Rate limit hit. Waiting {delay}s before retry...")
                    else:
                        self.logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                    
                    time.sleep(delay)
                    delay *= backoff_factor
                else:
                    self.logger.error(f"All {max_retries} retry attempts failed")
                    self.log_error(e, {"attempts": max_retries + 1})
        
        raise last_exception
    
    def get_error_summary(self) -> Dict[str, int]:
        """Get summary of error counts"""
        return self.error_counts.copy()
    
    def reset_error_counts(self):
        """Reset error count tracking"""
        self.error_counts.clear()


def handle_errors(error_handler: ErrorHandler, operation: str):
    """
    Decorator for automatic error handling
    
    Args:
        error_handler: ErrorHandler instance
        operation: Name of the operation being performed
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except AuthenticationError:
                raise  # Re-raise authentication errors
            except ConnectionError:
                raise  # Re-raise connection errors
            except Exception as e:
                error_handler.log_error(e, {"operation": operation, "function": func.__name__})
                raise
        return wrapper
    return decorator
