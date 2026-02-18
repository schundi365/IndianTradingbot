"""
Input validation and sanitization utilities

This module provides comprehensive input validation and sanitization
to prevent XSS attacks and ensure data integrity across all API endpoints.
"""

import re
import html
from functools import wraps
from flask import request, jsonify
import logging
from typing import Any, Dict, List, Optional, Callable

logger = logging.getLogger(__name__)


# ============================================================================
# Sanitization Functions
# ============================================================================

def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize string input to prevent XSS attacks
    
    Args:
        value: Input string
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return str(value)
    
    # HTML escape to prevent XSS
    sanitized = html.escape(value.strip())
    
    # Truncate if max_length specified
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def sanitize_dict(data: Dict, schema: Dict) -> Dict:
    """
    Recursively sanitize dictionary based on schema
    
    Args:
        data: Input dictionary
        schema: Schema defining expected types and constraints
        
    Returns:
        Sanitized dictionary
    """
    sanitized = {}
    
    for key, value in data.items():
        # Skip keys not in schema
        if key not in schema:
            continue
        
        field_schema = schema[key]
        field_type = field_schema.get('type')
        
        if field_type == 'string':
            max_length = field_schema.get('max_length')
            sanitized[key] = sanitize_string(value, max_length)
        elif field_type == 'int':
            try:
                sanitized[key] = int(value)
            except (ValueError, TypeError):
                continue
        elif field_type == 'float':
            try:
                sanitized[key] = float(value)
            except (ValueError, TypeError):
                continue
        elif field_type == 'bool':
            sanitized[key] = bool(value)
        elif field_type == 'list':
            if isinstance(value, list):
                sanitized[key] = value
        elif field_type == 'dict':
            if isinstance(value, dict):
                nested_schema = field_schema.get('schema', {})
                if nested_schema:
                    sanitized[key] = sanitize_dict(value, nested_schema)
                else:
                    sanitized[key] = value
        else:
            sanitized[key] = value
    
    return sanitized


# ============================================================================
# Validation Functions
# ============================================================================

def validate_required_fields(data: Dict, required_fields: List[str]) -> tuple[bool, Optional[str]]:
    """
    Validate that all required fields are present
    
    Args:
        data: Input data
        required_fields: List of required field names
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    return True, None


def validate_string(value: Any, min_length: int = 0, max_length: int = 1000, 
                   pattern: Optional[str] = None) -> tuple[bool, Optional[str]]:
    """
    Validate string value
    
    Args:
        value: Value to validate
        min_length: Minimum length
        max_length: Maximum length
        pattern: Regex pattern to match
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(value, str):
        return False, "Value must be a string"
    
    if len(value) < min_length:
        return False, f"String must be at least {min_length} characters"
    
    if len(value) > max_length:
        return False, f"String must not exceed {max_length} characters"
    
    if pattern and not re.match(pattern, value):
        return False, f"String does not match required pattern"
    
    return True, None


def validate_number(value: Any, min_value: Optional[float] = None, 
                   max_value: Optional[float] = None) -> tuple[bool, Optional[str]]:
    """
    Validate numeric value
    
    Args:
        value: Value to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(value, (int, float)):
        try:
            value = float(value)
        except (ValueError, TypeError):
            return False, "Value must be a number"
    
    if min_value is not None and value < min_value:
        return False, f"Value must be at least {min_value}"
    
    if max_value is not None and value > max_value:
        return False, f"Value must not exceed {max_value}"
    
    return True, None


def validate_integer(value: Any, min_value: Optional[int] = None, 
                    max_value: Optional[int] = None) -> tuple[bool, Optional[str]]:
    """
    Validate integer value
    
    Args:
        value: Value to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(value, int):
        try:
            value = int(value)
        except (ValueError, TypeError):
            return False, "Value must be an integer"
    
    if min_value is not None and value < min_value:
        return False, f"Value must be at least {min_value}"
    
    if max_value is not None and value > max_value:
        return False, f"Value must not exceed {max_value}"
    
    return True, None


def validate_list(value: Any, min_items: int = 0, max_items: Optional[int] = None,
                 item_type: Optional[type] = None) -> tuple[bool, Optional[str]]:
    """
    Validate list value
    
    Args:
        value: Value to validate
        min_items: Minimum number of items
        max_items: Maximum number of items
        item_type: Expected type of items
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(value, list):
        return False, "Value must be a list"
    
    if len(value) < min_items:
        return False, f"List must contain at least {min_items} items"
    
    if max_items is not None and len(value) > max_items:
        return False, f"List must not exceed {max_items} items"
    
    if item_type:
        for item in value:
            if not isinstance(item, item_type):
                return False, f"All items must be of type {item_type.__name__}"
    
    return True, None


def validate_enum(value: Any, allowed_values: List[Any]) -> tuple[bool, Optional[str]]:
    """
    Validate that value is in allowed list
    
    Args:
        value: Value to validate
        allowed_values: List of allowed values
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if value not in allowed_values:
        return False, f"Value must be one of: {', '.join(map(str, allowed_values))}"
    
    return True, None


def validate_broker_type(broker: str) -> tuple[bool, Optional[str]]:
    """
    Validate broker type
    
    Args:
        broker: Broker identifier
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    allowed_brokers = ['kite', 'alice_blue', 'angel_one', 'upstox', 'paper']
    return validate_enum(broker, allowed_brokers)


def validate_exchange(exchange: str) -> tuple[bool, Optional[str]]:
    """
    Validate exchange name
    
    Args:
        exchange: Exchange identifier
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    allowed_exchanges = ['NSE', 'BSE', 'NFO', 'BFO', 'MCX', 'CDS']
    return validate_enum(exchange, allowed_exchanges)


def validate_instrument_type(instrument_type: str) -> tuple[bool, Optional[str]]:
    """
    Validate instrument type
    
    Args:
        instrument_type: Instrument type identifier
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    allowed_types = ['EQ', 'FUT', 'CE', 'PE', 'IDX']
    return validate_enum(instrument_type, allowed_types)


def validate_timeframe(timeframe: str) -> tuple[bool, Optional[str]]:
    """
    Validate timeframe
    
    Args:
        timeframe: Timeframe identifier
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    allowed_timeframes = ['1min', '3min', '5min', '10min', '15min', '30min', 
                         '1hour', '1day', '1week', '1month']
    return validate_enum(timeframe, allowed_timeframes)


def validate_strategy(strategy: str) -> tuple[bool, Optional[str]]:
    """
    Validate strategy name
    
    Args:
        strategy: Strategy identifier
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Allow alphanumeric, underscore, hyphen
    if not re.match(r'^[a-zA-Z0-9_-]+$', strategy):
        return False, "Strategy name must contain only letters, numbers, underscores, and hyphens"
    
    return validate_string(strategy, min_length=1, max_length=50)


def validate_risk_percentage(risk: float) -> tuple[bool, Optional[str]]:
    """
    Validate risk percentage
    
    Args:
        risk: Risk percentage value
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    return validate_number(risk, min_value=0.01, max_value=100)


def validate_config_name(name: str) -> tuple[bool, Optional[str]]:
    """
    Validate configuration name
    
    Args:
        name: Configuration name
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Allow alphanumeric, underscore, hyphen, space
    if not re.match(r'^[a-zA-Z0-9_\- ]+$', name):
        return False, "Name must contain only letters, numbers, spaces, underscores, and hyphens"
    
    return validate_string(name, min_length=1, max_length=100)


# ============================================================================
# Validation Decorators
# ============================================================================

def validate_json_request(required_fields: Optional[List[str]] = None):
    """
    Decorator to validate JSON request body
    
    Args:
        required_fields: List of required field names
        
    Returns:
        Decorated function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check content type
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Content-Type must be application/json'
                }), 400
            
            # Get JSON data
            try:
                data = request.get_json()
            except Exception as e:
                logger.error(f"Invalid JSON: {e}")
                return jsonify({
                    'success': False,
                    'error': 'Invalid JSON format'
                }), 400
            
            if data is None:
                return jsonify({
                    'success': False,
                    'error': 'Request body is empty'
                }), 400
            
            # Validate required fields
            if required_fields:
                is_valid, error = validate_required_fields(data, required_fields)
                if not is_valid:
                    return jsonify({
                        'success': False,
                        'error': error
                    }), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def validate_query_params(param_schema: Dict):
    """
    Decorator to validate query parameters
    
    Args:
        param_schema: Schema defining parameter constraints
        
    Returns:
        Decorated function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            errors = []
            
            for param_name, constraints in param_schema.items():
                value = request.args.get(param_name)
                
                # Check if required
                if constraints.get('required', False) and value is None:
                    errors.append(f"Missing required parameter: {param_name}")
                    continue
                
                # Skip validation if optional and not provided
                if value is None:
                    continue
                
                # Validate based on type
                param_type = constraints.get('type', 'string')
                
                if param_type == 'string':
                    is_valid, error = validate_string(
                        value,
                        min_length=constraints.get('min_length', 0),
                        max_length=constraints.get('max_length', 1000),
                        pattern=constraints.get('pattern')
                    )
                    if not is_valid:
                        errors.append(f"{param_name}: {error}")
                
                elif param_type == 'int':
                    try:
                        int_value = int(value)
                        is_valid, error = validate_integer(
                            int_value,
                            min_value=constraints.get('min_value'),
                            max_value=constraints.get('max_value')
                        )
                        if not is_valid:
                            errors.append(f"{param_name}: {error}")
                    except ValueError:
                        errors.append(f"{param_name}: Must be an integer")
                
                elif param_type == 'enum':
                    allowed = constraints.get('allowed_values', [])
                    is_valid, error = validate_enum(value, allowed)
                    if not is_valid:
                        errors.append(f"{param_name}: {error}")
            
            if errors:
                return jsonify({
                    'success': False,
                    'error': 'Validation failed',
                    'details': errors
                }), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def sanitize_request_data(schema: Dict):
    """
    Decorator to sanitize request data
    
    Args:
        schema: Schema defining sanitization rules
        
    Returns:
        Decorated function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.is_json:
                try:
                    data = request.get_json()
                    if data and isinstance(data, dict):
                        # Sanitize data
                        sanitized_data = sanitize_dict(data, schema)
                        # Replace request data
                        request._cached_json = (sanitized_data, sanitized_data)
                except Exception as e:
                    logger.error(f"Error sanitizing request data: {e}")
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


# ============================================================================
# Path Parameter Validation
# ============================================================================

def validate_path_param_string(value: str, param_name: str, 
                               max_length: int = 100) -> tuple[bool, Optional[str]]:
    """
    Validate path parameter string
    
    Args:
        value: Parameter value
        param_name: Parameter name for error messages
        max_length: Maximum allowed length
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not value:
        return False, f"{param_name} cannot be empty"
    
    # Sanitize
    sanitized = sanitize_string(value, max_length)
    
    # Check for path traversal attempts
    if '..' in sanitized or '/' in sanitized or '\\' in sanitized:
        return False, f"Invalid {param_name}: path traversal not allowed"
    
    return True, None


def validate_path_param_int(value: Any, param_name: str,
                           min_value: int = 0) -> tuple[bool, Optional[str]]:
    """
    Validate path parameter integer
    
    Args:
        value: Parameter value
        param_name: Parameter name for error messages
        min_value: Minimum allowed value
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        int_value = int(value)
        if int_value < min_value:
            return False, f"{param_name} must be at least {min_value}"
        return True, None
    except (ValueError, TypeError):
        return False, f"{param_name} must be a valid integer"
