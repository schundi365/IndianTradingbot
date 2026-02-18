"""
Pytest configuration and fixtures for Indian Dashboard tests
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def app():
    """Create Flask app for testing"""
    import indian_dashboard.indian_dashboard as dashboard_module
    
    flask_app = dashboard_module.app
    flask_app.config['TESTING'] = True
    
    return flask_app


@pytest.fixture
def client(app):
    """Create Flask test client"""
    return app.test_client()


@pytest.fixture
def mock_broker_manager():
    """Create mock BrokerManager"""
    manager = Mock()
    manager.is_connected.return_value = True
    manager.get_adapter.return_value = Mock()
    return manager


@pytest.fixture
def mock_bot_controller():
    """Create mock BotController"""
    controller = Mock()
    controller.get_status.return_value = {
        'running': False,
        'uptime': 0,
        'positions': 0
    }
    controller.get_account_info.return_value = {
        'balance': 100000.0,
        'equity': 100000.0,
        'margin_available': 50000.0,
        'margin_used': 0.0,
        'pnl_today': 0.0
    }
    controller.get_positions.return_value = []
    controller.get_trades.return_value = []
    return controller
