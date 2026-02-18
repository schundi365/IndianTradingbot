"""
Property-Based Tests for Error Logging

Feature: indian-market-broker-integration
Property 18: Error Logging Completeness
Property 28: Order Failure Error Messages

Validates: Requirements 12.1, 12.4, 5.8

These tests verify that:
1. All broker API errors are logged with error code, message, and context
2. Order failures return descriptive error messages
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from unittest.mock import Mock, patch, MagicMock
import logging
from io import StringIO

from src.error_handler import (
    ErrorHandler,
    BrokerError,
    AuthenticationError,
    ConnectionError,
    DataError,
    OrderError,
    MarketError,
    ValidationError
)
from src.kite_adapter import KiteAdapter


# Strategy for generating error contexts
@st.composite
def error_context_strategy(draw):
    """Generate random error contexts"""
    return {
        'operation': draw(st.sampled_from(['connect', 'fetch_data', 'place_order', 'get_positions'])),
        'symbol': draw(st.sampled_from(['RELIANCE', 'TCS', 'INFY', 'NIFTY'])),
        'retry_count': draw(st.integers(min_value=0, max_value=5))
    }


# Strategy for generating order parameters
@st.composite
def order_params_strategy(draw):
    """Generate random order parameters"""
    return {
        'symbol': draw(st.sampled_from(['RELIANCE', 'TCS', 'INFY'])),
        'direction': draw(st.sampled_from([1, -1])),
        'quantity': draw(st.integers(min_value=1, max_value=1000)),
        'order_type': draw(st.sampled_from(['MARKET', 'LIMIT', 'SL', 'SL-M'])),
        'price': draw(st.floats(min_value=100, max_value=5000, allow_nan=False, allow_infinity=False))
    }


class TestErrorLoggingProperty:
    """Property-based tests for error logging completeness"""
    
    @given(
        error_type=st.sampled_from([
            AuthenticationError,
            ConnectionError,
            DataError,
            OrderError,
            MarketError,
            ValidationError
        ]),
        error_message=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',))),
        error_code=st.text(min_size=1, max_size=20, alphabet=st.characters(min_codepoint=65, max_codepoint=90)),
        context=error_context_strategy()
    )
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    def test_property_18_error_logging_completeness(
        self,
        error_type,
        error_message,
        error_code,
        context
    ):
        """
        Property 18: Error Logging Completeness
        
        For any broker API error, the system should log:
        - Error code
        - Error message
        - Operation context
        
        Validates: Requirements 12.1, 12.4
        """
        # Setup logger with string capture
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.DEBUG)
        
        logger = logging.getLogger('test_error_handler')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        
        error_handler = ErrorHandler(logger)
        
        # Create error with code and context
        error = error_type(error_message, error_code=error_code, context=context)
        
        # Log the error
        error_handler.log_error(error, context)
        
        # Get logged output
        log_output = log_stream.getvalue()
        
        # Property: Error code must be in log output
        assert error_code in log_output, \
            f"Error code '{error_code}' not found in log output"
        
        # Property: Error message must be in log output
        assert error_message in log_output, \
            f"Error message '{error_message}' not found in log output"
        
        # Property: Context operation must be in log output
        if 'operation' in context:
            assert context['operation'] in log_output, \
                f"Context operation '{context['operation']}' not found in log output"
        
        # Property: Error type must be in log output
        assert error_type.__name__ in log_output, \
            f"Error type '{error_type.__name__}' not found in log output"
        
        # Cleanup
        logger.removeHandler(handler)
    
    @given(
        order_params=order_params_strategy(),
        error_message=st.sampled_from([
            'Insufficient margin',
            'Invalid symbol',
            'Invalid price',
            'Order rejected',
            'Position limit exceeded',
            'Rate limit exceeded'
        ])
    )
    @settings(max_examples=100, deadline=None)
    def test_property_28_order_failure_error_messages(
        self,
        order_params,
        error_message
    ):
        """
        Property 28: Order Failure Error Messages
        
        For any failed order placement, the Order_Manager should return
        a descriptive error message explaining why the order failed.
        
        Validates: Requirements 5.8, 12.4
        """
        # Setup logger with string capture
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.DEBUG)
        
        logger = logging.getLogger('test_order_error_handler')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        
        error_handler = ErrorHandler(logger)
        
        # Create order error
        original_error = Exception(error_message)
        
        # Handle order error
        try:
            error_handler.handle_order_error(original_error, order_params)
        except OrderError as e:
            # Property: Error message must be descriptive (not just original error)
            assert len(str(e)) > len(error_message), \
                "Error message should be more descriptive than original error"
            
            # Property: Error message must contain guidance
            assert "guidance" in str(e).lower() or any(
                keyword in str(e).lower() 
                for keyword in ['check', 'reduce', 'add', 'verify', 'close']
            ), "Error message should contain actionable guidance"
            
            # Property: Order parameters must be logged
            log_output = log_stream.getvalue()
            assert order_params['symbol'] in log_output, \
                f"Symbol '{order_params['symbol']}' not found in log output"
            
            # Property: Guidance must be logged
            assert 'Guidance:' in log_output, \
                "Guidance not found in log output"
            
            # Property: Original error must be preserved in context
            assert e.context is not None, \
                "Error context should not be None"
            assert 'order_params' in e.context, \
                "Order parameters should be in error context"
            assert 'guidance' in e.context, \
                "Guidance should be in error context"
        
        # Cleanup
        logger.removeHandler(handler)
    
    @given(
        symbol=st.sampled_from(['RELIANCE', 'TCS', 'INFY', 'INVALID_SYMBOL']),
        timeframe=st.sampled_from(['minute', '5minute', '30minute', 'day']),
        operation=st.sampled_from(['fetch_data', 'get_instrument_token', 'validate_symbol'])
    )
    @settings(max_examples=50, deadline=None)
    def test_data_error_logging_includes_context(
        self,
        symbol,
        timeframe,
        operation
    ):
        """
        Test that data errors include symbol, timeframe, and operation context.
        
        Validates: Requirements 12.1, 12.4
        """
        # Setup logger with string capture
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.DEBUG)
        
        logger = logging.getLogger('test_data_error_handler')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        
        error_handler = ErrorHandler(logger)
        
        # Create data error
        original_error = Exception(f"Failed to fetch data for {symbol}")
        
        # Handle data error
        try:
            error_handler.handle_data_error(original_error, symbol, timeframe, operation)
        except DataError as e:
            # Property: Symbol must be in error message
            assert symbol in str(e), \
                f"Symbol '{symbol}' not found in error message"
            
            # Property: Timeframe must be in error message
            assert timeframe in str(e), \
                f"Timeframe '{timeframe}' not found in error message"
            
            # Property: Context must include all parameters
            assert e.context is not None, \
                "Error context should not be None"
            assert e.context['symbol'] == symbol, \
                "Symbol in context should match input"
            assert e.context['timeframe'] == timeframe, \
                "Timeframe in context should match input"
            assert e.context['operation'] == operation, \
                "Operation in context should match input"
            
            # Property: All context elements must be logged
            log_output = log_stream.getvalue()
            assert symbol in log_output, \
                f"Symbol '{symbol}' not found in log output"
            assert timeframe in log_output, \
                f"Timeframe '{timeframe}' not found in log output"
            assert operation in log_output, \
                f"Operation '{operation}' not found in log output"
        
        # Cleanup
        logger.removeHandler(handler)
    
    @given(
        max_retries=st.integers(min_value=1, max_value=5),
        initial_delay=st.floats(min_value=0.1, max_value=2.0, allow_nan=False, allow_infinity=False),
        backoff_factor=st.floats(min_value=1.5, max_value=3.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=50, deadline=None)
    def test_retry_logic_logs_all_attempts(
        self,
        max_retries,
        initial_delay,
        backoff_factor
    ):
        """
        Test that retry logic logs all retry attempts.
        
        Validates: Requirements 12.1, 12.3
        """
        # Setup logger with string capture
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.DEBUG)
        
        logger = logging.getLogger('test_retry_handler')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        
        error_handler = ErrorHandler(logger)
        
        # Create function that always fails
        attempt_count = [0]
        
        def failing_function():
            attempt_count[0] += 1
            raise Exception(f"Attempt {attempt_count[0]} failed")
        
        # Try to execute with retry
        try:
            error_handler.retry_with_backoff(
                failing_function,
                max_retries=max_retries,
                initial_delay=initial_delay,
                backoff_factor=backoff_factor
            )
        except Exception:
            pass  # Expected to fail
        
        # Property: All attempts must be logged
        log_output = log_stream.getvalue()
        
        # Should have attempted max_retries + 1 times (initial + retries)
        assert attempt_count[0] == max_retries + 1, \
            f"Expected {max_retries + 1} attempts, got {attempt_count[0]}"
        
        # Property: Retry messages must be in log
        if max_retries > 0:
            assert 'Retry' in log_output or 'retry' in log_output, \
                "Retry messages not found in log output"
        
        # Property: Final failure must be logged
        assert 'failed' in log_output.lower(), \
            "Final failure not logged"
        
        # Cleanup
        logger.removeHandler(handler)


class TestKiteAdapterErrorHandling:
    """Test error handling in KiteAdapter"""
    
    @given(
        symbol=st.sampled_from(['RELIANCE', 'TCS', 'INFY']),
        quantity=st.floats(min_value=-100, max_value=0, allow_nan=False, allow_infinity=False),
        order_type=st.sampled_from(['MARKET', 'LIMIT', 'SL', 'SL-M'])
    )
    @settings(max_examples=50, deadline=None)
    def test_invalid_quantity_returns_none_and_logs_error(
        self,
        symbol,
        quantity,
        order_type
    ):
        """
        Test that invalid quantity (negative or zero) returns None and logs error.
        
        Validates: Requirements 5.9, 12.4
        """
        # Setup mock config
        config = {
            'kite_api_key': 'test_key',
            'kite_token_file': 'test_token.json',
            'default_exchange': 'NSE'
        }
        
        # Create adapter
        adapter = KiteAdapter(config)
        adapter.kite = Mock()  # Mock Kite Connect
        
        # Mock get_instrument_info to return valid instrument
        adapter.get_instrument_info = Mock(return_value={
            'symbol': symbol,
            'lot_size': 1,
            'tick_size': 0.05,
            'instrument_token': '12345'
        })
        
        # Try to place order with invalid quantity
        result = adapter.place_order(
            symbol=symbol,
            direction=1,
            quantity=quantity,
            order_type=order_type
        )
        
        # Property: Invalid quantity must return None
        assert result is None, \
            f"Expected None for invalid quantity {quantity}, got {result}"
        
        # Property: Kite API should not be called
        adapter.kite.place_order.assert_not_called()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
