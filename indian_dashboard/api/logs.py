"""
Log Management API endpoints
"""

import csv
import io
import logging
from flask import Blueprint, request, jsonify, send_file
from validators import (
    validate_json_request,
    validate_query_params,
    sanitize_string
)
from rate_limiter import (
    READ_RATE_LIMIT,
    WRITE_RATE_LIMIT
)

logger = logging.getLogger(__name__)

# Create blueprint
logs_bp = Blueprint('logs', __name__, url_prefix='/api/logs')


def init_logs_api(db_manager):
    """
    Initialize logs API with database manager
    
    Args:
        db_manager: LogDatabaseManager instance
    """
    logs_bp.db_manager = db_manager
    return logs_bp


def apply_rate_limits(limiter):
    """
    Apply rate limits to logs API endpoints.
    
    Args:
        limiter: Flask-Limiter instance
    """
    limiter.limit(READ_RATE_LIMIT)(get_logs)
    limiter.limit(WRITE_RATE_LIMIT)(set_log_level)
    limiter.limit(READ_RATE_LIMIT)(download_logs)
    limiter.limit(WRITE_RATE_LIMIT)(clear_logs)


@logs_bp.route('/', methods=['GET'])
@logs_bp.route('', methods=['GET'])
@validate_query_params({
    'limit': {'type': 'int', 'min': 1, 'max': 1000},
    'offset': {'type': 'int', 'min': 0},
    'level': {'type': 'string', 'max_length': 20},
    'search': {'type': 'string', 'max_length': 100},
    'symbol': {'type': 'string', 'max_length': 50}
})
def get_logs():
    """
    Retrieve logs from database
    """
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        level = request.args.get('level', None)
        search = request.args.get('search', None)
        symbol = request.args.get('symbol', None)
        
        logs = logs_bp.db_manager.get_logs(
            limit=limit,
            offset=offset,
            level=level,
            search=search,
            symbol=symbol
        )
        
        total_count = logs_bp.db_manager.get_log_count(
            level=level,
            search=search,
            symbol=symbol
        )
        
        return jsonify({
            'success': True,
            'logs': logs,
            'total': total_count,
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching logs: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@logs_bp.route('/level', methods=['POST'])
@validate_json_request(required_fields=['level'])
def set_log_level():
    """
    Set global logging level
    """
    try:
        data = request.get_json()
        level_name = data['level'].upper()
        
        # Validate level
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if level_name not in valid_levels:
            return jsonify({
                'success': False,
                'error': f'Invalid log level. Must be one of: {", ".join(valid_levels)}'
            }), 400
            
        # Set root logger level
        logging.getLogger().setLevel(getattr(logging, level_name))
        
        logger.info(f"Global logging level changed to {level_name} via dashboard")
        
        return jsonify({
            'success': True,
            'message': f'Logging level set to {level_name}'
        }), 200
        
    except Exception as e:
        logger.error(f"Error setting log level: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@logs_bp.route('/download', methods=['GET'])
def download_logs():
    """
    Download logs as CSV
    """
    try:
        level = request.args.get('level', None)
        search = request.args.get('search', None)
        symbol = request.args.get('symbol', None)
        
        # Fetch a larger limit for download
        logs = logs_bp.db_manager.get_logs(
            limit=5000,
            level=level,
            search=search,
            symbol=symbol
        )
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=['id', 'timestamp', 'level', 'logger_name', 'message', 'symbol', 'level_no'])
        writer.writeheader()
        writer.writerows(logs)
        
        output.seek(0)
        
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"bot_logs_{sanitize_string(level or 'ALL')}.csv"
        )
        
    except Exception as e:
        logger.error(f"Error downloading logs: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@logs_bp.route('/clear', methods=['POST'])
def clear_logs():
    """
    Clear all logs from database
    """
    try:
        logs_bp.db_manager.clear_logs()
        logger.info("Log database cleared via dashboard")
        
        return jsonify({
            'success': True,
            'message': 'Log database cleared'
        }), 200
        
    except Exception as e:
        logger.error(f"Error clearing logs: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
