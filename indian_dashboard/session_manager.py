"""
Session Management for Indian Market Web Dashboard
Handles Flask sessions, session timeout, and CSRF protection
"""

from flask import session, request, jsonify, g
from functools import wraps
from datetime import datetime, timedelta
import secrets
import logging
import hashlib

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages user sessions with timeout and CSRF protection"""
    
    def __init__(self, app=None, session_timeout=3600):
        """
        Initialize session manager
        
        Args:
            app: Flask application instance
            session_timeout: Session timeout in seconds (default: 1 hour)
        """
        self.session_timeout = session_timeout
        self.csrf_token_length = 32
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """
        Initialize session manager with Flask app
        
        Args:
            app: Flask application instance
        """
        # Configure session settings
        app.config.setdefault('SESSION_COOKIE_SECURE', False)  # Set True in production with HTTPS
        app.config.setdefault('SESSION_COOKIE_HTTPONLY', True)
        app.config.setdefault('SESSION_COOKIE_SAMESITE', 'Lax')
        app.config.setdefault('PERMANENT_SESSION_LIFETIME', timedelta(seconds=self.session_timeout))
        
        # Register before_request handler for session validation
        app.before_request(self._validate_session)
        
        logger.info(f"SessionManager initialized with timeout: {self.session_timeout}s")
    
    def _validate_session(self):
        """Validate session before each request"""
        # Skip validation for static files and favicon
        if request.path.startswith('/static/') or request.path == '/favicon.ico':
            return
        
        # Check if session has expired
        if 'last_activity' in session:
            last_activity = datetime.fromisoformat(session['last_activity'])
            now = datetime.now()
            elapsed = (now - last_activity).total_seconds()
            
            if elapsed > self.session_timeout:
                logger.info(f"Session expired after {elapsed}s of inactivity")
                self.clear_session()
                
                # Return error for API requests
                if request.path.startswith('/api/'):
                    return jsonify({
                        'status': 'error',
                        'message': 'Session expired. Please refresh the page.',
                        'code': 'SESSION_EXPIRED'
                    }), 401
        
        # Update last activity timestamp
        session['last_activity'] = datetime.now().isoformat()
        session.permanent = True
    
    def create_session(self, user_data=None):
        """
        Create a new session
        
        Args:
            user_data: Optional user data to store in session
        
        Returns:
            dict: Session data including CSRF token
        """
        # Clear any existing session
        session.clear()
        
        # Set session as permanent (uses PERMANENT_SESSION_LIFETIME)
        session.permanent = True
        
        # Generate CSRF token
        csrf_token = self.generate_csrf_token()
        session['csrf_token'] = csrf_token
        
        # Set creation and last activity timestamps
        now = datetime.now().isoformat()
        session['created_at'] = now
        session['last_activity'] = now
        
        # Store user data if provided
        if user_data:
            session['user_data'] = user_data
        
        # Generate session ID for logging
        session_id = self._generate_session_id()
        session['session_id'] = session_id
        
        logger.info(f"New session created: {session_id}")
        
        return {
            'session_id': session_id,
            'csrf_token': csrf_token,
            'created_at': now,
            'expires_in': self.session_timeout
        }
    
    def clear_session(self):
        """Clear the current session"""
        session_id = session.get('session_id', 'unknown')
        session.clear()
        logger.info(f"Session cleared: {session_id}")
    
    def get_session_info(self):
        """
        Get current session information
        
        Returns:
            dict: Session information or None if no active session
        """
        if 'session_id' not in session:
            return None
        
        created_at = datetime.fromisoformat(session.get('created_at'))
        last_activity = datetime.fromisoformat(session.get('last_activity'))
        now = datetime.now()
        
        elapsed = (now - last_activity).total_seconds()
        remaining = max(0, self.session_timeout - elapsed)
        
        return {
            'session_id': session.get('session_id'),
            'created_at': session.get('created_at'),
            'last_activity': session.get('last_activity'),
            'elapsed_seconds': int(elapsed),
            'remaining_seconds': int(remaining),
            'is_active': remaining > 0,
            'user_data': session.get('user_data')
        }
    
    def extend_session(self):
        """Extend the current session by resetting last activity"""
        if 'session_id' in session:
            session['last_activity'] = datetime.now().isoformat()
            logger.debug(f"Session extended: {session.get('session_id')}")
            return True
        return False
    
    def generate_csrf_token(self):
        """
        Generate a new CSRF token
        
        Returns:
            str: CSRF token
        """
        return secrets.token_urlsafe(self.csrf_token_length)
    
    def get_csrf_token(self):
        """
        Get the current CSRF token, generating one if it doesn't exist
        
        Returns:
            str: CSRF token
        """
        if 'csrf_token' not in session:
            csrf_token = self.generate_csrf_token()
            session['csrf_token'] = csrf_token
            return csrf_token
        return session['csrf_token']
    
    def validate_csrf_token(self, token):
        """
        Validate a CSRF token
        
        Args:
            token: Token to validate
        
        Returns:
            bool: True if valid, False otherwise
        """
        if not token:
            return False
        
        session_token = session.get('csrf_token')
        if not session_token:
            return False
        
        # Use constant-time comparison to prevent timing attacks
        return secrets.compare_digest(token, session_token)
    
    def _generate_session_id(self):
        """
        Generate a unique session ID for logging
        
        Returns:
            str: Session ID
        """
        # Create a hash from random bytes and timestamp
        random_bytes = secrets.token_bytes(16)
        timestamp = datetime.now().isoformat().encode()
        hash_input = random_bytes + timestamp
        
        return hashlib.sha256(hash_input).hexdigest()[:16]
    
    def store_user_data(self, key, value):
        """
        Store user-specific data in session
        
        Args:
            key: Data key
            value: Data value
        """
        if 'user_data' not in session:
            session['user_data'] = {}
        
        session['user_data'][key] = value
        session.modified = True
    
    def get_user_data(self, key, default=None):
        """
        Get user-specific data from session
        
        Args:
            key: Data key
            default: Default value if key not found
        
        Returns:
            User data value or default
        """
        user_data = session.get('user_data', {})
        return user_data.get(key, default)
    
    def remove_user_data(self, key):
        """
        Remove user-specific data from session
        
        Args:
            key: Data key to remove
        """
        if 'user_data' in session and key in session['user_data']:
            del session['user_data'][key]
            session.modified = True


def require_csrf(f):
    """
    Decorator to require CSRF token validation for routes
    
    Usage:
        @app.route('/api/endpoint', methods=['POST'])
        @require_csrf
        def endpoint():
            return jsonify({'status': 'success'})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get CSRF token from request
        csrf_token = None
        
        # Check header first (preferred for AJAX requests)
        csrf_token = request.headers.get('X-CSRF-Token')
        
        # Fall back to form data
        if not csrf_token:
            csrf_token = request.form.get('csrf_token')
        
        # Fall back to JSON body
        if not csrf_token and request.is_json:
            csrf_token = request.json.get('csrf_token')
        
        # Validate token
        session_manager = g.get('session_manager')
        if not session_manager or not session_manager.validate_csrf_token(csrf_token):
            logger.warning(f"CSRF validation failed for {request.path}")
            return jsonify({
                'status': 'error',
                'message': 'CSRF token validation failed',
                'code': 'CSRF_INVALID'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_session(f):
    """
    Decorator to require an active session for routes
    
    Usage:
        @app.route('/api/endpoint')
        @require_session
        def endpoint():
            return jsonify({'status': 'success'})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_manager = g.get('session_manager')
        
        if not session_manager:
            return jsonify({
                'status': 'error',
                'message': 'Session manager not initialized',
                'code': 'SESSION_ERROR'
            }), 500
        
        session_info = session_manager.get_session_info()
        
        if not session_info or not session_info['is_active']:
            logger.warning(f"No active session for {request.path}")
            return jsonify({
                'status': 'error',
                'message': 'No active session. Please refresh the page.',
                'code': 'SESSION_REQUIRED'
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated_function
