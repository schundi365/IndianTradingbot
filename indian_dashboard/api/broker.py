"""
Broker API endpoints
"""

from flask import Blueprint, request, jsonify, session, current_app
import logging
from validators import (
    validate_json_request,
    validate_query_params,
    sanitize_request_data,
    validate_broker_type,
    validate_path_param_string,
    sanitize_string
)
from rate_limiter import (
    AUTH_RATE_LIMIT,
    READ_RATE_LIMIT,
    WRITE_RATE_LIMIT
)

logger = logging.getLogger(__name__)

# Create blueprint
broker_bp = Blueprint('broker', __name__, url_prefix='/api/broker')


def init_broker_api(broker_manager, credential_manager=None):
    """
    Initialize broker API with dependencies
    
    Args:
        broker_manager: BrokerManager instance
        credential_manager: CredentialManager instance (optional)
    """
    # Store in blueprint for access in routes
    broker_bp.broker_manager = broker_manager
    broker_bp.credential_manager = credential_manager
    
    return broker_bp


def apply_rate_limits(limiter):
    """
    Apply rate limits to broker API endpoints.
    Called after limiter is initialized.
    
    Args:
        limiter: Flask-Limiter instance
    """
    limiter.limit(READ_RATE_LIMIT)(list_brokers)
    limiter.limit(READ_RATE_LIMIT)(get_credentials_form)
    limiter.limit(AUTH_RATE_LIMIT)(connect_broker)
    limiter.limit(WRITE_RATE_LIMIT)(disconnect_broker)
    limiter.limit(READ_RATE_LIMIT)(get_broker_status)
    limiter.limit(WRITE_RATE_LIMIT)(test_connection)
    limiter.limit(AUTH_RATE_LIMIT)(initiate_oauth)
    limiter.limit(READ_RATE_LIMIT)(list_saved_credentials)
    limiter.limit(AUTH_RATE_LIMIT)(load_saved_credentials)
    limiter.limit(WRITE_RATE_LIMIT)(delete_saved_credentials)
    limiter.limit(AUTH_RATE_LIMIT)(check_token_validity)
    limiter.limit(AUTH_RATE_LIMIT)(load_stored_token)
    limiter.limit(AUTH_RATE_LIMIT)(refresh_token)
    limiter.limit(READ_RATE_LIMIT)(list_stored_tokens)


@broker_bp.route('/list', methods=['GET'])
def list_brokers():
    """
    Get list of supported brokers
    
    Returns:
        JSON response with list of brokers
    """
    try:
        brokers = broker_bp.broker_manager.get_supported_brokers()
        
        return jsonify({
            'success': True,
            'brokers': brokers
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing brokers: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@broker_bp.route('/credentials-form/<broker>', methods=['GET'])
def get_credentials_form(broker):
    """
    Get credential form fields for specific broker
    
    Args:
        broker: Broker ID
        
    Returns:
        JSON response with form fields
    """
    try:
        # Validate and sanitize broker parameter
        broker = sanitize_string(broker, max_length=50)
        is_valid, error = validate_broker_type(broker)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error
            }), 400
        
        form_fields = broker_bp.broker_manager.get_credentials_form(broker)
        
        return jsonify({
            'success': True,
            'broker': broker,
            'fields': form_fields
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting credentials form: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@broker_bp.route('/connect', methods=['POST'])
@validate_json_request(required_fields=['broker', 'credentials'])
@sanitize_request_data({
    'broker': {'type': 'string', 'max_length': 50},
    'save_credentials': {'type': 'bool'}
})
def connect_broker():
    """
    Connect to broker with credentials
    
    Request body:
        {
            "broker": "kite",
            "credentials": {
                "api_key": "...",
                "api_secret": "..."
            },
            "save_credentials": true  // Optional: save encrypted credentials
        }
        
    Returns:
        JSON response with connection status
    """
    try:
        data = request.get_json()
        
        broker = data.get('broker')
        credentials = data.get('credentials', {})
        save_credentials = data.get('save_credentials', False)
        
        # Validate broker type
        is_valid, error = validate_broker_type(broker)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error
            }), 400
        
        # Validate credentials is a dict
        if not isinstance(credentials, dict):
            return jsonify({
                'success': False,
                'error': 'Credentials must be an object'
            }), 400
        
        # Connect to broker
        success, result = broker_bp.broker_manager.connect(broker, credentials)
        
        if success:
            # Store broker in session
            session['broker'] = broker
            session['connected'] = True
            
            # Save encrypted credentials if requested
            if save_credentials and broker_bp.credential_manager:
                try:
                    broker_bp.credential_manager.save_credentials(broker, credentials)
                    logger.info(f"Saved encrypted credentials for {broker}")
                except Exception as e:
                    logger.error(f"Failed to save credentials: {e}")
                    # Don't fail the connection if credential saving fails
            
            return jsonify({
                'success': True,
                'message': f'Connected to {broker}',
                'user_info': result.get('user_info', {}),
                'credentials_saved': save_credentials
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Connection failed')
            }), 400
            
    except Exception as e:
        logger.error(f"Error connecting to broker: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@broker_bp.route('/disconnect', methods=['POST'])
def disconnect_broker():
    """
    Disconnect from current broker
    
    Returns:
        JSON response with disconnection status
    """
    try:
        success, message = broker_bp.broker_manager.disconnect()
        
        if success:
            # Clear session
            session.pop('broker', None)
            session.pop('connected', None)
            
            return jsonify({
                'success': True,
                'message': message
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400
            
    except Exception as e:
        logger.error(f"Error disconnecting from broker: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@broker_bp.route('/status', methods=['GET'])
def get_broker_status():
    """
    Get current broker connection status
    
    Returns:
        JSON response with connection status
    """
    try:
        status = broker_bp.broker_manager.get_status()
        
        return jsonify({
            'success': True,
            'status': status
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting broker status: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@broker_bp.route('/test', methods=['POST'])
def test_connection():
    """
    Test current broker connection
    
    Returns:
        JSON response with test result
    """
    try:
        success, message = broker_bp.broker_manager.test_connection()
        
        return jsonify({
            'success': success,
            'message': message
        }), 200 if success else 400
        
    except Exception as e:
        logger.error(f"Error testing connection: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@broker_bp.route('/oauth/initiate', methods=['POST'])
@validate_json_request(required_fields=['broker'])
@sanitize_request_data({
    'broker': {'type': 'string', 'max_length': 50},
    'api_key': {'type': 'string', 'max_length': 200},
    'api_secret': {'type': 'string', 'max_length': 200}
})
def initiate_oauth():
    """
    Initiate OAuth flow for supported brokers
    
    Request body:
        {
            "broker": "kite",
            "api_key": "...",
            "api_secret": "..."
        }
        
    Returns:
        JSON response with OAuth URL
    """
    try:
        data = request.get_json()
        
        broker = data.get('broker')
        api_key = data.get('api_key')
        api_secret = data.get('api_secret')
        
        # Validate broker type
        is_valid, error = validate_broker_type(broker)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error
            }), 400
        
        # Store credentials in session for OAuth callback
        session['oauth_broker'] = broker
        session['oauth_api_key'] = api_key
        session['oauth_api_secret'] = api_secret
        
        # Get OAuth URL
        oauth_url = broker_bp.broker_manager.get_oauth_url(broker, api_key)
        
        if oauth_url:
            return jsonify({
                'success': True,
                'oauth_url': oauth_url
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'OAuth not supported for this broker'
            }), 400
            
    except Exception as e:
        logger.error(f"Error initiating OAuth: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@broker_bp.route('/oauth/callback', methods=['GET'])
def oauth_callback():
    """
    Handle OAuth callback from broker
    
    Query params:
        request_token: Token from OAuth provider
        status: success/failure
        
    Returns:
        HTML page with JavaScript to communicate with parent window
    """
    try:
        request_token = request.args.get('request_token')
        status = request.args.get('status')
        
        if status != 'success' or not request_token:
            error = request.args.get('message', 'OAuth authentication failed')
            return f"""
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        text-align: center;
                        padding: 50px;
                        background: #f5f5f5;
                    }}
                    .error-box {{
                        background: white;
                        padding: 30px;
                        border-radius: 8px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        max-width: 500px;
                        margin: 0 auto;
                    }}
                    h2 {{ color: #dc3545; }}
                </style>
            </head>
            <body>
                <div class="error-box">
                    <h2>❌ Authentication Failed</h2>
                    <p>{error}</p>
                    <p>Redirecting to dashboard...</p>
                </div>
                <script>
                    if (window.opener) {{
                        window.opener.postMessage({{
                            type: 'oauth_error',
                            error: '{error}'
                        }}, '*');
                    }}
                    setTimeout(() => {{
                        window.location.href = '/';
                    }}, 2000);
                </script>
            </body>
            </html>
            """, 400
        
        # Get stored credentials from session
        broker = session.get('oauth_broker')
        api_key = session.get('oauth_api_key')
        api_secret = session.get('oauth_api_secret')
        
        if not broker or not api_key or not api_secret:
            return """
            <html>
            <head>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        text-align: center;
                        padding: 50px;
                        background: #f5f5f5;
                    }
                    .error-box {
                        background: white;
                        padding: 30px;
                        border-radius: 8px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        max-width: 500px;
                        margin: 0 auto;
                    }
                    h2 { color: #dc3545; }
                </style>
            </head>
            <body>
                <div class="error-box">
                    <h2>❌ Session Expired</h2>
                    <p>Please try logging in again.</p>
                    <p>Redirecting to dashboard...</p>
                </div>
                <script>
                    if (window.opener) {
                        window.opener.postMessage({
                            type: 'oauth_error',
                            error: 'Session expired'
                        }, '*');
                    }
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 2000);
                </script>
            </body>
            </html>
            """, 400
        
        # Exchange request token for access token
        success, result = broker_bp.broker_manager.complete_oauth(
            broker, api_key, api_secret, request_token
        )
        
        if success:
            # Store broker in session
            session['broker'] = broker
            session['connected'] = True
            
            # Clear OAuth session data
            session.pop('oauth_broker', None)
            session.pop('oauth_api_key', None)
            session.pop('oauth_api_secret', None)
            
            # Return success page with redirect to dashboard
            access_token = result.get('access_token', '')
            token_expiry = result.get('token_expiry', '')
            user_info = result.get('user_info', {})
            
            return f"""
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        text-align: center;
                        padding: 50px;
                        background: #f5f5f5;
                    }}
                    .success-box {{
                        background: white;
                        padding: 30px;
                        border-radius: 8px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        max-width: 500px;
                        margin: 0 auto;
                    }}
                    h1 {{ color: #28a745; }}
                    .spinner {{
                        border: 4px solid #f3f3f3;
                        border-top: 4px solid #28a745;
                        border-radius: 50%;
                        width: 40px;
                        height: 40px;
                        animation: spin 1s linear infinite;
                        margin: 20px auto;
                    }}
                    @keyframes spin {{
                        0% {{ transform: rotate(0deg); }}
                        100% {{ transform: rotate(360deg); }}
                    }}
                </style>
            </head>
            <body>
                <div class="success-box">
                    <h1>✅ Authentication Successful!</h1>
                    <p><strong>User:</strong> {user_info.get('user_id', 'N/A')}</p>
                    <div class="spinner"></div>
                    <p>Redirecting to dashboard...</p>
                </div>
                <script>
                    // Notify parent window if opened in popup
                    if (window.opener) {{
                        window.opener.postMessage({{
                            type: 'oauth_success',
                            broker: '{broker}',
                            user_info: {user_info},
                            token_expiry: '{token_expiry}'
                        }}, '*');
                    }}
                    // Redirect to dashboard root
                    setTimeout(() => {{
                        window.location.href = '/';
                    }}, 1500);
                </script>
            </body>
            </html>
            """
        else:
            error = result.get('error', 'Authentication failed')
            return f"""
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        text-align: center;
                        padding: 50px;
                        background: #f5f5f5;
                    }}
                    .error-box {{
                        background: white;
                        padding: 30px;
                        border-radius: 8px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        max-width: 500px;
                        margin: 0 auto;
                    }}
                    h2 {{ color: #dc3545; }}
                </style>
            </head>
            <body>
                <div class="error-box">
                    <h2>❌ Authentication Failed</h2>
                    <p>{error}</p>
                    <p>Redirecting to dashboard...</p>
                </div>
                <script>
                    if (window.opener) {{
                        window.opener.postMessage({{
                            type: 'oauth_error',
                            error: '{error}'
                        }}, '*');
                    }}
                    setTimeout(() => {{
                        window.location.href = '/';
                    }}, 2000);
                </script>
            </body>
            </html>
            """, 400
            
    except Exception as e:
        logger.error(f"Error in OAuth callback: {e}", exc_info=True)
        return f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    text-align: center;
                    padding: 50px;
                    background: #f5f5f5;
                }}
                .error-box {{
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    max-width: 500px;
                    margin: 0 auto;
                }}
                h2 {{ color: #dc3545; }}
            </style>
        </head>
        <body>
            <div class="error-box">
                <h2>❌ Error</h2>
                <p>{str(e)}</p>
                <p>Redirecting to dashboard...</p>
            </div>
            <script>
                if (window.opener) {{
                    window.opener.postMessage({{
                        type: 'oauth_error',
                        error: '{str(e)}'
                    }}, '*');
                }}
                setTimeout(() => {{
                    window.location.href = '/';
                }}, 2000);
            </script>
        </body>
        </html>
        """, 500


@broker_bp.route('/oauth/token/check', methods=['POST'])
@validate_json_request(required_fields=['broker', 'api_key'])
@sanitize_request_data({
    'broker': {'type': 'string', 'max_length': 50},
    'api_key': {'type': 'string', 'max_length': 200}
})
def check_token_validity():
    """
    Check if stored OAuth token is valid
    
    Request body:
        {
            "broker": "kite",
            "api_key": "..."
        }
        
    Returns:
        JSON response with token validity status
    """
    try:
        data = request.get_json()
        broker = data.get('broker')
        api_key = data.get('api_key')
        
        # Validate broker type
        is_valid_broker, error = validate_broker_type(broker)
        if not is_valid_broker:
            return jsonify({
                'success': False,
                'error': error
            }), 400
        
        is_valid, expiry = broker_bp.broker_manager.check_token_validity(broker, api_key)
        
        return jsonify({
            'success': True,
            'is_valid': is_valid,
            'token_expiry': expiry
        }), 200
        
    except Exception as e:
        logger.error(f"Error checking token validity: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@broker_bp.route('/oauth/token/load', methods=['POST'])
@validate_json_request(required_fields=['broker', 'api_key'])
@sanitize_request_data({
    'broker': {'type': 'string', 'max_length': 50},
    'api_key': {'type': 'string', 'max_length': 200}
})
def load_stored_token():
    """
    Load and use stored OAuth token
    
    Request body:
        {
            "broker": "kite",
            "api_key": "..."
        }
        
    Returns:
        JSON response with connection status
    """
    try:
        data = request.get_json()
        broker = data.get('broker')
        api_key = data.get('api_key')
        
        # Validate broker type
        is_valid_broker, error = validate_broker_type(broker)
        if not is_valid_broker:
            return jsonify({
                'success': False,
                'error': error
            }), 400
        
        success, result = broker_bp.broker_manager.load_stored_token(broker, api_key)
        
        if success:
            # Store broker in session
            session['broker'] = broker
            session['connected'] = True
            
            return jsonify({
                'success': True,
                'message': f'Connected using stored token',
                'user_info': result.get('user_info', {}),
                'token_expiry': result.get('token_expiry')
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to load token')
            }), 400
            
    except Exception as e:
        logger.error(f"Error loading stored token: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@broker_bp.route('/oauth/token/refresh', methods=['POST'])
@validate_json_request(required_fields=['broker', 'api_key'])
@sanitize_request_data({
    'broker': {'type': 'string', 'max_length': 50},
    'api_key': {'type': 'string', 'max_length': 200}
})
def refresh_token():
    """
    Refresh OAuth token (if supported)
    
    Request body:
        {
            "broker": "kite",
            "api_key": "..."
        }
        
    Returns:
        JSON response with refresh status
    """
    try:
        data = request.get_json()
        broker = data.get('broker')
        api_key = data.get('api_key')
        
        # Validate broker type
        is_valid_broker, error = validate_broker_type(broker)
        if not is_valid_broker:
            return jsonify({
                'success': False,
                'error': error
            }), 400
        
        success, result = broker_bp.broker_manager.refresh_oauth_token(broker, api_key)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Token refreshed successfully',
                'token_expiry': result.get('token_expiry')
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Token refresh failed'),
                'requires_reauth': result.get('requires_reauth', False)
            }), 400
            
    except Exception as e:
        logger.error(f"Error refreshing token: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@broker_bp.route('/oauth/tokens/list', methods=['GET'])
def list_stored_tokens():
    """
    List all stored OAuth tokens
    
    Returns:
        JSON response with list of tokens
    """
    try:
        tokens = broker_bp.broker_manager.list_stored_tokens()
        
        return jsonify({
            'success': True,
            'tokens': tokens
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing tokens: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@broker_bp.route('/credentials/saved', methods=['GET'])
def list_saved_credentials():
    """
    List brokers with saved credentials
    
    Returns:
        JSON response with list of brokers that have saved credentials
    """
    try:
        if not broker_bp.credential_manager:
            return jsonify({
                'success': False,
                'error': 'Credential manager not available'
            }), 500
        
        brokers = broker_bp.credential_manager.list_saved_brokers()
        
        return jsonify({
            'success': True,
            'brokers': brokers
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing saved credentials: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@broker_bp.route('/credentials/load/<broker>', methods=['POST'])
def load_saved_credentials(broker):
    """
    Load saved credentials and connect to broker
    
    Args:
        broker: Broker ID
        
    Returns:
        JSON response with connection status
    """
    try:
        # Validate and sanitize broker parameter
        broker = sanitize_string(broker, max_length=50)
        is_valid, error = validate_broker_type(broker)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error
            }), 400
        
        if not broker_bp.credential_manager:
            return jsonify({
                'success': False,
                'error': 'Credential manager not available'
            }), 500
        
        # Load encrypted credentials
        credentials = broker_bp.credential_manager.load_credentials(broker)
        
        if not credentials:
            return jsonify({
                'success': False,
                'error': f'No saved credentials found for {broker}'
            }), 404
        
        # Connect using loaded credentials
        success, result = broker_bp.broker_manager.connect(broker, credentials)
        
        if success:
            # Store broker in session
            session['broker'] = broker
            session['connected'] = True
            
            return jsonify({
                'success': True,
                'message': f'Connected to {broker} using saved credentials',
                'user_info': result.get('user_info', {})
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Connection failed')
            }), 400
            
    except Exception as e:
        logger.error(f"Error loading saved credentials: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@broker_bp.route('/credentials/delete/<broker>', methods=['DELETE'])
def delete_saved_credentials(broker):
    """
    Delete saved credentials for a broker
    
    Args:
        broker: Broker ID
        
    Returns:
        JSON response with deletion status
    """
    try:
        # Validate and sanitize broker parameter
        broker = sanitize_string(broker, max_length=50)
        is_valid, error = validate_broker_type(broker)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error
            }), 400
        
        if not broker_bp.credential_manager:
            return jsonify({
                'success': False,
                'error': 'Credential manager not available'
            }), 500
        
        success = broker_bp.credential_manager.delete_credentials(broker)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Deleted saved credentials for {broker}'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'No saved credentials found for {broker}'
            }), 404
            
    except Exception as e:
        logger.error(f"Error deleting saved credentials: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
