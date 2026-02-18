"""
Instruments API endpoints
"""

from flask import Blueprint, request, jsonify
import logging
from validators import (
    validate_query_params,
    validate_path_param_int,
    sanitize_string
)
from rate_limiter import (
    READ_RATE_LIMIT,
    EXPENSIVE_RATE_LIMIT
)

logger = logging.getLogger(__name__)

# Create blueprint
instruments_bp = Blueprint('instruments', __name__, url_prefix='/api/instruments')


def init_instruments_api(broker_manager, instrument_service):
    """
    Initialize instruments API with dependencies
    
    Args:
        broker_manager: BrokerManager instance
        instrument_service: InstrumentService instance
    """
    instruments_bp.broker_manager = broker_manager
    instruments_bp.instrument_service = instrument_service
    
    return instruments_bp


def apply_rate_limits(limiter):
    """
    Apply rate limits to instruments API endpoints.
    Called after limiter is initialized.
    
    Args:
        limiter: Flask-Limiter instance
    """
    limiter.limit(READ_RATE_LIMIT)(get_instruments)
    limiter.limit(EXPENSIVE_RATE_LIMIT)(refresh_instruments)
    limiter.limit(READ_RATE_LIMIT)(get_instrument_by_token)
    limiter.limit(READ_RATE_LIMIT)(get_quote)
    limiter.limit(READ_RATE_LIMIT)(get_cache_info)


@instruments_bp.route('', methods=['GET'])
@validate_query_params({
    'search': {'type': 'string', 'max_length': 100},
    'exchange': {'type': 'string', 'max_length': 100},
    'instrument_type': {'type': 'string', 'max_length': 100},
    'segment': {'type': 'string', 'max_length': 100}
})
def get_instruments():
    """
    Get instruments with optional filtering
    
    Query parameters:
        - search: Search query
        - exchange: Exchange filter (comma-separated)
        - instrument_type: Type filter (comma-separated)
        - segment: Segment filter (comma-separated)
        
    Returns:
        JSON response with instruments
    """
    try:
        # Check if broker is connected
        if not instruments_bp.broker_manager.is_connected():
            return jsonify({
                'success': False,
                'error': 'Broker not connected'
            }), 400
        
        broker_adapter = instruments_bp.broker_manager.get_adapter()
        broker_type = instruments_bp.broker_manager.get_broker_type()
        
        # Get instruments (with caching)
        instruments = instruments_bp.instrument_service.get_instruments(
            broker_adapter, 
            broker_type
        )
        
        # Apply search if provided (sanitized by decorator)
        search_query = request.args.get('search', '').strip()
        if search_query:
            instruments = instruments_bp.instrument_service.search_instruments(
                instruments, 
                search_query
            )
        
        # Apply filters if provided (sanitized by decorator)
        filters = {}
        if request.args.get('exchange'):
            # Split and sanitize each value
            exchanges = [sanitize_string(e.strip(), 10) for e in request.args.get('exchange').split(',')]
            filters['exchange'] = exchanges
        if request.args.get('instrument_type'):
            types = [sanitize_string(t.strip(), 10) for t in request.args.get('instrument_type').split(',')]
            filters['instrument_type'] = types
        if request.args.get('segment'):
            segments = [sanitize_string(s.strip(), 20) for s in request.args.get('segment').split(',')]
            filters['segment'] = segments
        
        if filters:
            instruments = instruments_bp.instrument_service.filter_instruments(
                instruments, 
                filters
            )
        
        # Get cache info
        cache_info = instruments_bp.instrument_service.get_cache_info(broker_type)
        
        return jsonify({
            'success': True,
            'instruments': instruments,
            'count': len(instruments),
            'cache_info': cache_info
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting instruments: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@instruments_bp.route('/refresh', methods=['POST'])
def refresh_instruments():
    """
    Force refresh instruments from broker
    
    Returns:
        JSON response with refreshed instruments
    """
    try:
        # Check if broker is connected
        if not instruments_bp.broker_manager.is_connected():
            return jsonify({
                'success': False,
                'error': 'Broker not connected'
            }), 400
        
        broker_adapter = instruments_bp.broker_manager.get_adapter()
        broker_type = instruments_bp.broker_manager.get_broker_type()
        
        # Force refresh
        instruments = instruments_bp.instrument_service.refresh_instruments(
            broker_adapter, 
            broker_type
        )
        
        return jsonify({
            'success': True,
            'message': 'Instruments refreshed',
            'count': len(instruments)
        }), 200
        
    except Exception as e:
        logger.error(f"Error refreshing instruments: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@instruments_bp.route('/<int:token>', methods=['GET'])
def get_instrument_by_token(token):
    """
    Get instrument by token
    
    Args:
        token: Instrument token
        
    Returns:
        JSON response with instrument details
    """
    try:
        # Validate token parameter
        is_valid, error = validate_path_param_int(token, 'token', min_value=0)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error
            }), 400
        
        # Check if broker is connected
        if not instruments_bp.broker_manager.is_connected():
            return jsonify({
                'success': False,
                'error': 'Broker not connected'
            }), 400
        
        broker_adapter = instruments_bp.broker_manager.get_adapter()
        broker_type = instruments_bp.broker_manager.get_broker_type()
        
        # Get all instruments
        instruments = instruments_bp.instrument_service.get_instruments(
            broker_adapter, 
            broker_type
        )
        
        # Find by token
        instrument = instruments_bp.instrument_service.get_instrument_by_token(
            instruments, 
            token
        )
        
        if instrument:
            return jsonify({
                'success': True,
                'instrument': instrument
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Instrument not found'
            }), 404
            
    except Exception as e:
        logger.error(f"Error getting instrument: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@instruments_bp.route('/quote/<symbol>', methods=['GET'])
def get_quote(symbol):
    """
    Get real-time quote for symbol
    
    Args:
        symbol: Trading symbol
        
    Returns:
        JSON response with quote data
    """
    try:
        # Validate and sanitize symbol parameter
        symbol = sanitize_string(symbol, max_length=50)
        if not symbol or len(symbol) < 1:
            return jsonify({
                'success': False,
                'error': 'Invalid symbol'
            }), 400
        
        # Check if broker is connected
        if not instruments_bp.broker_manager.is_connected():
            return jsonify({
                'success': False,
                'error': 'Broker not connected'
            }), 400
        
        broker_adapter = instruments_bp.broker_manager.get_adapter()
        
        # Get quote from broker
        quote = broker_adapter.get_quote(symbol)
        
        if quote:
            return jsonify({
                'success': True,
                'symbol': symbol,
                'quote': quote
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Quote not available'
            }), 404
            
    except Exception as e:
        logger.error(f"Error getting quote: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@instruments_bp.route('/cache-info', methods=['GET'])
def get_cache_info():
    """
    Get cache information
    
    Returns:
        JSON response with cache info
    """
    try:
        broker_type = instruments_bp.broker_manager.get_broker_type()
        
        if not broker_type:
            return jsonify({
                'success': False,
                'error': 'No broker connected'
            }), 400
        
        cache_info = instruments_bp.instrument_service.get_cache_info(broker_type)
        
        return jsonify({
            'success': True,
            'cache_info': cache_info
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting cache info: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
