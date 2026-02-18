"""
Property-Based Test for Kite Authentication Token Validation
Tests Property 2: Kite Authentication Token Validation

**Validates: Requirements 2.2, 3.1**

This test validates that:
- Valid tokens with today's date allow successful authentication
- The adapter correctly reads and validates token files
- Connection is established when authentication succeeds
- Token validation is consistent across different valid token formats
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

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.kite_adapter import KiteAdapter
except ImportError as e:
    pytest.skip(f"Could not import KiteAdapter: {e}", allow_module_level=True)


# Strategy for generating valid access tokens
valid_access_token_strategy = st.text(
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


@given(
    api_key=api_key_strategy,
    access_token=valid_access_token_strategy,
    user_name=st.text(min_size=3, max_size=20).filter(lambda x: x.isalnum())
)
@settings(max_examples=5, deadline=None)
def test_kite_authentication_with_valid_today_token(api_key: str, access_token: str, user_name: str):
    """
    Property 2: Kite Authentication Token Validation
    
    For any valid token file with today's date, the Kite_Adapter should:
    1. Successfully read the token file
    2. Validate that the token is from today
    3. Authenticate with Kite Connect API
    4. Establish a connection that allows trading operations
    """
    # Create temporary token file with today's date
    with tempfile.TemporaryDirectory() as tmp_dir:
        token_file = Path(tmp_dir) / "kite_token.json"
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Write valid token file with today's date
        token_data = {
            "access_token": access_token,
            "date": today
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
        
        # Mock KiteConnect to avoid actual API calls
        with patch('src.kite_adapter.KiteConnect') as mock_kite_class:
            mock_kite_instance = MagicMock()
            mock_kite_class.return_value = mock_kite_instance
            
            # Mock profile response
            mock_kite_instance.profile.return_value = {
                'user_name': user_name,
                'broker': 'ZERODHA'
            }
            
            # Mock instruments response
            mock_kite_instance.instruments.return_value = [
                {
                    'exchange': 'NSE',
                    'tradingsymbol': 'RELIANCE',
                    'instrument_token': 738561,
                    'lot_size': 1,
                    'tick_size': 0.05
                }
            ]
            
            # Test connection
            result = adapter.connect()
            
            # Verify authentication succeeded
            assert result == True, \
                "Authentication should succeed with valid token from today"
            
            # Verify KiteConnect was initialized with correct API key
            mock_kite_class.assert_called_once_with(api_key=api_key)
            
            # Verify access token was set
            mock_kite_instance.set_access_token.assert_called_once_with(access_token)
            
            # Verify profile was fetched (connection verification)
            mock_kite_instance.profile.assert_called_once()
            
            # Verify adapter is connected
            assert adapter.is_connected() == True, \
                "Adapter should report as connected after successful authentication"
            
            # Verify access token is stored
            assert adapter.access_token == access_token, \
                "Access token should be stored in adapter"
            
            # Verify kite instance is stored
            assert adapter.kite is not None, \
                "Kite instance should be stored in adapter"


@given(
    api_key=api_key_strategy,
    access_token=valid_access_token_strategy,
    user_name=st.text(min_size=3, max_size=20).filter(lambda x: x.isalnum()),
    broker_name=st.sampled_from(['ZERODHA', 'KITE'])
)
@settings(max_examples=5, deadline=None)
def test_kite_authentication_allows_trading_operations(
    api_key: str, 
    access_token: str, 
    user_name: str,
    broker_name: str
):
    """
    Property 2: Kite Authentication Token Validation - Trading Operations
    
    For any valid token file with today's date, after successful authentication,
    the Kite_Adapter should allow trading operations such as:
    1. Fetching account information
    2. Checking connection status
    3. Accessing instrument cache
    """
    # Create temporary token file with today's date
    with tempfile.TemporaryDirectory() as tmp_dir:
        token_file = Path(tmp_dir) / "kite_token.json"
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Write valid token file
        token_data = {
            "access_token": access_token,
            "date": today
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
        
        # Mock KiteConnect
        with patch('src.kite_adapter.KiteConnect') as mock_kite_class:
            mock_kite_instance = MagicMock()
            mock_kite_class.return_value = mock_kite_instance
            
            # Mock profile response
            mock_kite_instance.profile.return_value = {
                'user_name': user_name,
                'broker': broker_name
            }
            
            # Mock instruments response
            mock_kite_instance.instruments.return_value = [
                {
                    'exchange': 'NSE',
                    'tradingsymbol': 'RELIANCE',
                    'instrument_token': 738561,
                    'lot_size': 1,
                    'tick_size': 0.05
                }
            ]
            
            # Mock margins response for is_connected check
            mock_kite_instance.margins.return_value = {
                'equity': {
                    'net': 500000.0,
                    'available': {'live_balance': 505000.0, 'cash': 450000.0},
                    'utilised': {'debits': 50000.0}
                }
            }
            
            # Authenticate
            result = adapter.connect()
            assert result == True, "Authentication should succeed"
            
            # Test that trading operations are allowed
            
            # 1. Check connection status
            is_connected = adapter.is_connected()
            assert is_connected == True, \
                "is_connected() should return True after successful authentication"
            mock_kite_instance.margins.assert_called()
            
            # 2. Verify instrument cache was loaded
            assert len(adapter.instrument_cache) > 0, \
                "Instrument cache should be populated after authentication"
            
            # 3. Verify access to account operations
            account_info = adapter.get_account_info()
            assert account_info is not None, \
                "Account info should be accessible after authentication"
            assert 'balance' in account_info, \
                "Account info should contain balance"
            assert 'equity' in account_info, \
                "Account info should contain equity"


@given(
    api_key=api_key_strategy,
    access_token=valid_access_token_strategy
)
@settings(max_examples=5, deadline=None)
def test_kite_authentication_token_file_reading(api_key: str, access_token: str):
    """
    Property 2: Kite Authentication Token Validation - Token File Reading
    
    For any valid token file format with today's date, the Kite_Adapter should:
    1. Correctly read the JSON token file
    2. Extract the access token
    3. Extract and validate the date
    4. Use the token for authentication
    """
    # Create temporary token file
    with tempfile.TemporaryDirectory() as tmp_dir:
        token_file = Path(tmp_dir) / "kite_token.json"
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Write token file
        token_data = {
            "access_token": access_token,
            "date": today
        }
        
        with open(token_file, 'w') as f:
            json.dump(token_data, f)
        
        # Verify file was created correctly
        assert token_file.exists(), "Token file should exist"
        
        # Read back and verify
        with open(token_file, 'r') as f:
            read_data = json.load(f)
        
        assert read_data['access_token'] == access_token, \
            "Token file should contain correct access token"
        assert read_data['date'] == today, \
            "Token file should contain today's date"
        
        # Create configuration
        config = {
            "kite_api_key": api_key,
            "kite_token_file": str(token_file),
            "default_exchange": "NSE"
        }
        
        # Create adapter
        adapter = KiteAdapter(config)
        
        # Mock KiteConnect
        with patch('src.kite_adapter.KiteConnect') as mock_kite_class:
            mock_kite_instance = MagicMock()
            mock_kite_class.return_value = mock_kite_instance
            
            # Mock profile response
            mock_kite_instance.profile.return_value = {
                'user_name': 'test_user',
                'broker': 'ZERODHA'
            }
            
            # Mock instruments response
            mock_kite_instance.instruments.return_value = []
            
            # Authenticate
            result = adapter.connect()
            
            # Verify authentication succeeded
            assert result == True, \
                "Authentication should succeed when token file is read correctly"
            
            # Verify the correct token was used
            mock_kite_instance.set_access_token.assert_called_once_with(access_token)


@given(
    api_key=api_key_strategy,
    access_token=valid_access_token_strategy,
    exchange=st.sampled_from(['NSE', 'BSE', 'NFO', 'CDS'])
)
@settings(max_examples=5, deadline=None)
def test_kite_authentication_with_different_exchanges(
    api_key: str, 
    access_token: str,
    exchange: str
):
    """
    Property 2: Kite Authentication Token Validation - Exchange Configuration
    
    For any valid token and exchange configuration, the Kite_Adapter should:
    1. Successfully authenticate regardless of configured exchange
    2. Store the exchange configuration
    3. Use the configured exchange for operations
    """
    # Create temporary token file
    with tempfile.TemporaryDirectory() as tmp_dir:
        token_file = Path(tmp_dir) / "kite_token.json"
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Write token file
        token_data = {
            "access_token": access_token,
            "date": today
        }
        
        with open(token_file, 'w') as f:
            json.dump(token_data, f)
        
        # Create configuration with specific exchange
        config = {
            "kite_api_key": api_key,
            "kite_token_file": str(token_file),
            "default_exchange": exchange
        }
        
        # Create adapter
        adapter = KiteAdapter(config)
        
        # Mock KiteConnect
        with patch('src.kite_adapter.KiteConnect') as mock_kite_class:
            mock_kite_instance = MagicMock()
            mock_kite_class.return_value = mock_kite_instance
            
            # Mock profile response
            mock_kite_instance.profile.return_value = {
                'user_name': 'test_user',
                'broker': 'ZERODHA'
            }
            
            # Mock instruments response
            mock_kite_instance.instruments.return_value = []
            
            # Authenticate
            result = adapter.connect()
            
            # Verify authentication succeeded
            assert result == True, \
                f"Authentication should succeed with {exchange} exchange configuration"
            
            # Verify exchange configuration is stored
            assert adapter.default_exchange == exchange, \
                f"Adapter should store configured exchange: {exchange}"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
