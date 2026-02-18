"""
OAuth Handler Service
Manages OAuth flows, token storage, and token refresh for brokers
"""

import logging
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple
from kiteconnect import KiteConnect

logger = logging.getLogger(__name__)


class OAuthHandler:
    """
    Handles OAuth authentication flows for brokers
    Manages access tokens, refresh tokens, and token expiry
    """
    
    def __init__(self, token_storage_dir: str = None):
        """
        Initialize OAuth handler
        
        Args:
            token_storage_dir: Directory to store OAuth tokens
        """
        if token_storage_dir is None:
            token_storage_dir = Path(__file__).parent.parent.parent / "data" / "oauth_tokens"
        
        self.token_storage_dir = Path(token_storage_dir)
        self.token_storage_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"OAuth handler initialized with token storage: {self.token_storage_dir}")
    
    def get_oauth_url(self, broker: str, api_key: str, redirect_url: str = None) -> Optional[str]:
        """
        Generate OAuth URL for broker
        
        Args:
            broker: Broker ID (e.g., 'kite', 'upstox')
            api_key: API key for OAuth
            redirect_url: Optional custom redirect URL
            
        Returns:
            OAuth URL or None if not supported
        """
        try:
            if broker == 'kite':
                kite = KiteConnect(api_key=api_key)
                oauth_url = kite.login_url()
                logger.info(f"Generated Kite OAuth URL for API key: {api_key[:8]}...")
                return oauth_url
                
            elif broker == 'upstox':
                # Upstox OAuth implementation
                # TODO: Implement when Upstox adapter is ready
                logger.warning("Upstox OAuth not yet implemented")
                return None
                
            else:
                logger.warning(f"OAuth not supported for broker: {broker}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating OAuth URL for {broker}: {e}", exc_info=True)
            return None
    
    def exchange_token(self, broker: str, api_key: str, api_secret: str, 
                      request_token: str) -> Tuple[bool, Dict]:
        """
        Exchange request token for access token
        
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
            if broker == 'kite':
                return self._exchange_kite_token(api_key, api_secret, request_token)
            elif broker == 'upstox':
                # TODO: Implement Upstox token exchange
                return False, {'error': 'Upstox OAuth not yet implemented'}
            else:
                return False, {'error': f'OAuth not supported for broker: {broker}'}
                
        except Exception as e:
            error_msg = f"Token exchange error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, {'error': error_msg}
    
    def _exchange_kite_token(self, api_key: str, api_secret: str, 
                            request_token: str) -> Tuple[bool, Dict]:
        """
        Exchange Kite request token for access token
        
        Args:
            api_key: Kite API key
            api_secret: Kite API secret
            request_token: Request token from OAuth callback
            
        Returns:
            Tuple of (success: bool, result: dict)
        """
        try:
            kite = KiteConnect(api_key=api_key)
            
            # Generate session
            logger.info("Exchanging request token for access token...")
            data = kite.generate_session(request_token, api_secret=api_secret)
            access_token = data['access_token']
            
            # Set access token
            kite.set_access_token(access_token)
            
            # Get user profile
            logger.info("Fetching user profile...")
            profile = kite.profile()
            
            # Calculate token expiry (Kite tokens expire at 6 AM next day)
            token_expiry = self._calculate_kite_token_expiry()
            
            # Store token
            self._store_token(
                broker='kite',
                api_key=api_key,
                access_token=access_token,
                token_expiry=token_expiry,
                user_info=profile
            )
            
            logger.info(f"Successfully obtained access token for user: {profile.get('user_id')}")
            logger.info(f"Token expires at: {token_expiry}")
            
            return True, {
                'access_token': access_token,
                'token_expiry': token_expiry.strftime('%Y-%m-%d %H:%M:%S'),
                'user_info': {
                    'user_id': profile.get('user_id'),
                    'user_name': profile.get('user_name'),
                    'email': profile.get('email'),
                    'broker': profile.get('broker')
                }
            }
            
        except Exception as e:
            error_msg = f"Kite token exchange failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, {'error': error_msg}
    
    def _calculate_kite_token_expiry(self) -> datetime:
        """
        Calculate Kite token expiry time
        Kite tokens expire at 6:00 AM IST the next day
        
        Returns:
            datetime object representing token expiry
        """
        now = datetime.now()
        
        # If current time is before 6 AM, token expires today at 6 AM
        if now.hour < 6:
            expiry = now.replace(hour=6, minute=0, second=0, microsecond=0)
        else:
            # Otherwise, token expires tomorrow at 6 AM
            tomorrow = now + timedelta(days=1)
            expiry = tomorrow.replace(hour=6, minute=0, second=0, microsecond=0)
        
        return expiry
    
    def _store_token(self, broker: str, api_key: str, access_token: str,
                    token_expiry: datetime, user_info: Dict):
        """
        Store OAuth token to file
        
        Args:
            broker: Broker ID
            api_key: API key (used as identifier)
            access_token: Access token
            token_expiry: Token expiry datetime
            user_info: User profile information
        """
        try:
            # Use full API key hash for unique filename
            import hashlib
            api_key_hash = hashlib.md5(api_key.encode()).hexdigest()[:16]
            token_file = self.token_storage_dir / f"{broker}_{api_key_hash}.json"
            
            token_data = {
                'broker': broker,
                'api_key': api_key,
                'access_token': access_token,
                'token_expiry': token_expiry.isoformat(),
                'user_info': user_info,
                'created_at': datetime.now().isoformat(),
                'last_refreshed': datetime.now().isoformat()
            }
            
            with open(token_file, 'w') as f:
                json.dump(token_data, f, indent=2)
            
            logger.info(f"Token stored to: {token_file}")
            
        except Exception as e:
            logger.error(f"Failed to store token: {e}", exc_info=True)
    
    def load_token(self, broker: str, api_key: str) -> Optional[Dict]:
        """
        Load stored OAuth token
        
        Args:
            broker: Broker ID
            api_key: API key
            
        Returns:
            Token data dict or None if not found/expired
        """
        try:
            # Use same hash method as storage
            import hashlib
            api_key_hash = hashlib.md5(api_key.encode()).hexdigest()[:16]
            token_file = self.token_storage_dir / f"{broker}_{api_key_hash}.json"
            
            if not token_file.exists():
                logger.info(f"No stored token found for {broker}")
                return None
            
            with open(token_file, 'r') as f:
                token_data = json.load(f)
            
            # Check if token is expired
            token_expiry = datetime.fromisoformat(token_data['token_expiry'])
            if datetime.now() >= token_expiry:
                logger.warning(f"Stored token for {broker} has expired")
                return None
            
            logger.info(f"Loaded valid token for {broker}, expires: {token_expiry}")
            return token_data
            
        except Exception as e:
            logger.error(f"Failed to load token: {e}", exc_info=True)
            return None
    
    def is_token_valid(self, broker: str, api_key: str) -> bool:
        """
        Check if stored token is valid (exists and not expired)
        
        Args:
            broker: Broker ID
            api_key: API key
            
        Returns:
            True if token is valid, False otherwise
        """
        token_data = self.load_token(broker, api_key)
        return token_data is not None
    
    def get_token_expiry(self, broker: str, api_key: str) -> Optional[datetime]:
        """
        Get token expiry time
        
        Args:
            broker: Broker ID
            api_key: API key
            
        Returns:
            datetime object or None if token not found
        """
        token_data = self.load_token(broker, api_key)
        if token_data:
            return datetime.fromisoformat(token_data['token_expiry'])
        return None
    
    def delete_token(self, broker: str, api_key: str) -> bool:
        """
        Delete stored token
        
        Args:
            broker: Broker ID
            api_key: API key
            
        Returns:
            True if deleted, False if not found
        """
        try:
            # Use same hash method as storage
            import hashlib
            api_key_hash = hashlib.md5(api_key.encode()).hexdigest()[:16]
            token_file = self.token_storage_dir / f"{broker}_{api_key_hash}.json"
            
            if token_file.exists():
                os.remove(token_file)
                logger.info(f"Deleted token for {broker}")
                return True
            else:
                logger.warning(f"No token file found to delete for {broker}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete token: {e}", exc_info=True)
            return False
    
    def refresh_token(self, broker: str, api_key: str) -> Tuple[bool, Dict]:
        """
        Refresh OAuth token (if supported by broker)
        
        Note: Kite Connect does not support token refresh.
        Tokens must be regenerated through OAuth flow.
        
        Args:
            broker: Broker ID
            api_key: API key
            
        Returns:
            Tuple of (success: bool, result: dict)
        """
        if broker == 'kite':
            # Kite doesn't support token refresh
            # User must re-authenticate through OAuth
            return False, {
                'error': 'Kite Connect does not support token refresh. Please re-authenticate.',
                'requires_reauth': True
            }
        elif broker == 'upstox':
            # TODO: Implement Upstox token refresh when available
            return False, {'error': 'Upstox token refresh not yet implemented'}
        else:
            return False, {'error': f'Token refresh not supported for broker: {broker}'}
    
    def list_stored_tokens(self) -> list:
        """
        List all stored tokens
        
        Returns:
            List of dicts with broker, api_key, expiry info
        """
        tokens = []
        
        try:
            for token_file in self.token_storage_dir.glob("*.json"):
                try:
                    with open(token_file, 'r') as f:
                        token_data = json.load(f)
                    
                    expiry = datetime.fromisoformat(token_data['token_expiry'])
                    is_valid = datetime.now() < expiry
                    
                    tokens.append({
                        'broker': token_data['broker'],
                        'api_key': token_data['api_key'][:8] + '...',
                        'user_id': token_data.get('user_info', {}).get('user_id'),
                        'expiry': expiry.strftime('%Y-%m-%d %H:%M:%S'),
                        'is_valid': is_valid,
                        'file': token_file.name
                    })
                    
                except Exception as e:
                    logger.error(f"Error reading token file {token_file}: {e}")
                    continue
            
            return tokens
            
        except Exception as e:
            logger.error(f"Error listing tokens: {e}", exc_info=True)
            return []
    
    def cleanup_expired_tokens(self) -> int:
        """
        Delete all expired tokens
        
        Returns:
            Number of tokens deleted
        """
        deleted_count = 0
        
        try:
            for token_file in self.token_storage_dir.glob("*.json"):
                try:
                    with open(token_file, 'r') as f:
                        token_data = json.load(f)
                    
                    expiry = datetime.fromisoformat(token_data['token_expiry'])
                    
                    if datetime.now() >= expiry:
                        os.remove(token_file)
                        deleted_count += 1
                        logger.info(f"Deleted expired token: {token_file.name}")
                        
                except Exception as e:
                    logger.error(f"Error processing token file {token_file}: {e}")
                    continue
            
            logger.info(f"Cleaned up {deleted_count} expired tokens")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up tokens: {e}", exc_info=True)
            return deleted_count
