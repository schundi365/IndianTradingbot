"""
Bot Control API endpoints
"""

from flask import Blueprint, request, jsonify
import logging
from validators import (
    validate_json_request,
    validate_query_params,
    sanitize_string,
    validate_path_param_string
)
from rate_limiter import (
    READ_RATE_LIMIT,
    WRITE_RATE_LIMIT,
    STATUS_RATE_LIMIT
)

logger = logging.getLogger(__name__)

# Create blueprint
bot_bp = Blueprint('bot', __name__, url_prefix='/api/bot')


def init_bot_api(bot_controller, broker_manager):
    """
    Initialize bot API with dependencies
    
    Args:
        bot_controller: BotController instance
        broker_manager: BrokerManager instance
    """
    bot_bp.bot_controller = bot_controller
    bot_bp.broker_manager = broker_manager
    
    return bot_bp


def apply_rate_limits(limiter):
    """
    Apply rate limits to bot API endpoints.
    Called after limiter is initialized.
    
    Args:
        limiter: Flask-Limiter instance
    """
    limiter.limit(WRITE_RATE_LIMIT)(start_bot)
    limiter.limit(WRITE_RATE_LIMIT)(stop_bot)
    limiter.limit(WRITE_RATE_LIMIT)(restart_bot)
    limiter.limit(STATUS_RATE_LIMIT)(get_bot_status)
    limiter.limit(READ_RATE_LIMIT)(get_account_info)
    limiter.limit(READ_RATE_LIMIT)(get_positions)
    limiter.limit(WRITE_RATE_LIMIT)(close_position)
    limiter.limit(READ_RATE_LIMIT)(get_trades)
    limiter.limit(READ_RATE_LIMIT)(get_bot_config)


@bot_bp.route('/start', methods=['POST'])
@validate_json_request(required_fields=['config'])
def start_bot():
    """
    Start the trading bot
    
    Request body:
        {
            "config": {...}
        }
        
    Returns:
        JSON response with start status
    """
    try:
        data = request.get_json()
        config = data['config']
        
        # Validate config is a dict
        if not isinstance(config, dict):
            return jsonify({
                'success': False,
                'error': 'Configuration must be an object'
            }), 400
        
        # Check if broker is connected
        if not bot_bp.broker_manager.is_connected():
            return jsonify({
                'success': False,
                'error': 'Broker not connected'
            }), 400
        
        # Get broker adapter
        broker_adapter = bot_bp.broker_manager.get_adapter()
        
        # Start bot
        success, message = bot_bp.bot_controller.start(config, broker_adapter)
        
        if success:
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
        logger.error(f"Error starting bot: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bot_bp.route('/stop', methods=['POST'])
def stop_bot():
    """
    Stop the trading bot
    
    Returns:
        JSON response with stop status
    """
    try:
        success, message = bot_bp.bot_controller.stop()
        
        if success:
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
        logger.error(f"Error stopping bot: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bot_bp.route('/restart', methods=['POST'])
def restart_bot():
    """
    Restart the trading bot
    
    Returns:
        JSON response with restart status
    """
    try:
        success, message = bot_bp.bot_controller.restart()
        
        if success:
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
        logger.error(f"Error restarting bot: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bot_bp.route('/status', methods=['GET'])
def get_bot_status():
    """
    Get bot status
    
    Returns:
        JSON response with bot status
    """
    try:
        status = bot_bp.bot_controller.get_status()
        
        return jsonify({
            'success': True,
            'status': status
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting bot status: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bot_bp.route('/account', methods=['GET'])
def get_account_info():
    """
    Get account information
    
    Returns:
        JSON response with account info
    """
    try:
        account_info = bot_bp.bot_controller.get_account_info()
        
        if account_info:
            return jsonify({
                'success': True,
                'account': account_info
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Account information not available'
            }), 404
            
    except Exception as e:
        logger.error(f"Error getting account info: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bot_bp.route('/positions', methods=['GET'])
def get_positions():
    """
    Get current positions
    
    Returns:
        JSON response with positions
    """
    try:
        positions = bot_bp.bot_controller.get_positions()
        
        return jsonify({
            'success': True,
            'positions': positions,
            'count': len(positions)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting positions: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bot_bp.route('/positions/<symbol>', methods=['DELETE'])
def close_position(symbol):
    """
    Close a specific position
    
    Args:
        symbol: Trading symbol
        
    Returns:
        JSON response with close status
    """
    try:
        # Validate and sanitize symbol parameter
        symbol = sanitize_string(symbol, max_length=50)
        is_valid, error = validate_path_param_string(symbol, 'symbol', max_length=50)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error
            }), 400
        
        success, message = bot_bp.bot_controller.close_position(symbol)
        
        if success:
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
        logger.error(f"Error closing position: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bot_bp.route('/trades', methods=['GET'])
@validate_query_params({
    'from_date': {'type': 'string', 'max_length': 20, 'pattern': r'^\d{4}-\d{2}-\d{2}$'},
    'to_date': {'type': 'string', 'max_length': 20, 'pattern': r'^\d{4}-\d{2}-\d{2}$'}
})
def get_trades():
    """
    Get trade history
    
    Query parameters:
        - from_date: Start date (YYYY-MM-DD)
        - to_date: End date (YYYY-MM-DD)
        
    Returns:
        JSON response with trades
    """
    try:
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        trades = bot_bp.bot_controller.get_trades(from_date, to_date)
        
        return jsonify({
            'success': True,
            'trades': trades,
            'count': len(trades)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting trades: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bot_bp.route('/config', methods=['GET'])
def get_bot_config():
    """
    Get current bot configuration
    
    Returns:
        JSON response with bot config
    """
    try:
        config = bot_bp.bot_controller.get_bot_config()
        
        if config:
            return jsonify({
                'success': True,
                'config': config
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No bot configuration available'
            }), 404
            
    except Exception as e:
        logger.error(f"Error getting bot config: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
