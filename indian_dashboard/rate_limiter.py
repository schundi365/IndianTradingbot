"""
Rate Limiter Module
Implements rate limiting for API endpoints
"""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import request, jsonify
import logging

logger = logging.getLogger(__name__)


def get_rate_limit_key():
    """
    Get the key for rate limiting.
    Uses IP address by default, but can be extended to use session ID or API key.
    """
    # Try to get session ID first (more accurate for authenticated users)
    try:
        from flask import session
        if 'session_id' in session:
            return f"session:{session.get('session_id')}"
    except (RuntimeError, KeyError):
        # Session not available or no session_id
        pass
    
    # Fall back to IP address
    return f"ip:{get_remote_address()}"


def rate_limit_exceeded_handler(e):
    """
    Custom handler for rate limit exceeded errors.
    
    Args:
        e: RateLimitExceeded exception
        
    Returns:
        JSON response with error details
    """
    logger.warning(f"Rate limit exceeded: {get_rate_limit_key()} - {request.path}")
    
    return jsonify({
        'status': 'error',
        'error': 'rate_limit_exceeded',
        'message': 'Too many requests. Please slow down and try again later.',
        'retry_after': e.description if hasattr(e, 'description') else None
    }), 429


def init_rate_limiter(app, storage_uri=None):
    """
    Initialize rate limiter for Flask app.
    
    Args:
        app: Flask application instance
        storage_uri: Optional storage URI for rate limit data (default: in-memory)
        
    Returns:
        Limiter instance
    """
    # Configure storage
    if storage_uri is None:
        # Use in-memory storage by default
        storage_uri = "memory://"
    
    # Create limiter instance
    limiter = Limiter(
        app=app,
        key_func=get_rate_limit_key,
        default_limits=["200 per hour", "50 per minute"],  # Global default limits
        storage_uri=storage_uri,
        strategy="fixed-window",  # Can be "fixed-window" or "moving-window"
        headers_enabled=True,  # Add rate limit headers to responses
        swallow_errors=True,  # Don't crash if storage fails
    )
    
    # Register custom error handler
    app.register_error_handler(429, rate_limit_exceeded_handler)
    
    logger.info(f"Rate limiter initialized with storage: {storage_uri}")
    
    return limiter


# Rate limit decorators for different endpoint types
# These can be imported and used on specific routes

# Strict limits for authentication endpoints (prevent brute force)
AUTH_RATE_LIMIT = "5 per minute"

# Moderate limits for data modification endpoints
WRITE_RATE_LIMIT = "30 per minute"

# Relaxed limits for read-only endpoints
READ_RATE_LIMIT = "100 per minute"

# Very relaxed limits for status/health check endpoints
STATUS_RATE_LIMIT = "200 per minute"

# Strict limits for expensive operations (instrument refresh, etc.)
EXPENSIVE_RATE_LIMIT = "3 per minute"


def get_limiter_from_app():
    """
    Get limiter instance from current Flask app.
    This is a helper to access the limiter in blueprints.
    
    Returns:
        Limiter instance or None
    """
    from flask import current_app
    return current_app.config.get('LIMITER')

