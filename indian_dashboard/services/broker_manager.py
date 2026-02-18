"""
Broker Manager Service
Manages broker connections and adapters
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.broker_adapter import BrokerAdapter
from src.kite_adapter import KiteAdapter
from src.paper_trading_adapter import PaperTradingAdapter

# Import config
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import BROKER_CONFIGS, CREDENTIAL_FORMS

# Import OAuth handler
from services.oauth_handler import OAuthHandler

logger = logging.getLogger(__name__)


class BrokerManager:
    """Manages broker connections and adapters"""
    
    def __init__(self):
        self.current_broker = None
        self.current_broker_type = None
        self.broker_adapters = {
            'kite': KiteAdapter,
            'paper': PaperTradingAdapter,
            # Add more brokers as they are implemented
            # 'alice_blue': AliceBlueAdapter,
            # 'angel_one': AngelOneAdapter,
            # 'upstox': UpstoxAdapter,
        }
        self.connection_time = None
        self.user_info = {}
        self.access_token = None
        self.token_expiry = None
        
        # Initialize OAuth handler
        self.oauth_handler = OAuthHandler()
    
    def get_supported_brokers(self) -> List[Dict]:
        """
        Get list of supported brokers
        
        Returns:
            List of broker dictionaries with id, name, logo
        """
        brokers = []
        for broker_id, adapter_class in self.broker_adapters.items():
            config = BROKER_CONFIGS.get(broker_id, {})
            brokers.append({
                'id': broker_id,
                'name': config.get('name', broker_id.title()),
                'logo': config.get('logo', f'/static/logos/{broker_id}.png'),
                'oauth_enabled': config.get('oauth_enabled', False)
            })
        return brokers
    
    def get_credentials_form(self, broker: str) -> List[Dict]:
        """
        Get credential form fields for specific broker
        
        Args:
            broker: Broker ID (e.g., 'kite', 'alice_blue')
            
        Returns:
            List of form field dictionaries
        """
        return CREDENTIAL_FORMS.get(broker, [])
    
    def connect(self, broker: str, credentials: Dict, config: Dict = None) -> Tuple[bool, Dict]:
        """
        Connect to broker with credentials
        
        Args:
            broker: Broker ID
            credentials: Dictionary of credentials
            config: Optional configuration dictionary
            
        Returns:
            Tuple of (success: bool, result: dict)
            result contains 'user_info' on success or 'error' on failure
        """
        try:
            logger.info(f"Attempting to connect to broker: {broker}")
            
            # Check if broker is supported
            adapter_class = self.broker_adapters.get(broker)
            if not adapter_class:
                error_msg = f'Unsupported broker: {broker}'
                logger.error(error_msg)
                return False, {'error': error_msg}
            
            # Prepare configuration
            if config is None:
                config = {}
            
            # Add credentials to config
            config.update(credentials)
            
            # For Kite, handle special fields
            if broker == 'kite':
                config['kite_api_key'] = credentials.get('api_key')
                config['kite_api_secret'] = credentials.get('api_secret')
                # If access_token is provided (from OAuth), use it
                if 'access_token' in credentials:
                    config['access_token'] = credentials['access_token']
            
            # Create adapter instance
            logger.info(f"Creating {broker} adapter instance")
            adapter = adapter_class(config)
            
            # Connect
            logger.info(f"Connecting to {broker}...")
            if adapter.connect():
                self.current_broker = adapter
                self.current_broker_type = broker
                self.connection_time = datetime.now()
                
                # Get user info if available
                try:
                    if hasattr(adapter, 'get_user_info'):
                        self.user_info = adapter.get_user_info()
                    elif hasattr(adapter, 'kite') and adapter.kite:
                        # For Kite adapter
                        profile = adapter.kite.profile()
                        self.user_info = {
                            'user_id': profile.get('user_id'),
                            'user_name': profile.get('user_name'),
                            'email': profile.get('email'),
                            'broker': profile.get('broker')
                        }
                    else:
                        self.user_info = {'broker': broker}
                except Exception as e:
                    logger.warning(f"Could not fetch user info: {e}")
                    self.user_info = {'broker': broker}
                
                logger.info(f"Successfully connected to {broker}")
                logger.info(f"User info: {self.user_info}")
                
                return True, {'user_info': self.user_info}
            else:
                error_msg = 'Connection failed - check credentials and try again'
                logger.error(error_msg)
                return False, {'error': error_msg}
                
        except Exception as e:
            error_msg = f'Connection error: {str(e)}'
            logger.error(error_msg, exc_info=True)
            return False, {'error': error_msg}
    
    def disconnect(self) -> Tuple[bool, str]:
        """
        Disconnect from current broker
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if self.current_broker:
                broker_type = self.current_broker_type
                logger.info(f"Disconnecting from {broker_type}")
                
                self.current_broker.disconnect()
                self.current_broker = None
                self.current_broker_type = None
                self.connection_time = None
                self.user_info = {}
                self.access_token = None
                self.token_expiry = None
                
                logger.info(f"Disconnected from {broker_type}")
                return True, f"Disconnected from {broker_type}"
            else:
                return False, "No broker connected"
                
        except Exception as e:
            error_msg = f"Disconnect error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
    
    def is_connected(self) -> bool:
        """
        Check if broker is connected
        
        Returns:
            True if connected, False otherwise
        """
        if self.current_broker is None:
            return False
        
        try:
            return self.current_broker.is_connected()
        except Exception as e:
            logger.error(f"Error checking connection status: {e}")
            return False
    
    def get_status(self) -> Dict:
        """
        Get current broker connection status
        
        Returns:
            Dictionary with connection status information
        """
        if not self.is_connected():
            return {
                'connected': False,
                'broker': None,
                'user_info': {},
                'connection_time': None,
                'access_token': None,
                'token_expiry': None
            }
        
        return {
            'connected': True,
            'broker': self.current_broker_type,
            'user_info': self.user_info,
            'connection_time': self.connection_time.isoformat() if self.connection_time else None,
            'access_token': self.access_token,
            'token_expiry': self.token_expiry
        }
    
    def get_adapter(self) -> Optional[BrokerAdapter]:
        """
        Get current broker adapter
        
        Returns:
            BrokerAdapter instance or None if not connected
        """
        return self.current_broker
    
    def get_broker_type(self) -> Optional[str]:
        """
        Get current broker type
        
        Returns:
            Broker ID string or None if not connected
        """
        return self.current_broker_type
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        Test current broker connection
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.current_broker:
            return False, "No broker connected"
        
        try:
            if self.current_broker.is_connected():
                # Try to fetch account info as a connection test
                account_info = self.current_broker.get_account_info()
                if account_info:
                    return True, f"Connection OK - Balance: ₹{account_info.get('balance', 0):,.2f}"
                else:
                    return True, "Connection OK"
            else:
                return False, "Connection lost - please reconnect"
                
        except Exception as e:
            error_msg = f"Connection test failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def check_token_validity(self, broker: str, api_key: str) -> Tuple[bool, Optional[str]]:
        """
        Check if stored OAuth token is valid
        
        Args:
            broker: Broker ID
            api_key: API key
            
        Returns:
            Tuple of (is_valid: bool, expiry_time: str or None)
        """
        try:
            is_valid = self.oauth_handler.is_token_valid(broker, api_key)
            
            if is_valid:
                expiry = self.oauth_handler.get_token_expiry(broker, api_key)
                if expiry:
                    return True, expiry.strftime('%Y-%m-%d %H:%M:%S')
                return True, None
            else:
                return False, None
                
        except Exception as e:
            logger.error(f"Error checking token validity: {e}", exc_info=True)
            return False, None
    
    def load_stored_token(self, broker: str, api_key: str) -> Tuple[bool, Dict]:
        """
        Load and use stored OAuth token
        
        Args:
            broker: Broker ID
            api_key: API key
            
        Returns:
            Tuple of (success: bool, result: dict)
        """
        try:
            token_data = self.oauth_handler.load_token(broker, api_key)
            
            if not token_data:
                return False, {'error': 'No valid token found'}
            
            # Connect using stored token
            credentials = {
                'api_key': api_key,
                'access_token': token_data['access_token']
            }
            
            success, result = self.connect(broker, credentials)
            
            if success:
                self.access_token = token_data['access_token']
                self.token_expiry = token_data['token_expiry']
                
                return True, {
                    'access_token': token_data['access_token'],
                    'token_expiry': token_data['token_expiry'],
                    'user_info': token_data.get('user_info', {})
                }
            else:
                return False, result
                
        except Exception as e:
            error_msg = f"Error loading stored token: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, {'error': error_msg}
    
    def refresh_oauth_token(self, broker: str, api_key: str) -> Tuple[bool, Dict]:
        """
        Refresh OAuth token (if supported)
        
        Args:
            broker: Broker ID
            api_key: API key
            
        Returns:
            Tuple of (success: bool, result: dict)
        """
        return self.oauth_handler.refresh_token(broker, api_key)
    
    def list_stored_tokens(self) -> list:
        """
        List all stored OAuth tokens
        
        Returns:
            List of token info dicts
        """
        return self.oauth_handler.list_stored_tokens()
    
    def cleanup_expired_tokens(self) -> int:
        """
        Clean up expired OAuth tokens
        
        Returns:
            Number of tokens deleted
        """
        return self.oauth_handler.cleanup_expired_tokens()
    
    def get_oauth_url(self, broker: str, api_key: str) -> Optional[str]:
        """
        Get OAuth URL for broker
        
        Args:
            broker: Broker ID
            api_key: API key for OAuth
            
        Returns:
            OAuth URL or None if not supported
        """
        try:
            # Use OAuth handler
            return self.oauth_handler.get_oauth_url(broker, api_key)
                
        except Exception as e:
            logger.error(f"Error getting OAuth URL: {e}", exc_info=True)
            return None
    
    def complete_oauth(self, broker: str, api_key: str, api_secret: str, 
                      request_token: str) -> Tuple[bool, Dict]:
        """
        Complete OAuth flow by exchanging request token for access token
        
        Args:
            broker: Broker ID
            api_key: API key
            api_secret: API secret
            request_token: Request token from OAuth callback
            
        Returns:
            Tuple of (success: bool, result: dict)
            result contains 'access_token', 'token_expiry', 'user_info' on success
        """
        try:
            # Use OAuth handler to exchange token
            success, result = self.oauth_handler.exchange_token(
                broker, api_key, api_secret, request_token
            )
            
            if success:
                # Connect using the access token
                credentials = {
                    'api_key': api_key,
                    'api_secret': api_secret,
                    'access_token': result['access_token']
                }
                
                connect_success, connect_result = self.connect(broker, credentials)
                
                if connect_success:
                    # Store token info
                    self.access_token = result['access_token']
                    self.token_expiry = result['token_expiry']
                    
                    return True, result
                else:
                    return False, connect_result
            else:
                return False, result
                
        except Exception as e:
            error_msg = f"OAuth completion error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, {'error': error_msg}
