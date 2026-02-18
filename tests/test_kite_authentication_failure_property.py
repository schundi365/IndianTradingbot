"""
Property-Based Test for Kite Authentication Failure Handling
Tests Property 3: Authentication Failure Handling

**Validates: Requirements 2.3, 3.3, 3.4**

This test validates that:
- Invalid or expired tokens are rejected
- Missing token files are handled gracefully
- Tokens from previous days are rejected
- Descriptive error messages are provided
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
import json
from unittest.mock import Mock, MagicMock, patch
import tempfile
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.kite_adapter import KiteAdapter
except ImportError as e:
    pytest.skip(f"Could not import KiteAdapter: {e}", allow_module_level=True)


# Strategy for generating access tokens
access_token_strategy = st.text(
    alphabet=st.characters(min_codepoint=48, max_codepoint=122, blacklist_categories=('Cc', 'Cs')),
    min_size=32,
    max_size=64
).filter(lambda x: len(x.strip()) > 0)

# Strategy for generating API keys
api_key_strategy = st.text(
    alphabet=st.characters(min_codepoint=48, max_codepoint=122, blacklist_categories=('Cc', 'Cs')),
    min_size=16,
    max_size=32
).filter(lambda x: len(x.strip()) > 0)

# Strategy for generating dates in the past (1-30 days ago)
past_date_strategy = st.integers(min_value=1, max_value=30).map(
    lambda days: (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
)


@given(
    api_key=api_key_strategy,
    access_token=access_token_strategy,
    days_ago=st.integers(min_value=1, max_value=30)
)
@settings(max_examples=5, deadline=None)
def test_authentication_rejects_expired_tokens(api_key: str, access_token: str, days_ago: int):
    """
    Property 3: Authentication Failure Handling - Expired Tokens
    
    For any token file with a date from a previous day, the Kite_Adapter should:
    1. Detect that the token is expired (not from today)
    2. Return False from connect()
    3. Log a descriptive error message
    4. Prevent trading operations
    """
    # Create temporary token file with past date
    with tempfile.TemporaryDirectory() as tmp_dir:
        token_file = Path(tmp_dir) / "kite_token.json"
        past_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        # Write token file with past date
        token_data = {
            "access_token": access_token,
            "date": past_date
        }
        
        with open(token_file, 'w') as f:
            json.dump(token_data, f)
        
        # Create configuration
        config = {
            "kite_api_key": api_key,
            "kite_token_file": str(token_file),
            "default_exchange": "NSE"
        }
        
        # Create adapter
        adapter = KiteAdapter(config)
        
        # Set up logger to capture messages
        log_messages = []
        
        class LogCapture(logging.Handler):
            def emit(self, record):
                log_messages.append({
                    'level': record.levelname,
                    'message': record.getMessage()
                })
        
        handler = LogCapture()
        adapter.logger.addHandler(handler)
        adapter.logger.setLevel(logging.DEBUG)
        
        # Test connection with expired token
        result = adapter.connect()
        
        # Verify authentication failed
        assert result == False, \
            f"Authentication should fail with token from {days_ago} days ago"
        
        # Verify descriptive error was logged
        error_messages = [msg for msg in log_messages if msg['level'] == 'ERROR']
        assert len(error_messages) >= 2, \
            "Should log at least 2 error messages for expired token"
        
        # Check that error messages are descriptive
        all_error_text = ' '.join([msg['message'] for msg in error_messages])
        
        assert past_date in all_error_text or "token" in all_error_text.lower(), \
            "Error message should mention the token date or token issue"
        
        assert "re-authenticate" in all_error_text.lower() or "kite_login" in all_error_text.lower(), \
            "Error message should provide instructions to re-authenticate"
        
        # Verify adapter is not connected
        assert adapter.is_connected() == False, \
            "Adapter should not be connected after failed authentication"
        
        # Verify access token was not set
        assert adapter.access_token is None, \
            "Access token should not be stored when authentication fails"
        
        # Verify kite instance was not created
        assert adapter.kite is None, \
            "Kite instance should not be created when authentication fails"


@given(
    api_key=api_key_strategy
)
@settings(max_examples=5, deadline=None)
def test_authentication_handles_missing_token_file(api_key: str):
    """
    Property 3: Authentication Failure Handling - Missing Token File
    
    For any configuration with a non-existent token file, the Kite_Adapter should:
    1. Detect that the token file is missing
    2. Return False from connect()
    3. Log a descriptive error message with instructions
    4. Prevent trading operations
    """
    # Create temporary directory but don't create token file
    with tempfile.TemporaryDirectory() as tmp_dir:
        token_file = Path(tmp_dir) / "nonexistent_token.json"
        
        # Verify file doesn't exist
        assert not token_file.exists(), "Token file should not exist for this test"
        
        # Create configuration
        config = {
            "kite_api_key": api_key,
            "kite_token_file": str(token_file),
            "default_exchange": "NSE"
        }
        
        # Create adapter
        adapter = KiteAdapter(config)
        
        # Set up logger to capture messages
        log_messages = []
        
        class LogCapture(logging.Handler):
            def emit(self, record):
                log_messages.append({
                    'level': record.levelname,
                    'message': record.getMessage()
                })
        
        handler = LogCapture()
        adapter.logger.addHandler(handler)
        adapter.logger.setLevel(logging.DEBUG)
        
        # Test connection with missing token file
        result = adapter.connect()
        
        # Verify authentication failed
        assert result == False, \
            "Authentication should fail when token file is missing"
        
        # Verify descriptive error was logged
        error_messages = [msg for msg in log_messages if msg['level'] == 'ERROR']
        assert len(error_messages) >= 2, \
            "Should log at least 2 error messages for missing token file"
        
        # Check that error messages are descriptive
        all_error_text = ' '.join([msg['message'] for msg in error_messages])
        
        assert "not found" in all_error_text.lower() or "missing" in all_error_text.lower(), \
            "Error message should indicate token file is missing"
        
        assert "kite_login" in all_error_text.lower() or "authenticate" in all_error_text.lower(), \
            "Error message should provide instructions to run login script"
        
        # Verify adapter is not connected
        assert adapter.is_connected() == False, \
            "Adapter should not be connected when token file is missing"
        
        # Verify access token was not set
        assert adapter.access_token is None, \
            "Access token should not be stored when token file is missing"


@given(
    api_key=api_key_strategy,
    access_token=access_token_strategy
)
@settings(max_examples=5, deadline=None)
def test_authentication_rejects_invalid_token_format(api_key: str, access_token: str):
    """
    Property 3: Authentication Failure Handling - Invalid Token Format
    
    For any token file with invalid JSON or missing required fields, the Kite_Adapter should:
    1. Detect the invalid format
    2. Return False from connect()
    3. Handle the error gracefully
    4. Prevent trading operations
    """
    # Create temporary token file with invalid JSON
    with tempfile.TemporaryDirectory() as tmp_dir:
        token_file = Path(tmp_dir) / "kite_token.json"
        
        # Write invalid JSON
        with open(token_file, 'w') as f:
            f.write("{ invalid json content }")
        
        # Create configuration
        config = {
            "kite_api_key": api_key,
            "kite_token_file": str(token_file),
            "default_exchange": "NSE"
        }
        
        # Create adapter
        adapter = KiteAdapter(config)
        
        # Test connection with invalid token file
        result = adapter.connect()
        
        # Verify authentication failed
        assert result == False, \
            "Authentication should fail with invalid JSON in token file"
        
        # Verify adapter is not connected
        assert adapter.is_connected() == False, \
            "Adapter should not be connected after failed authentication"


@given(
    api_key=api_key_strategy,
    access_token=access_token_strategy
)
@settings(max_examples=5, deadline=None)
def test_authentication_rejects_token_missing_date_field(api_key: str, access_token: str):
    """
    Property 3: Authentication Failure Handling - Missing Date Field
    
    For any token file missing the 'date' field, the Kite_Adapter should:
    1. Detect the missing field
    2. Return False from connect()
    3. Handle the error gracefully
    4. Prevent trading operations
    """
    # Create temporary token file without date field
    with tempfile.TemporaryDirectory() as tmp_dir:
        token_file = Path(tmp_dir) / "kite_token.json"
        
        # Write token file without date field
        token_data = {
            "access_token": access_token
            # Missing 'date' field
        }
        
        with open(token_file, 'w') as f:
            json.dump(token_data, f)
        
        # Create configuration
        config = {
            "kite_api_key": api_key,
            "kite_token_file": str(token_file),
            "default_exchange": "NSE"
        }
        
        # Create adapter
        adapter = KiteAdapter(config)
        
        # Test connection with incomplete token file
        result = adapter.connect()
        
        # Verify authentication failed
        assert result == False, \
            "Authentication should fail when token file is missing date field"
        
        # Verify adapter is not connected
        assert adapter.is_connected() == False, \
            "Adapter should not be connected after failed authentication"


@given(
    api_key=api_key_strategy,
    access_token=access_token_strategy
)
@settings(max_examples=5, deadline=None)
def test_authentication_prevents_operations_after_failure(api_key: str, access_token: str):
    """
    Property 3: Authentication Failure Handling - Prevent Trading Operations
    
    For any failed authentication, the Kite_Adapter should:
    1. Prevent all trading operations
    2. Return appropriate error values for operations
    3. Maintain a disconnected state
    """
    # Create temporary directory without token file
    with tempfile.TemporaryDirectory() as tmp_dir:
        token_file = Path(tmp_dir) / "missing_token.json"
        
        # Create configuration
        config = {
            "kite_api_key": api_key,
            "kite_token_file": str(token_file),
            "default_exchange": "NSE"
        }
        
        # Create adapter
        adapter = KiteAdapter(config)
        
        # Attempt connection (should fail)
        result = adapter.connect()
        assert result == False, "Authentication should fail"
        
        # Verify trading operations are prevented
        
        # 1. is_connected should return False
        assert adapter.is_connected() == False, \
            "is_connected() should return False after failed authentication"
        
        # 2. get_historical_data should return None
        data = adapter.get_historical_data("RELIANCE", "30minute", 100)
        assert data is None, \
            "get_historical_data() should return None when not connected"
        
        # 3. place_order should return None
        order_id = adapter.place_order("RELIANCE", 1, 10, "MARKET")
        assert order_id is None, \
            "place_order() should return None when not connected"
        
        # 4. get_positions should return empty list
        positions = adapter.get_positions()
        assert positions == [], \
            "get_positions() should return empty list when not connected"
        
        # 5. get_account_info should return zero values
        account_info = adapter.get_account_info()
        assert account_info['balance'] == 0.0, \
            "get_account_info() should return zero balance when not connected"
        assert account_info['equity'] == 0.0, \
            "get_account_info() should return zero equity when not connected"


@given(
    api_key=api_key_strategy,
    access_token=access_token_strategy,
    days_ago=st.integers(min_value=1, max_value=30)
)
@settings(max_examples=5, deadline=None)
def test_authentication_error_messages_are_descriptive(api_key: str, access_token: str, days_ago: int):
    """
    Property 3: Authentication Failure Handling - Descriptive Error Messages
    
    For any authentication failure scenario, the Kite_Adapter should:
    1. Provide clear error messages explaining the problem
    2. Include actionable instructions for resolution
    3. Log errors at appropriate severity level
    """
    # Test with expired token
    with tempfile.TemporaryDirectory() as tmp_dir:
        token_file = Path(tmp_dir) / "kite_token.json"
        past_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        # Write token file with past date
        token_data = {
            "access_token": access_token,
            "date": past_date
        }
        
        with open(token_file, 'w') as f:
            json.dump(token_data, f)
        
        # Create configuration
        config = {
            "kite_api_key": api_key,
            "kite_token_file": str(token_file),
            "default_exchange": "NSE"
        }
        
        # Create adapter with real logger to capture messages
        adapter = KiteAdapter(config)
        
        # Set up logger to capture messages
        log_messages = []
        
        class LogCapture(logging.Handler):
            def emit(self, record):
                log_messages.append({
                    'level': record.levelname,
                    'message': record.getMessage()
                })
        
        handler = LogCapture()
        adapter.logger.addHandler(handler)
        adapter.logger.setLevel(logging.DEBUG)
        
        # Attempt connection
        result = adapter.connect()
        
        # Verify authentication failed
        assert result == False, "Authentication should fail with expired token"
        
        # Verify error messages were logged
        error_messages = [msg for msg in log_messages if msg['level'] == 'ERROR']
        assert len(error_messages) >= 2, \
            "Should log at least 2 error messages for expired token"
        
        # Verify messages are descriptive
        all_error_text = ' '.join([msg['message'] for msg in error_messages])
        
        # Should mention the problem
        assert any([
            past_date in all_error_text,
            "token" in all_error_text.lower(),
            "expired" in all_error_text.lower(),
            "previous" in all_error_text.lower()
        ]), "Error messages should describe the problem"
        
        # Should provide solution
        assert any([
            "kite_login" in all_error_text.lower(),
            "re-authenticate" in all_error_text.lower(),
            "authenticate" in all_error_text.lower()
        ]), "Error messages should provide instructions for resolution"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
