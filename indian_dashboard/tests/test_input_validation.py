"""
Tests for input validation and sanitization

This test suite validates that all input validation and sanitization
functions work correctly to prevent XSS attacks and ensure data integrity.
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from indian_dashboard.validators import (
    sanitize_string,
    sanitize_dict,
    validate_required_fields,
    validate_string,
    validate_number,
    validate_integer,
    validate_list,
    validate_enum,
    validate_broker_type,
    validate_exchange,
    validate_instrument_type,
    validate_timeframe,
    validate_strategy,
    validate_risk_percentage,
    validate_config_name,
    validate_path_param_string,
    validate_path_param_int
)


class TestSanitization:
    """Test sanitization functions"""
    
    def test_sanitize_string_basic(self):
        """Test basic string sanitization"""
        result = sanitize_string("  hello world  ")
        assert result == "hello world"
    
    def test_sanitize_string_xss_script_tag(self):
        """Test XSS prevention with script tags"""
        malicious = "<script>alert('XSS')</script>"
        result = sanitize_string(malicious)
        assert "<script>" not in result
        assert "&lt;script&gt;" in result
    
    def test_sanitize_string_xss_img_tag(self):
        """Test XSS prevention with img tags"""
        malicious = "<img src=x onerror=alert('XSS')>"
        result = sanitize_string(malicious)
        assert "<img" not in result
        assert "&lt;img" in result
    
    def test_sanitize_string_xss_event_handler(self):
        """Test XSS prevention with event handlers"""
        malicious = "<div onclick='alert(1)'>Click</div>"
        result = sanitize_string(malicious)
        assert "onclick" not in result or "&lt;" in result
    
    def test_sanitize_string_max_length(self):
        """Test string truncation"""
        long_string = "a" * 1000
        result = sanitize_string(long_string, max_length=100)
        assert len(result) == 100
    
    def test_sanitize_string_special_chars(self):
        """Test special character escaping"""
        special = "Test & <test> 'quote' \"double\""
        result = sanitize_string(special)
        assert "&amp;" in result
        assert "&lt;" in result
        assert "&gt;" in result
    
    def test_sanitize_dict_basic(self):
        """Test dictionary sanitization"""
        schema = {
            'name': {'type': 'string', 'max_length': 50},
            'age': {'type': 'int'}
        }
        data = {
            'name': '<script>alert(1)</script>',
            'age': '25',
            'extra': 'ignored'
        }
        result = sanitize_dict(data, schema)
        assert '&lt;script&gt;' in result['name']
        assert result['age'] == 25
        assert 'extra' not in result
    
    def test_sanitize_dict_nested(self):
        """Test nested dictionary sanitization"""
        schema = {
            'user': {
                'type': 'dict',
                'schema': {
                    'name': {'type': 'string', 'max_length': 50}
                }
            }
        }
        data = {
            'user': {
                'name': '<b>Test</b>'
            }
        }
        result = sanitize_dict(data, schema)
        assert '&lt;b&gt;' in result['user']['name']


class TestValidationFunctions:
    """Test validation functions"""
    
    def test_validate_required_fields_success(self):
        """Test required fields validation - success"""
        data = {'name': 'test', 'age': 25}
        is_valid, error = validate_required_fields(data, ['name', 'age'])
        assert is_valid is True
        assert error is None
    
    def test_validate_required_fields_missing(self):
        """Test required fields validation - missing field"""
        data = {'name': 'test'}
        is_valid, error = validate_required_fields(data, ['name', 'age'])
        assert is_valid is False
        assert 'age' in error
    
    def test_validate_string_success(self):
        """Test string validation - success"""
        is_valid, error = validate_string("test", min_length=1, max_length=10)
        assert is_valid is True
        assert error is None
    
    def test_validate_string_too_short(self):
        """Test string validation - too short"""
        is_valid, error = validate_string("ab", min_length=5)
        assert is_valid is False
        assert "at least 5" in error
    
    def test_validate_string_too_long(self):
        """Test string validation - too long"""
        is_valid, error = validate_string("a" * 100, max_length=50)
        assert is_valid is False
        assert "not exceed 50" in error
    
    def test_validate_string_pattern(self):
        """Test string validation - pattern matching"""
        is_valid, error = validate_string("test123", pattern=r'^[a-z0-9]+$')
        assert is_valid is True
        
        is_valid, error = validate_string("test@123", pattern=r'^[a-z0-9]+$')
        assert is_valid is False
    
    def test_validate_number_success(self):
        """Test number validation - success"""
        is_valid, error = validate_number(50, min_value=0, max_value=100)
        assert is_valid is True
    
    def test_validate_number_too_small(self):
        """Test number validation - too small"""
        is_valid, error = validate_number(-5, min_value=0)
        assert is_valid is False
        assert "at least 0" in error
    
    def test_validate_number_too_large(self):
        """Test number validation - too large"""
        is_valid, error = validate_number(150, max_value=100)
        assert is_valid is False
        assert "not exceed 100" in error
    
    def test_validate_integer_success(self):
        """Test integer validation - success"""
        is_valid, error = validate_integer(10, min_value=1, max_value=100)
        assert is_valid is True
    
    def test_validate_integer_not_int(self):
        """Test integer validation - not an integer"""
        is_valid, error = validate_integer("abc")
        assert is_valid is False
        assert "integer" in error
    
    def test_validate_list_success(self):
        """Test list validation - success"""
        is_valid, error = validate_list([1, 2, 3], min_items=1, max_items=5)
        assert is_valid is True
    
    def test_validate_list_too_few(self):
        """Test list validation - too few items"""
        is_valid, error = validate_list([], min_items=1)
        assert is_valid is False
        assert "at least 1" in error
    
    def test_validate_list_too_many(self):
        """Test list validation - too many items"""
        is_valid, error = validate_list([1, 2, 3, 4, 5, 6], max_items=5)
        assert is_valid is False
        assert "not exceed 5" in error
    
    def test_validate_list_item_type(self):
        """Test list validation - item type checking"""
        is_valid, error = validate_list([1, 2, 3], item_type=int)
        assert is_valid is True
        
        is_valid, error = validate_list([1, "2", 3], item_type=int)
        assert is_valid is False
    
    def test_validate_enum_success(self):
        """Test enum validation - success"""
        is_valid, error = validate_enum("option1", ["option1", "option2"])
        assert is_valid is True
    
    def test_validate_enum_invalid(self):
        """Test enum validation - invalid value"""
        is_valid, error = validate_enum("option3", ["option1", "option2"])
        assert is_valid is False
        assert "option1" in error


class TestDomainValidators:
    """Test domain-specific validators"""
    
    def test_validate_broker_type_valid(self):
        """Test broker type validation - valid brokers"""
        for broker in ['kite', 'alice_blue', 'angel_one', 'upstox', 'paper']:
            is_valid, error = validate_broker_type(broker)
            assert is_valid is True, f"Broker {broker} should be valid"
    
    def test_validate_broker_type_invalid(self):
        """Test broker type validation - invalid broker"""
        is_valid, error = validate_broker_type("invalid_broker")
        assert is_valid is False
    
    def test_validate_exchange_valid(self):
        """Test exchange validation - valid exchanges"""
        for exchange in ['NSE', 'BSE', 'NFO', 'BFO', 'MCX', 'CDS']:
            is_valid, error = validate_exchange(exchange)
            assert is_valid is True, f"Exchange {exchange} should be valid"
    
    def test_validate_exchange_invalid(self):
        """Test exchange validation - invalid exchange"""
        is_valid, error = validate_exchange("INVALID")
        assert is_valid is False
    
    def test_validate_instrument_type_valid(self):
        """Test instrument type validation - valid types"""
        for inst_type in ['EQ', 'FUT', 'CE', 'PE', 'IDX']:
            is_valid, error = validate_instrument_type(inst_type)
            assert is_valid is True, f"Type {inst_type} should be valid"
    
    def test_validate_instrument_type_invalid(self):
        """Test instrument type validation - invalid type"""
        is_valid, error = validate_instrument_type("INVALID")
        assert is_valid is False
    
    def test_validate_timeframe_valid(self):
        """Test timeframe validation - valid timeframes"""
        for tf in ['1min', '5min', '15min', '1hour', '1day']:
            is_valid, error = validate_timeframe(tf)
            assert is_valid is True, f"Timeframe {tf} should be valid"
    
    def test_validate_timeframe_invalid(self):
        """Test timeframe validation - invalid timeframe"""
        is_valid, error = validate_timeframe("2sec")
        assert is_valid is False
    
    def test_validate_strategy_valid(self):
        """Test strategy validation - valid strategies"""
        for strategy in ['trend_following', 'mean-reversion', 'scalping123']:
            is_valid, error = validate_strategy(strategy)
            assert is_valid is True, f"Strategy {strategy} should be valid"
    
    def test_validate_strategy_invalid(self):
        """Test strategy validation - invalid characters"""
        is_valid, error = validate_strategy("strategy@123")
        assert is_valid is False
    
    def test_validate_risk_percentage_valid(self):
        """Test risk percentage validation - valid values"""
        for risk in [0.01, 1, 5, 50, 100]:
            is_valid, error = validate_risk_percentage(risk)
            assert is_valid is True, f"Risk {risk} should be valid"
    
    def test_validate_risk_percentage_invalid(self):
        """Test risk percentage validation - invalid values"""
        is_valid, error = validate_risk_percentage(0)
        assert is_valid is False
        
        is_valid, error = validate_risk_percentage(101)
        assert is_valid is False
    
    def test_validate_config_name_valid(self):
        """Test config name validation - valid names"""
        for name in ['my_config', 'config-1', 'Test Config 123']:
            is_valid, error = validate_config_name(name)
            assert is_valid is True, f"Name '{name}' should be valid"
    
    def test_validate_config_name_invalid(self):
        """Test config name validation - invalid characters"""
        is_valid, error = validate_config_name("config@123")
        assert is_valid is False


class TestPathParameterValidation:
    """Test path parameter validation"""
    
    def test_validate_path_param_string_valid(self):
        """Test path parameter string validation - valid"""
        is_valid, error = validate_path_param_string("test_config", "name")
        assert is_valid is True
    
    def test_validate_path_param_string_empty(self):
        """Test path parameter string validation - empty"""
        is_valid, error = validate_path_param_string("", "name")
        assert is_valid is False
    
    def test_validate_path_param_string_path_traversal(self):
        """Test path parameter string validation - path traversal"""
        is_valid, error = validate_path_param_string("../etc/passwd", "name")
        assert is_valid is False
        assert "traversal" in error
    
    def test_validate_path_param_string_slash(self):
        """Test path parameter string validation - slash"""
        is_valid, error = validate_path_param_string("test/config", "name")
        assert is_valid is False
    
    def test_validate_path_param_int_valid(self):
        """Test path parameter integer validation - valid"""
        is_valid, error = validate_path_param_int(123, "token")
        assert is_valid is True
    
    def test_validate_path_param_int_negative(self):
        """Test path parameter integer validation - negative"""
        is_valid, error = validate_path_param_int(-5, "token", min_value=0)
        assert is_valid is False
    
    def test_validate_path_param_int_not_int(self):
        """Test path parameter integer validation - not an integer"""
        is_valid, error = validate_path_param_int("abc", "token")
        assert is_valid is False


class TestXSSPrevention:
    """Test XSS attack prevention"""
    
    def test_xss_script_injection(self):
        """Test prevention of script injection"""
        attacks = [
            "<script>alert('XSS')</script>",
            "<script src='http://evil.com/xss.js'></script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "<iframe src='javascript:alert(1)'>",
            "<body onload=alert('XSS')>",
            "<input onfocus=alert('XSS') autofocus>",
            "<select onfocus=alert('XSS') autofocus>",
            "<textarea onfocus=alert('XSS') autofocus>",
            "<marquee onstart=alert('XSS')>",
            "<div style='background:url(javascript:alert(1))'>",
        ]
        
        for attack in attacks:
            sanitized = sanitize_string(attack)
            # Ensure dangerous HTML tags are escaped
            if "<script" in attack:
                assert "&lt;script" in sanitized or "<script" not in sanitized
            if "<img" in attack or "<svg" in attack or "<iframe" in attack:
                assert "&lt;" in sanitized
            # Event handlers should be escaped
            if "onerror" in attack or "onload" in attack or "onfocus" in attack:
                # The quotes around the handler should be escaped
                assert "&#x27;" in sanitized or "&quot;" in sanitized or "onerror" not in sanitized
    
    def test_xss_html_entity_encoding(self):
        """Test HTML entity encoding"""
        test_cases = [
            ("<", "&lt;"),
            (">", "&gt;"),
            ("&", "&amp;"),
            ("'", "&#x27;"),
            ('"', "&quot;"),
        ]
        
        for input_char, expected in test_cases:
            result = sanitize_string(input_char)
            assert expected in result
    
    def test_xss_sql_injection_chars(self):
        """Test SQL injection character escaping"""
        sql_attacks = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users--",
        ]
        
        for attack in sql_attacks:
            sanitized = sanitize_string(attack)
            # Single quotes should be escaped
            assert "'" not in sanitized or "&#x27;" in sanitized


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
