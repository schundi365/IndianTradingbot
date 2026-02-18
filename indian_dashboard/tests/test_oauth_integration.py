"""
OAuth Integration Tests
Tests for OAuth flow, token storage, and token refresh
"""

import sys
import os
import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from indian_dashboard.services.oauth_handler import OAuthHandler
from indian_dashboard.services.broker_manager import BrokerManager


class TestOAuthHandler:
    """Test OAuth handler functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Create temporary directory for token storage
        self.temp_dir = tempfile.mkdtemp()
        self.oauth_handler = OAuthHandler(token_storage_dir=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures"""
        # Clean up temporary directory
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_oauth_handler_initialization(self):
        """Test OAuth handler initializes correctly"""
        assert self.oauth_handler is not None
        assert self.oauth_handler.token_storage_dir.exists()
    
    def test_get_oauth_url_kite(self):
        """Test OAuth URL generation for Kite"""
        api_key = "test_api_key_12345"
        oauth_url = self.oauth_handler.get_oauth_url('kite', api_key)
        
        assert oauth_url is not None
        assert 'kite.zerodha.com' in oauth_url
        assert api_key in oauth_url
    
    def test_get_oauth_url_unsupported_broker(self):
        """Test OAuth URL for unsupported broker returns None"""
        oauth_url = self.oauth_handler.get_oauth_url('unsupported_broker', 'test_key')
        assert oauth_url is None
    
    def test_token_storage_and_retrieval(self):
        """Test storing and retrieving tokens"""
        # Create test token data
        broker = 'kite'
        api_key = 'test_api_key_12345'
        access_token = 'test_access_token_xyz'
        token_expiry = datetime.now() + timedelta(hours=12)
        user_info = {
            'user_id': 'TEST123',
            'user_name': 'Test User',
            'email': 'test@example.com'
        }
        
        # Store token
        self.oauth_handler._store_token(
            broker=broker,
            api_key=api_key,
            access_token=access_token,
            token_expiry=token_expiry,
            user_info=user_info
        )
        
        # Retrieve token
        token_data = self.oauth_handler.load_token(broker, api_key)
        
        assert token_data is not None
        assert token_data['broker'] == broker
        assert token_data['api_key'] == api_key
        assert token_data['access_token'] == access_token
        assert token_data['user_info'] == user_info
    
    def test_token_expiry_check(self):
        """Test token expiry validation"""
        broker = 'kite'
        api_key = 'test_api_key_12345'
        
        # Store expired token
        expired_token_expiry = datetime.now() - timedelta(hours=1)
        self.oauth_handler._store_token(
            broker=broker,
            api_key=api_key,
            access_token='expired_token',
            token_expiry=expired_token_expiry,
            user_info={}
        )
        
        # Try to load expired token
        token_data = self.oauth_handler.load_token(broker, api_key)
        assert token_data is None  # Should return None for expired token
    
    def test_is_token_valid(self):
        """Test token validity check"""
        broker = 'kite'
        api_key = 'test_api_key_12345'
        
        # No token stored yet
        assert not self.oauth_handler.is_token_valid(broker, api_key)
        
        # Store valid token
        token_expiry = datetime.now() + timedelta(hours=12)
        self.oauth_handler._store_token(
            broker=broker,
            api_key=api_key,
            access_token='valid_token',
            token_expiry=token_expiry,
            user_info={}
        )
        
        # Check validity
        assert self.oauth_handler.is_token_valid(broker, api_key)
    
    def test_delete_token(self):
        """Test token deletion"""
        broker = 'kite'
        api_key = 'test_api_key_12345'
        
        # Store token
        token_expiry = datetime.now() + timedelta(hours=12)
        self.oauth_handler._store_token(
            broker=broker,
            api_key=api_key,
            access_token='test_token',
            token_expiry=token_expiry,
            user_info={}
        )
        
        # Verify token exists
        assert self.oauth_handler.is_token_valid(broker, api_key)
        
        # Delete token
        result = self.oauth_handler.delete_token(broker, api_key)
        assert result is True
        
        # Verify token is gone
        assert not self.oauth_handler.is_token_valid(broker, api_key)
    
    def test_list_stored_tokens(self):
        """Test listing stored tokens"""
        # Store multiple tokens
        for i in range(3):
            api_key = f'test_api_key_{i}'
            token_expiry = datetime.now() + timedelta(hours=12)
            self.oauth_handler._store_token(
                broker='kite',
                api_key=api_key,
                access_token=f'token_{i}',
                token_expiry=token_expiry,
                user_info={'user_id': f'USER{i}'}
            )
        
        # List tokens
        tokens = self.oauth_handler.list_stored_tokens()
        assert len(tokens) == 3
        
        # Verify token info
        for token in tokens:
            assert 'broker' in token
            assert 'api_key' in token
            assert 'expiry' in token
            assert 'is_valid' in token
    
    def test_cleanup_expired_tokens(self):
        """Test cleanup of expired tokens"""
        # Store mix of valid and expired tokens
        for i in range(3):
            api_key = f'test_api_key_{i}'
            if i < 2:
                # Expired tokens
                token_expiry = datetime.now() - timedelta(hours=1)
            else:
                # Valid token
                token_expiry = datetime.now() + timedelta(hours=12)
            
            self.oauth_handler._store_token(
                broker='kite',
                api_key=api_key,
                access_token=f'token_{i}',
                token_expiry=token_expiry,
                user_info={}
            )
        
        # Clean up expired tokens
        deleted_count = self.oauth_handler.cleanup_expired_tokens()
        assert deleted_count == 2
        
        # Verify only valid token remains
        tokens = self.oauth_handler.list_stored_tokens()
        assert len(tokens) == 1
        assert tokens[0]['is_valid'] is True
    
    def test_kite_token_expiry_calculation(self):
        """Test Kite token expiry calculation"""
        expiry = self.oauth_handler._calculate_kite_token_expiry()
        
        # Verify expiry is at 6 AM
        assert expiry.hour == 6
        assert expiry.minute == 0
        assert expiry.second == 0
        
        # Verify expiry is in the future
        assert expiry > datetime.now()
    
    def test_refresh_token_kite_not_supported(self):
        """Test that Kite token refresh returns appropriate error"""
        success, result = self.oauth_handler.refresh_token('kite', 'test_key')
        
        assert success is False
        assert 'error' in result
        assert 'requires_reauth' in result
        assert result['requires_reauth'] is True


class TestBrokerManagerOAuth:
    """Test BrokerManager OAuth integration"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.broker_manager = BrokerManager()
    
    def test_broker_manager_has_oauth_handler(self):
        """Test BrokerManager has OAuth handler"""
        assert hasattr(self.broker_manager, 'oauth_handler')
        assert self.broker_manager.oauth_handler is not None
    
    def test_get_oauth_url(self):
        """Test OAuth URL generation through BrokerManager"""
        api_key = "test_api_key_12345"
        oauth_url = self.broker_manager.get_oauth_url('kite', api_key)
        
        assert oauth_url is not None
        assert 'kite.zerodha.com' in oauth_url
    
    def test_check_token_validity(self):
        """Test token validity check through BrokerManager"""
        is_valid, expiry = self.broker_manager.check_token_validity('kite', 'test_key')
        
        # Should return False for non-existent token
        assert is_valid is False
        assert expiry is None
    
    def test_list_stored_tokens(self):
        """Test listing tokens through BrokerManager"""
        tokens = self.broker_manager.list_stored_tokens()
        assert isinstance(tokens, list)
    
    def test_cleanup_expired_tokens(self):
        """Test cleanup through BrokerManager"""
        count = self.broker_manager.cleanup_expired_tokens()
        assert isinstance(count, int)
        assert count >= 0


def run_tests():
    """Run all OAuth tests"""
    print("=" * 60)
    print("OAuth Integration Tests")
    print("=" * 60)
    
    # Run pytest
    pytest.main([__file__, '-v', '--tb=short'])


if __name__ == '__main__':
    run_tests()
