"""
Session Management API Endpoints
"""

from flask import Blueprint, jsonify, request, g
import logging
from rate_limiter import (
    READ_RATE_LIMIT,
    WRITE_RATE_LIMIT,
    STATUS_RATE_LIMIT
)

logger = logging.getLogger(__name__)


def init_session_api(session_manager):
    """
    Initialize session API blueprint
    
    Args:
        session_manager: SessionManager instance
    
    Returns:
        Blueprint: Flask blueprint for session endpoints
    """
    session_bp = Blueprint('session', __name__, url_prefix='/api/session')
    
    @session_bp.before_request
    def before_request():
        """Make session manager available in request context"""
        g.session_manager = session_manager
    
    @session_bp.route('/info', methods=['GET'])
    def get_session_info():
        """
        Get current session information
        
        Returns:
            JSON response with session info
        """
        try:
            session_info = session_manager.get_session_info()
            
            if not session_info:
                return jsonify({
                    'status': 'success',
                    'session': None,
                    'message': 'No active session'
                }), 200
            
            return jsonify({
                'status': 'success',
                'session': session_info
            }), 200
            
        except Exception as e:
            logger.error(f"Error getting session info: {e}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @session_bp.route('/csrf-token', methods=['GET'])
    def get_csrf_token():
        """
        Get CSRF token for the current session
        
        Returns:
            JSON response with CSRF token
        """
        try:
            csrf_token = session_manager.get_csrf_token()
            
            return jsonify({
                'status': 'success',
                'csrf_token': csrf_token
            }), 200
            
        except Exception as e:
            logger.error(f"Error getting CSRF token: {e}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @session_bp.route('/extend', methods=['POST'])
    def extend_session():
        """
        Extend the current session
        
        Returns:
            JSON response with success status
        """
        try:
            success = session_manager.extend_session()
            
            if success:
                session_info = session_manager.get_session_info()
                return jsonify({
                    'status': 'success',
                    'message': 'Session extended',
                    'session': session_info
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'No active session to extend'
                }), 400
            
        except Exception as e:
            logger.error(f"Error extending session: {e}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @session_bp.route('/clear', methods=['POST'])
    def clear_session():
        """
        Clear the current session (logout)
        
        Returns:
            JSON response with success status
        """
        try:
            session_manager.clear_session()
            
            return jsonify({
                'status': 'success',
                'message': 'Session cleared'
            }), 200
            
        except Exception as e:
            logger.error(f"Error clearing session: {e}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @session_bp.route('/validate-csrf', methods=['POST'])
    def validate_csrf():
        """
        Validate a CSRF token (for testing)
        
        Request body:
            {
                "csrf_token": "token_to_validate"
            }
        
        Returns:
            JSON response with validation result
        """
        try:
            data = request.get_json()
            token = data.get('csrf_token')
            
            if not token:
                return jsonify({
                    'status': 'error',
                    'message': 'CSRF token required'
                }), 400
            
            is_valid = session_manager.validate_csrf_token(token)
            
            return jsonify({
                'status': 'success',
                'valid': is_valid
            }), 200
            
        except Exception as e:
            logger.error(f"Error validating CSRF token: {e}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    # Store route functions for rate limiting
    session_bp._get_session_info = get_session_info
    session_bp._get_csrf_token = get_csrf_token
    session_bp._extend_session = extend_session
    session_bp._clear_session = clear_session
    session_bp._validate_csrf = validate_csrf
    
    return session_bp


def apply_rate_limits(limiter, session_bp):
    """
    Apply rate limits to session API endpoints.
    Called after limiter is initialized.
    
    Args:
        limiter: Flask-Limiter instance
        session_bp: Session blueprint instance
    """
    limiter.limit(STATUS_RATE_LIMIT)(session_bp._get_session_info)
    limiter.limit(READ_RATE_LIMIT)(session_bp._get_csrf_token)
    limiter.limit(WRITE_RATE_LIMIT)(session_bp._extend_session)
    limiter.limit(WRITE_RATE_LIMIT)(session_bp._clear_session)
    limiter.limit(WRITE_RATE_LIMIT)(session_bp._validate_csrf)
