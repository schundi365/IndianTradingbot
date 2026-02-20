"""
Charts API endpoints
Provides historical price data and indicators for charting
"""

from flask import Blueprint, request, jsonify
import logging
from validators import validate_query_params, sanitize_string, validate_path_param_string
from rate_limiter import READ_RATE_LIMIT

logger = logging.getLogger(__name__)

# Create blueprint
charts_bp = Blueprint('charts', __name__, url_prefix='/api/charts')


def init_charts_api(bot_controller, chart_data_service):
    """
    Initialize charts API with dependencies
    
    Args:
        bot_controller: BotController instance
        chart_data_service: ChartDataService instance
    """
    charts_bp.bot_controller = bot_controller
    charts_bp.chart_data_service = chart_data_service
    
    return charts_bp


def apply_rate_limits(limiter):
    """
    Apply rate limits to charts API endpoints
    
    Args:
        limiter: Flask-Limiter instance
    """
    limiter.limit(READ_RATE_LIMIT)(get_price_data)
    limiter.limit(READ_RATE_LIMIT)(get_indicator_data)
    limiter.limit(READ_RATE_LIMIT)(get_trade_markers)


@charts_bp.route('/price-data/<symbol>', methods=['GET'])
@validate_query_params({
    'timeframe': {'type': 'string', 'max_length': 10},
    'bars': {'type': 'integer', 'min': 1, 'max': 1000},
    'indicators': {'type': 'string', 'max_length': 200}
})
def get_price_data(symbol):
    """
    Get historical price data with optional indicators
    
    Path params:
        symbol: Trading symbol
        
    Query params:
        timeframe: Timeframe (1min, 5min, 15min, 1h, 1d) - default 15min
        bars: Number of bars (1-1000) - default 200
        indicators: Comma-separated list of indicators (ma,macd,rsi,atr,bollinger)
        
    Returns:
        JSON with OHLCV data and indicators
    """
    try:
        # Validate and sanitize symbol
        symbol = sanitize_string(symbol, max_length=50)
        is_valid, error = validate_path_param_string(symbol, 'symbol', max_length=50)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error
            }), 400
        
        # Get query parameters
        timeframe = request.args.get('timeframe', '15min')
        bars = request.args.get('bars', 200, type=int)
        indicators_str = request.args.get('indicators', '')
        
        # Parse indicators
        indicators = []
        if indicators_str:
            indicators = [i.strip() for i in indicators_str.split(',') if i.strip()]
        
        # Get price data
        data = charts_bp.chart_data_service.get_price_data(
            symbol=symbol,
            timeframe=timeframe,
            bars=bars,
            indicators=indicators
        )
        
        if 'error' in data:
            return jsonify({
                'success': False,
                'error': data['error']
            }), 400
        
        return jsonify({
            'success': True,
            'data': data
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting price data: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@charts_bp.route('/indicator-data/<symbol>/<indicator>', methods=['GET'])
@validate_query_params({
    'timeframe': {'type': 'string', 'max_length': 10},
    'bars': {'type': 'integer', 'min': 1, 'max': 1000},
    'period': {'type': 'integer', 'min': 1, 'max': 200},
    'fast': {'type': 'integer', 'min': 1, 'max': 100},
    'slow': {'type': 'integer', 'min': 1, 'max': 100},
    'signal': {'type': 'integer', 'min': 1, 'max': 100},
    'std_dev': {'type': 'integer', 'min': 1, 'max': 5}
})
def get_indicator_data(symbol, indicator):
    """
    Get specific indicator data
    
    Path params:
        symbol: Trading symbol
        indicator: Indicator name (ma, ema, macd, rsi, atr, bollinger)
        
    Query params:
        timeframe: Timeframe - default 15min
        bars: Number of bars - default 200
        period: Indicator period (for MA, RSI, ATR, Bollinger)
        fast: MACD fast period
        slow: MACD slow period
        signal: MACD signal period
        std_dev: Bollinger Bands standard deviation
        
    Returns:
        JSON with indicator data
    """
    try:
        # Validate and sanitize
        symbol = sanitize_string(symbol, max_length=50)
        indicator = sanitize_string(indicator, max_length=20)
        
        is_valid, error = validate_path_param_string(symbol, 'symbol', max_length=50)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error
            }), 400
        
        # Get query parameters
        timeframe = request.args.get('timeframe', '15min')
        bars = request.args.get('bars', 200, type=int)
        
        # Get indicator parameters
        params = {}
        if request.args.get('period'):
            params['period'] = request.args.get('period', type=int)
        if request.args.get('fast'):
            params['fast'] = request.args.get('fast', type=int)
        if request.args.get('slow'):
            params['slow'] = request.args.get('slow', type=int)
        if request.args.get('signal'):
            params['signal'] = request.args.get('signal', type=int)
        if request.args.get('std_dev'):
            params['std_dev'] = request.args.get('std_dev', type=int)
        
        # Get indicator data
        data = charts_bp.chart_data_service.get_indicator_data(
            symbol=symbol,
            indicator=indicator,
            timeframe=timeframe,
            bars=bars,
            params=params
        )
        
        if 'error' in data:
            return jsonify({
                'success': False,
                'error': data['error']
            }), 400
        
        return jsonify({
            'success': True,
            'data': data
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting indicator data: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@charts_bp.route('/trade-markers/<symbol>', methods=['GET'])
@validate_query_params({
    'from_date': {'type': 'string', 'max_length': 20, 'pattern': r'^\d{4}-\d{2}-\d{2}$'},
    'to_date': {'type': 'string', 'max_length': 20, 'pattern': r'^\d{4}-\d{2}-\d{2}$'}
})
def get_trade_markers(symbol):
    """
    Get trade entry/exit markers for chart overlay
    
    Path params:
        symbol: Trading symbol
        
    Query params:
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)
        
    Returns:
        JSON with trade markers
    """
    try:
        # Validate and sanitize symbol
        symbol = sanitize_string(symbol, max_length=50)
        is_valid, error = validate_path_param_string(symbol, 'symbol', max_length=50)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error
            }), 400
        
        # Get query parameters
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        # Get trades for this symbol
        all_trades = charts_bp.bot_controller.get_trades(from_date, to_date)
        symbol_trades = [t for t in all_trades if t.get('symbol') == symbol]
        
        # Get trade markers
        markers = charts_bp.chart_data_service.get_trade_markers(symbol, symbol_trades)
        
        return jsonify({
            'success': True,
            'markers': markers
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting trade markers: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
