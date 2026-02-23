"""
Global Error Handler for Indian Market Web Dashboard
Provides comprehensive error handling, logging, and graceful degradation
"""

import logging
import traceback
from functools import wraps
from flask import jsonify, request
from datetime import datetime

logger = logging.getLogger(__name__)


class ErrorType:
    """Error type constants"""
    VALIDATION = 'validation_error'
    AUTHENTICATION = 'authentication_error'
    AUTHORIZATION = 'authorization_error'
    NOT_FOUND = 'not_found'
    BROKER_ERROR = 'broker_error'
    RATE_LIMIT = 'rate_limit_error'
    TIMEOUT = 'timeout_error'
    NETWORK = 'network_error'
    SERVER = 'server_error'
    UNKNOWN = 'unknown_error'


class DashboardError(Exception):
    """Base exception for dashboard errors"""
    
    def __init__(self, message, error_type=ErrorType.UNKNOWN, status_code=500, details=None):
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.status_code = status_code
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self):
        """Convert error to dictionary for JSON response"""
        return {
            'success': False,
            'error': self.message,
            'error_type': self.error_type,
            'details': self.details,
            'timestamp': self.timestamp
        }


class ValidationError(DashboardError):
    """Validation error"""
    def __init__(self, message, details=None):
        super().__init__(message, ErrorType.VALIDATION, 400, details)


class AuthenticationError(DashboardError):
    """Authentication error"""
    def __init__(self, message, details=None):
        super().__init__(message, ErrorType.AUTHENTICATION, 401, details)


class AuthorizationError(DashboardError):
    """Authorization error"""
    def __init__(self, message, details=None):
        super().__init__(message, ErrorType.AUTHORIZATION, 403, details)


class NotFoundError(DashboardError):
    """Resource not found error"""
    def __init__(self, message, details=None):
        super().__init__(message, ErrorType.NOT_FOUND, 404, details)


class BrokerError(DashboardError):
    """Broker-related error"""
    def __init__(self, message, details=None):
        super().__init__(message, ErrorType.BROKER_ERROR, 502, details)


class RateLimitError(DashboardError):
    """Rate limit exceeded error"""
    def __init__(self, message, details=None):
        super().__init__(message, ErrorType.RATE_LIMIT, 429, details)


class TimeoutError(DashboardError):
    """Timeout error"""
    def __init__(self, message, details=None):
        super().__init__(message, ErrorType.TIMEOUT, 504, details)


class NetworkError(DashboardError):
    """Network error"""
    def __init__(self, message, details=None):
        super().__init__(message, ErrorType.NETWORK, 503, details)


def handle_errors(func):
    """
    Decorator to handle errors in API endpoints
    Catches exceptions and returns appropriate JSON responses
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DashboardError as e:
            # Log custom dashboard errors
            logger.warning(f"{e.error_type}: {e.message}", extra={
                'endpoint': request.endpoint,
                'method': request.method,
                'details': e.details
            })
            return jsonify(e.to_dict()), e.status_code
        except ValueError as e:
            # Handle validation errors
            logger.warning(f"Validation error: {str(e)}", extra={
                'endpoint': request.endpoint,
                'method': request.method
            })
            error = ValidationError(str(e))
            return jsonify(error.to_dict()), error.status_code
        except KeyError as e:
            # Handle missing required fields
            logger.warning(f"Missing required field: {str(e)}", extra={
                'endpoint': request.endpoint,
                'method': request.method
            })
            error = ValidationError(f"Missing required field: {str(e)}")
            return jsonify(error.to_dict()), error.status_code
        except Exception as e:
            # Log unexpected errors with full traceback
            logger.error(f"Unexpected error in {request.endpoint}: {str(e)}", exc_info=True, extra={
                'endpoint': request.endpoint,
                'method': request.method,
                'traceback': traceback.format_exc()
            })
            error = DashboardError(
                "An unexpected error occurred. Please try again.",
                ErrorType.SERVER,
                500,
                {'original_error': str(e)}
            )
            return jsonify(error.to_dict()), error.status_code
    
    return wrapper


def init_error_handlers(app):
    """
    Initialize global error handlers for Flask app
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request"""
        logger.warning(f"Bad request: {error}", extra={
            'endpoint': request.endpoint,
            'method': request.method
        })
        return jsonify({
            'success': False,
            'error': 'Bad request',
            'error_type': ErrorType.VALIDATION,
            'details': {'message': str(error)},
            'timestamp': datetime.now().isoformat()
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 Unauthorized"""
        logger.warning(f"Unauthorized access: {error}", extra={
            'endpoint': request.endpoint,
            'method': request.method
        })
        return jsonify({
            'success': False,
            'error': 'Authentication required',
            'error_type': ErrorType.AUTHENTICATION,
            'details': {'message': str(error)},
            'timestamp': datetime.now().isoformat()
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden"""
        logger.warning(f"Forbidden access: {error}", extra={
            'endpoint': request.endpoint,
            'method': request.method
        })
        return jsonify({
            'success': False,
            'error': 'Access forbidden',
            'error_type': ErrorType.AUTHORIZATION,
            'details': {'message': str(error)},
            'timestamp': datetime.now().isoformat()
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found"""
        logger.info(f"Resource not found: {request.path}", extra={
            'endpoint': request.endpoint,
            'method': request.method
        })
        return jsonify({
            'success': False,
            'error': 'Resource not found',
            'error_type': ErrorType.NOT_FOUND,
            'details': {'path': request.path},
            'timestamp': datetime.now().isoformat()
        }), 404
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        """Handle 429 Too Many Requests"""
        logger.warning(f"Rate limit exceeded: {error}", extra={
            'endpoint': request.endpoint,
            'method': request.method
        })
        return jsonify({
            'success': False,
            'error': 'Rate limit exceeded. Please try again later.',
            'error_type': ErrorType.RATE_LIMIT,
            'details': {'message': str(error)},
            'timestamp': datetime.now().isoformat()
        }), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server Error"""
        logger.error(f"Internal server error: {error}", exc_info=True, extra={
            'endpoint': request.endpoint,
            'method': request.method
        })
        return jsonify({
            'success': False,
            'error': 'Internal server error. Please try again.',
            'error_type': ErrorType.SERVER,
            'details': {},
            'timestamp': datetime.now().isoformat()
        }), 500
    
    @app.errorhandler(502)
    def bad_gateway(error):
        """Handle 502 Bad Gateway (broker errors)"""
        logger.error(f"Bad gateway error: {error}", extra={
            'endpoint': request.endpoint,
            'method': request.method
        })
        return jsonify({
            'success': False,
            'error': 'Broker service unavailable. Please try again.',
            'error_type': ErrorType.BROKER_ERROR,
            'details': {'message': str(error)},
            'timestamp': datetime.now().isoformat()
        }), 502
    
    @app.errorhandler(503)
    def service_unavailable(error):
        """Handle 503 Service Unavailable"""
        logger.error(f"Service unavailable: {error}", extra={
            'endpoint': request.endpoint,
            'method': request.method
        })
        return jsonify({
            'success': False,
            'error': 'Service temporarily unavailable. Please try again.',
            'error_type': ErrorType.NETWORK,
            'details': {'message': str(error)},
            'timestamp': datetime.now().isoformat()
        }), 503
    
    @app.errorhandler(504)
    def gateway_timeout(error):
        """Handle 504 Gateway Timeout"""
        logger.error(f"Gateway timeout: {error}", extra={
            'endpoint': request.endpoint,
            'method': request.method
        })
        return jsonify({
            'success': False,
            'error': 'Request timeout. Please try again.',
            'error_type': ErrorType.TIMEOUT,
            'details': {'message': str(error)},
            'timestamp': datetime.now().isoformat()
        }), 504
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Handle all unexpected exceptions"""
        logger.error(f"Unexpected error: {error}", exc_info=True, extra={
            'endpoint': request.endpoint,
            'method': request.method,
            'traceback': traceback.format_exc()
        })
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred. Please try again.',
            'error_type': ErrorType.UNKNOWN,
            'details': {},
            'timestamp': datetime.now().isoformat()
        }), 500
    
    logger.info("Global error handlers initialized")


def log_request():
    """Log incoming request details"""
    logger.debug(f"Request: {request.method} {request.path}", extra={
        'method': request.method,
        'path': request.path,
        'remote_addr': request.remote_addr,
        'user_agent': request.user_agent.string if request.user_agent else None
    })


def log_response(response):
    """Log outgoing response details"""
    logger.debug(f"Response: {response.status_code}", extra={
        'status_code': response.status_code,
        'content_length': response.content_length
    })
    return response
