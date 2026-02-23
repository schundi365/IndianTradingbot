"""
Test Error Handling Implementation
Tests for global error handler and error display
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from indian_dashboard.dashboard_error_handler import (
    DashboardError,
    ValidationError,
    AuthenticationError,
    BrokerError,
    RateLimitError,
    TimeoutError,
    NetworkError,
    ErrorType,
    handle_errors
)


class TestDashboardErrors:
    """Test custom error classes"""
    
    def test_dashboard_error_creation(self):
        """Test creating a DashboardError"""
        error = DashboardError(
            "Test error",
            ErrorType.SERVER,
            500,
            {"detail": "test"}
        )
        
        assert error.message == "Test error"
        assert error.error_type == ErrorType.SERVER
        assert error.status_code == 500
        assert error.details == {"detail": "test"}
        assert error.timestamp is not None
    
    def test_dashboard_error_to_dict(self):
        """Test converting error to dictionary"""
        error = DashboardError("Test error", ErrorType.SERVER, 500)
        error_dict = error.to_dict()
        
        assert error_dict['success'] is False
        assert error_dict['error'] == "Test error"
        assert error_dict['error_type'] == ErrorType.SERVER
        assert 'timestamp' in error_dict
    
    def test_validation_error(self):
        """Test ValidationError"""
        error = ValidationError("Invalid input", {"field": "username"})
        
        assert error.message == "Invalid input"
        assert error.error_type == ErrorType.VALIDATION
        assert error.status_code == 400
        assert error.details == {"field": "username"}
    
    def test_authentication_error(self):
        """Test AuthenticationError"""
        error = AuthenticationError("Invalid credentials")
        
        assert error.message == "Invalid credentials"
        assert error.error_type == ErrorType.AUTHENTICATION
        assert error.status_code == 401
    
    def test_broker_error(self):
        """Test BrokerError"""
        error = BrokerError("Broker connection failed")
        
        assert error.message == "Broker connection failed"
        assert error.error_type == ErrorType.BROKER_ERROR
        assert error.status_code == 502
    
    def test_rate_limit_error(self):
        """Test RateLimitError"""
        error = RateLimitError("Too many requests", {"retry_after": 60})
        
        assert error.message == "Too many requests"
        assert error.error_type == ErrorType.RATE_LIMIT
        assert error.status_code == 429
        assert error.details["retry_after"] == 60
    
    def test_timeout_error(self):
        """Test TimeoutError"""
        error = TimeoutError("Request timeout")
        
        assert error.message == "Request timeout"
        assert error.error_type == ErrorType.TIMEOUT
        assert error.status_code == 504
    
    def test_network_error(self):
        """Test NetworkError"""
        error = NetworkError("Network unavailable")
        
        assert error.message == "Network unavailable"
        assert error.error_type == ErrorType.NETWORK
        assert error.status_code == 503


class TestErrorDecorator:
    """Test error handling decorator"""
    
    def test_handle_errors_decorator_success(self):
        """Test decorator with successful function"""
        @handle_errors
        def successful_function():
            return {"success": True, "data": "test"}
        
        # Mock request context
        from flask import Flask
        app = Flask(__name__)
        
        with app.test_request_context():
            result = successful_function()
            assert result == {"success": True, "data": "test"}
    
    def test_handle_errors_decorator_dashboard_error(self):
        """Test decorator with DashboardError"""
        @handle_errors
        def error_function():
            raise ValidationError("Invalid input")
        
        from flask import Flask
        app = Flask(__name__)
        
        with app.test_request_context():
            response, status_code = error_function()
            assert status_code == 400
            assert response.json['success'] is False
            assert response.json['error'] == "Invalid input"
            assert response.json['error_type'] == ErrorType.VALIDATION
    
    def test_handle_errors_decorator_value_error(self):
        """Test decorator with ValueError"""
        @handle_errors
        def value_error_function():
            raise ValueError("Invalid value")
        
        from flask import Flask
        app = Flask(__name__)
        
        with app.test_request_context():
            response, status_code = value_error_function()
            assert status_code == 400
            assert response.json['success'] is False
            assert "Invalid value" in response.json['error']
    
    def test_handle_errors_decorator_key_error(self):
        """Test decorator with KeyError"""
        @handle_errors
        def key_error_function():
            raise KeyError("missing_field")
        
        from flask import Flask
        app = Flask(__name__)
        
        with app.test_request_context():
            response, status_code = key_error_function()
            assert status_code == 400
            assert response.json['success'] is False
            assert "missing_field" in response.json['error']
    
    def test_handle_errors_decorator_generic_exception(self):
        """Test decorator with generic exception"""
        @handle_errors
        def generic_error_function():
            raise Exception("Unexpected error")
        
        from flask import Flask
        app = Flask(__name__)
        
        with app.test_request_context():
            response, status_code = generic_error_function()
            assert status_code == 500
            assert response.json['success'] is False
            assert response.json['error_type'] == ErrorType.SERVER


class TestErrorHandlerIntegration:
    """Test error handler integration with Flask"""
    
    def test_404_error_handler(self):
        """Test 404 error handler"""
        from flask import Flask
        from indian_dashboard.dashboard_error_handler import init_error_handlers
        
        app = Flask(__name__)
        init_error_handlers(app)
        
        with app.test_client() as client:
            response = client.get('/nonexistent')
            assert response.status_code == 404
            data = response.get_json()
            assert data['success'] is False
            assert data['error_type'] == ErrorType.NOT_FOUND
    
    def test_500_error_handler(self):
        """Test 500 error handler"""
        from flask import Flask
        from indian_dashboard.dashboard_error_handler import init_error_handlers
        
        app = Flask(__name__)
        init_error_handlers(app)
        
        @app.route('/error')
        def error_route():
            raise Exception("Test error")
        
        with app.test_client() as client:
            response = client.get('/error')
            assert response.status_code == 500
            data = response.get_json()
            assert data['success'] is False
            assert data['error_type'] == ErrorType.UNKNOWN


def test_error_types():
    """Test all error type constants"""
    assert ErrorType.VALIDATION == 'validation_error'
    assert ErrorType.AUTHENTICATION == 'authentication_error'
    assert ErrorType.AUTHORIZATION == 'authorization_error'
    assert ErrorType.NOT_FOUND == 'not_found'
    assert ErrorType.BROKER_ERROR == 'broker_error'
    assert ErrorType.RATE_LIMIT == 'rate_limit_error'
    assert ErrorType.TIMEOUT == 'timeout_error'
    assert ErrorType.NETWORK == 'network_error'
    assert ErrorType.SERVER == 'server_error'
    assert ErrorType.UNKNOWN == 'unknown_error'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
