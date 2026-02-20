"""
Analytics API endpoints
Provides performance metrics and statistics
"""

from flask import Blueprint, request, jsonify
import logging
from validators import validate_query_params, sanitize_string
from rate_limiter import READ_RATE_LIMIT

logger = logging.getLogger(__name__)

# Create blueprint
analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')


def init_analytics_api(bot_controller, analytics_service):
    """
    Initialize analytics API with dependencies
    
    Args:
        bot_controller: BotController instance
        analytics_service: AnalyticsService instance
    """
    analytics_bp.bot_controller = bot_controller
    analytics_bp.analytics_service = analytics_service
    
    return analytics_bp


def apply_rate_limits(limiter):
    """
    Apply rate limits to analytics API endpoints
    
    Args:
        limiter: Flask-Limiter instance
    """
    limiter.limit(READ_RATE_LIMIT)(get_performance_metrics)
    limiter.limit(READ_RATE_LIMIT)(get_profit_by_symbol)
    limiter.limit(READ_RATE_LIMIT)(get_win_loss_by_symbol)
    limiter.limit(READ_RATE_LIMIT)(get_daily_profit)
    limiter.limit(READ_RATE_LIMIT)(get_hourly_performance)
    limiter.limit(READ_RATE_LIMIT)(get_trade_distribution)
    limiter.limit(READ_RATE_LIMIT)(get_drawdown_data)
    limiter.limit(READ_RATE_LIMIT)(get_risk_metrics)


@analytics_bp.route('/performance', methods=['GET'])
@validate_query_params({
    'from_date': {'type': 'string', 'max_length': 20, 'pattern': r'^\d{4}-\d{2}-\d{2}$'},
    'to_date': {'type': 'string', 'max_length': 20, 'pattern': r'^\d{4}-\d{2}-\d{2}$'}
})
def get_performance_metrics():
    """
    Get overall performance metrics
    
    Query params:
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)
        
    Returns:
        JSON with performance metrics
    """
    try:
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        # Get trades from bot controller
        trades = analytics_bp.bot_controller.get_trades(from_date, to_date)
        
        # Calculate metrics
        metrics = analytics_bp.analytics_service.get_performance_metrics(
            trades, from_date, to_date
        )
        
        return jsonify({
            'success': True,
            'metrics': metrics
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analytics_bp.route('/profit-by-symbol', methods=['GET'])
@validate_query_params({
    'from_date': {'type': 'string', 'max_length': 20, 'pattern': r'^\d{4}-\d{2}-\d{2}$'},
    'to_date': {'type': 'string', 'max_length': 20, 'pattern': r'^\d{4}-\d{2}-\d{2}$'}
})
def get_profit_by_symbol():
    """
    Get profit/loss by symbol
    
    Query params:
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)
        
    Returns:
        JSON with profit by symbol data
    """
    try:
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        trades = analytics_bp.bot_controller.get_trades(from_date, to_date)
        
        data = analytics_bp.analytics_service.get_profit_by_symbol(
            trades, from_date, to_date
        )
        
        return jsonify({
            'success': True,
            'data': data
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting profit by symbol: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analytics_bp.route('/win-loss-by-symbol', methods=['GET'])
@validate_query_params({
    'from_date': {'type': 'string', 'max_length': 20, 'pattern': r'^\d{4}-\d{2}-\d{2}$'},
    'to_date': {'type': 'string', 'max_length': 20, 'pattern': r'^\d{4}-\d{2}-\d{2}$'}
})
def get_win_loss_by_symbol():
    """
    Get win/loss count by symbol
    
    Query params:
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)
        
    Returns:
        JSON with win/loss by symbol data
    """
    try:
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        trades = analytics_bp.bot_controller.get_trades(from_date, to_date)
        
        data = analytics_bp.analytics_service.get_win_loss_by_symbol(
            trades, from_date, to_date
        )
        
        return jsonify({
            'success': True,
            'data': data
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting win/loss by symbol: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analytics_bp.route('/daily-profit', methods=['GET'])
@validate_query_params({
    'from_date': {'type': 'string', 'max_length': 20, 'pattern': r'^\d{4}-\d{2}-\d{2}$'},
    'to_date': {'type': 'string', 'max_length': 20, 'pattern': r'^\d{4}-\d{2}-\d{2}$'}
})
def get_daily_profit():
    """
    Get daily profit/loss trend
    
    Query params:
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)
        
    Returns:
        JSON with daily profit data
    """
    try:
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        trades = analytics_bp.bot_controller.get_trades(from_date, to_date)
        
        data = analytics_bp.analytics_service.get_daily_profit(
            trades, from_date, to_date
        )
        
        return jsonify({
            'success': True,
            'data': data
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting daily profit: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analytics_bp.route('/hourly-performance', methods=['GET'])
@validate_query_params({
    'from_date': {'type': 'string', 'max_length': 20, 'pattern': r'^\d{4}-\d{2}-\d{2}$'},
    'to_date': {'type': 'string', 'max_length': 20, 'pattern': r'^\d{4}-\d{2}-\d{2}$'}
})
def get_hourly_performance():
    """
    Get hourly performance data
    
    Query params:
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)
        
    Returns:
        JSON with hourly performance data
    """
    try:
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        trades = analytics_bp.bot_controller.get_trades(from_date, to_date)
        
        data = analytics_bp.analytics_service.get_hourly_performance(
            trades, from_date, to_date
        )
        
        return jsonify({
            'success': True,
            'data': data
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting hourly performance: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analytics_bp.route('/trade-distribution', methods=['GET'])
@validate_query_params({
    'from_date': {'type': 'string', 'max_length': 20, 'pattern': r'^\d{4}-\d{2}-\d{2}$'},
    'to_date': {'type': 'string', 'max_length': 20, 'pattern': r'^\d{4}-\d{2}-\d{2}$'}
})
def get_trade_distribution():
    """
    Get trade distribution by symbol
    
    Query params:
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)
        
    Returns:
        JSON with trade distribution data
    """
    try:
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        trades = analytics_bp.bot_controller.get_trades(from_date, to_date)
        
        data = analytics_bp.analytics_service.get_trade_distribution(
            trades, from_date, to_date
        )
        
        return jsonify({
            'success': True,
            'data': data
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting trade distribution: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analytics_bp.route('/drawdown', methods=['GET'])
@validate_query_params({
    'from_date': {'type': 'string', 'max_length': 20, 'pattern': r'^\d{4}-\d{2}-\d{2}$'},
    'to_date': {'type': 'string', 'max_length': 20, 'pattern': r'^\d{4}-\d{2}-\d{2}$'}
})
def get_drawdown_data():
    """
    Get drawdown analysis
    
    Query params:
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)
        
    Returns:
        JSON with drawdown data
    """
    try:
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        trades = analytics_bp.bot_controller.get_trades(from_date, to_date)
        
        data = analytics_bp.analytics_service.get_drawdown_data(
            trades, from_date, to_date
        )
        
        return jsonify({
            'success': True,
            'data': data
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting drawdown data: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analytics_bp.route('/risk-metrics', methods=['GET'])
@validate_query_params({
    'from_date': {'type': 'string', 'max_length': 20, 'pattern': r'^\d{4}-\d{2}-\d{2}$'},
    'to_date': {'type': 'string', 'max_length': 20, 'pattern': r'^\d{4}-\d{2}-\d{2}$'}
})
def get_risk_metrics():
    """
    Get risk metrics
    
    Query params:
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)
        
    Returns:
        JSON with risk metrics
    """
    try:
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        trades = analytics_bp.bot_controller.get_trades(from_date, to_date)
        
        data = analytics_bp.analytics_service.get_risk_metrics(
            trades, from_date, to_date
        )
        
        return jsonify({
            'success': True,
            'data': data
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting risk metrics: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
