"""
Configuration API endpoints
"""

from flask import Blueprint, request, jsonify
import logging
import json
from pathlib import Path
from validators import (
    validate_json_request,
    sanitize_request_data,
    validate_config_name,
    validate_path_param_string,
    sanitize_string,
    validate_required_fields,
    validate_list,
    validate_risk_percentage,
    validate_integer,
    validate_number,
    validate_strategy,
    validate_timeframe,
    validate_broker_type
)
from rate_limiter import (
    READ_RATE_LIMIT,
    WRITE_RATE_LIMIT
)

logger = logging.getLogger(__name__)

# Create blueprint
config_bp = Blueprint('config', __name__, url_prefix='/api/config')


def init_config_api(config_dir, preset_configs):
    """
    Initialize config API with dependencies
    
    Args:
        config_dir: Directory to store configurations
        preset_configs: Dictionary of preset configurations
    """
    config_bp.config_dir = Path(config_dir)
    config_bp.config_dir.mkdir(parents=True, exist_ok=True)
    config_bp.preset_configs = preset_configs
    
    return config_bp


def apply_rate_limits(limiter):
    """
    Apply rate limits to config API endpoints.
    Called after limiter is initialized.
    
    Args:
        limiter: Flask-Limiter instance
    """
    limiter.limit(READ_RATE_LIMIT)(get_current_config)
    limiter.limit(WRITE_RATE_LIMIT)(save_current_config)
    limiter.limit(READ_RATE_LIMIT)(list_configs)
    limiter.limit(READ_RATE_LIMIT)(get_config)
    limiter.limit(WRITE_RATE_LIMIT)(delete_config)
    limiter.limit(READ_RATE_LIMIT)(get_presets)
    limiter.limit(WRITE_RATE_LIMIT)(validate_config)


@config_bp.route('', methods=['GET'])
def get_current_config():
    """
    Get current active configuration
    
    Returns:
        JSON response with current config
    """
    try:
        # Try to load last used config from session file
        session_file = config_bp.config_dir / '_current.json'
        
        if session_file.exists():
            with open(session_file, 'r') as f:
                config = json.load(f)
            
            return jsonify({
                'success': True,
                'config': config
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No active configuration'
            }), 404
            
    except Exception as e:
        logger.error(f"Error getting current config: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@config_bp.route('', methods=['POST'])
@validate_json_request(required_fields=['config'])
def save_current_config():
    """
    Save current configuration
    
    Request body:
        {
            "config": {...},
            "name": "optional_name"
        }
        
    Returns:
        JSON response with save status
    """
    try:
        data = request.get_json()
        
        config = data['config']
        name = data.get('name')
        
        # Log the config being saved for debugging
        logger.info(f"Saving configuration: {json.dumps(config, indent=2)}")
        
        # Validate config structure
        errors = validate_configuration(config)
        if errors:
            logger.error(f"Configuration validation failed: {errors}")
            return jsonify({
                'success': False,
                'error': 'Invalid configuration',
                'details': errors
            }), 400
        
        # Validate and sanitize name if provided
        if name:
            name = sanitize_string(name, max_length=100)
            is_valid, error = validate_config_name(name)
            if not is_valid:
                return jsonify({
                    'success': False,
                    'error': error
                }), 400
        
        # Save as current config
        session_file = config_bp.config_dir / '_current.json'
        with open(session_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # If name provided, also save as named config
        if name:
            config_file = config_bp.config_dir / f"{name}.json"
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            return jsonify({
                'success': True,
                'message': f'Configuration saved as "{name}"'
            }), 200
        else:
            return jsonify({
                'success': True,
                'message': 'Current configuration saved'
            }), 200
            
    except Exception as e:
        logger.error(f"Error saving config: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@config_bp.route('/list', methods=['GET'])
def list_configs():
    """
    List all saved configurations
    
    Returns:
        JSON response with list of configs
    """
    try:
        configs = []
        
        for config_file in config_bp.config_dir.glob('*.json'):
            # Skip current session file
            if config_file.name == '_current.json':
                continue
            
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                
                configs.append({
                    'name': config_file.stem,
                    'description': config_data.get('description', ''),
                    'broker': config_data.get('broker', ''),
                    'strategy': config_data.get('strategy', ''),
                    'instruments_count': len(config_data.get('instruments', []))
                })
            except Exception as e:
                logger.warning(f"Error reading config {config_file}: {e}")
                continue
        
        return jsonify({
            'success': True,
            'configs': configs
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing configs: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@config_bp.route('/<name>', methods=['GET'])
def get_config(name):
    """
    Get specific configuration by name
    
    Args:
        name: Configuration name
        
    Returns:
        JSON response with configuration
    """
    try:
        # Validate and sanitize name parameter
        name = sanitize_string(name, max_length=100)
        is_valid, error = validate_path_param_string(name, 'name', max_length=100)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error
            }), 400
        
        config_file = config_bp.config_dir / f"{name}.json"
        
        if not config_file.exists():
            return jsonify({
                'success': False,
                'error': f'Configuration "{name}" not found'
            }), 404
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        return jsonify({
            'success': True,
            'name': name,
            'config': config
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting config: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@config_bp.route('/<name>', methods=['DELETE'])
def delete_config(name):
    """
    Delete configuration by name
    
    Args:
        name: Configuration name
        
    Returns:
        JSON response with deletion status
    """
    try:
        # Validate and sanitize name parameter
        name = sanitize_string(name, max_length=100)
        is_valid, error = validate_path_param_string(name, 'name', max_length=100)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error
            }), 400
        
        config_file = config_bp.config_dir / f"{name}.json"
        
        if not config_file.exists():
            return jsonify({
                'success': False,
                'error': f'Configuration "{name}" not found'
            }), 404
        
        config_file.unlink()
        
        return jsonify({
            'success': True,
            'message': f'Configuration "{name}" deleted'
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting config: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@config_bp.route('/presets', methods=['GET'])
def get_presets():
    """
    Get available preset configurations
    
    Returns:
        JSON response with presets
    """
    try:
        presets = []
        
        for preset_id, preset_data in config_bp.preset_configs.items():
            presets.append({
                'id': preset_id,
                'name': preset_data.get('name', preset_id),
                'description': preset_data.get('description', ''),
                'strategy': preset_data.get('strategy', ''),
                'config': preset_data
            })
        
        return jsonify({
            'success': True,
            'presets': presets
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting presets: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@config_bp.route('/validate', methods=['POST'])
@validate_json_request(required_fields=['config'])
def validate_config():
    """
    Validate configuration
    
    Request body:
        {
            "config": {...}
        }
        
    Returns:
        JSON response with validation result
    """
    try:
        data = request.get_json()
        config = data['config']
        
        errors = validate_configuration(config)
        warnings = []
        
        # Warnings
        if config.get('risk_per_trade', 0) > 5:
            warnings.append('Risk per trade above 5% is considered high')
        
        if config.get('max_positions', 0) > 10:
            warnings.append('More than 10 positions may be difficult to manage')
        
        is_valid = len(errors) == 0
        
        return jsonify({
            'success': True,
            'valid': is_valid,
            'errors': errors,
            'warnings': warnings
        }), 200
        
    except Exception as e:
        logger.error(f"Error validating config: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def validate_configuration(config: dict) -> list:
    """
    Validate configuration structure and values
    
    Args:
        config: Configuration dictionary
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    # Validate required fields
    required_fields = ['broker', 'instruments', 'strategy', 'timeframe']
    is_valid, error = validate_required_fields(config, required_fields)
    if not is_valid:
        errors.append(error)
        return errors  # Can't continue without required fields
    
    # Validate broker
    is_valid, error = validate_broker_type(config.get('broker', ''))
    if not is_valid:
        errors.append(f"broker: {error}")
    
    # Validate instruments
    is_valid, error = validate_list(config.get('instruments', []), min_items=1)
    if not is_valid:
        errors.append(f"instruments: {error}")
    
    # Validate strategy
    is_valid, error = validate_strategy(config.get('strategy', ''))
    if not is_valid:
        errors.append(f"strategy: {error}")
    
    # Validate timeframe
    is_valid, error = validate_timeframe(config.get('timeframe', ''))
    if not is_valid:
        errors.append(f"timeframe: {error}")
    
    # Validate risk parameters
    if 'risk_per_trade' in config:
        is_valid, error = validate_risk_percentage(config['risk_per_trade'])
        if not is_valid:
            errors.append(f"risk_per_trade: {error}")
    
    if 'max_positions' in config:
        is_valid, error = validate_integer(config['max_positions'], min_value=1, max_value=100)
        if not is_valid:
            errors.append(f"max_positions: {error}")
    
    if 'max_daily_loss' in config:
        is_valid, error = validate_risk_percentage(config['max_daily_loss'])
        if not is_valid:
            errors.append(f"max_daily_loss: {error}")
            
    # Technical Indicator Validations
    if 'loop_interval' in config:
        is_valid, error = validate_integer(config['loop_interval'], min_value=1, max_value=300)
        if not is_valid:
            errors.append(f"loop_interval: {error}")
            
    if 'rsi_period' in config:
        is_valid, error = validate_integer(config['rsi_period'], min_value=2, max_value=100)
        if not is_valid:
            errors.append(f"rsi_period: {error}")
            
    if 'rsi_overbought' in config:
        is_valid, error = validate_number(config['rsi_overbought'], min_value=50, max_value=99)
        if not is_valid:
            errors.append(f"rsi_overbought: {error}")
            
    if 'rsi_oversold' in config:
        is_valid, error = validate_number(config['rsi_oversold'], min_value=1, max_value=50)
        if not is_valid:
            errors.append(f"rsi_oversold: {error}")
            
    if 'adx_period' in config:
        is_valid, error = validate_integer(config['adx_period'], min_value=2, max_value=100)
        if not is_valid:
            errors.append(f"adx_period: {error}")
            
    if 'adx_min_strength' in config:
        is_valid, error = validate_number(config['adx_min_strength'], min_value=0, max_value=100)
        if not is_valid:
            errors.append(f"adx_min_strength: {error}")
            
    if 'min_trend_confidence' in config:
        is_valid, error = validate_number(config['min_trend_confidence'], min_value=0, max_value=1)
        if not is_valid:
            errors.append(f"min_trend_confidence: {error}")
            
    if 'trend_detection_sensitivity' in config:
        is_valid, error = validate_integer(config['trend_detection_sensitivity'], min_value=1, max_value=10)
        if not is_valid:
            errors.append(f"trend_detection_sensitivity: {error}")
            
    if 'macd_min_histogram' in config:
        is_valid, error = validate_number(config['macd_min_histogram'], min_value=0, max_value=0.1)
        if not is_valid:
            errors.append(f"macd_min_histogram: {error}")
    
    if 'paper_trading_initial_balance' in config:
        is_valid, error = validate_number(config['paper_trading_initial_balance'], min_value=10000, max_value=100000000)
        if not is_valid:
            errors.append(f"paper_trading_initial_balance: {error}")
    
    if errors:
        logger.error(f"Validation errors found: {errors}")
        
    return errors
