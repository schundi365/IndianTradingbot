"""
Integration tests for bot control handlers
Tests the complete flow: Frontend -> API -> BotController
"""

import pytest
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import Flask for creating test app
from flask import Flask

from services.bot_controller import BotController
from services.broker_manager import BrokerManager
from api.bot import init_bot_api


@pytest.fixture
def app():
    """Create test Flask app"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    
    # Create mock dependencies
    bot_controller = BotController()
    broker_manager = Mock()
    
    # Register bot API blueprint
    bot_api = init_bot_api(bot_controller, broker_manager)
    app.register_blueprint(bot_api)
    
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def mock_broker_adapter():
    """Create mock broker adapter"""
    adapter = Mock()
    adapter.is_connected.return_value = True
    adapter.connect.return_value = True
    adapter.get_account_info.return_value = {
        'balance': 100000,
        'equity': 105000,
        'margin_available': 50000,
        'margin_used': 10000,
        'pnl_today': 5000
    }
    adapter.get_positions.return_value = []
    adapter.get_orders.return_value = []
    return adapter


@pytest.fixture
def mock_bot_controller(mock_broker_adapter):
    """Create mock bot controller"""
    controller = BotController()
    return controller


@pytest.fixture
def mock_broker_manager(mock_broker_adapter):
    """Create mock broker manager"""
    manager = Mock()
    manager.is_connected.return_value = True
    manager.get_adapter.return_value = mock_broker_adapter
    return manager


class TestBotControlHandlers:
    """Test bot control handlers"""
    
    def test_start_bot_success(self, client, mock_broker_manager, mock_broker_adapter):
        """Test starting bot successfully"""
        with patch('api.bot.bot_bp.broker_manager', mock_broker_manager):
            with patch('api.bot.bot_bp.bot_controller') as mock_controller:
                # Mock successful start
                mock_controller.start.return_value = (True, "Bot started successfully")
                
                # Make request
                config = {
                    'strategy': 'trend_following',
                    'timeframe': '5min',
                    'instruments': [{'symbol': 'NIFTY', 'exchange': 'NSE'}]
                }
                
                response = client.post(
                    '/api/bot/start',
                    data=json.dumps({'config': config}),
                    content_type='application/json'
                )
                
                # Verify response
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] is True
                assert 'started successfully' in data['message'].lower()
                
                # Verify controller was called
                mock_controller.start.assert_called_once()
    
    def test_start_bot_no_config(self, client, mock_broker_manager):
        """Test starting bot without config"""
        with patch('api.bot.bot_bp.broker_manager', mock_broker_manager):
            response = client.post(
                '/api/bot/start',
                data=json.dumps({}),
                content_type='application/json'
            )
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'configuration' in data['error'].lower()
    
    def test_start_bot_broker_not_connected(self, client):
        """Test starting bot when broker not connected"""
        mock_manager = Mock()
        mock_manager.is_connected.return_value = False
        
        with patch('api.bot.bot_bp.broker_manager', mock_manager):
            config = {
                'strategy': 'trend_following',
                'instruments': [{'symbol': 'NIFTY'}]
            }
            
            response = client.post(
                '/api/bot/start',
                data=json.dumps({'config': config}),
                content_type='application/json'
            )
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'broker not connected' in data['error'].lower()
    
    def test_stop_bot_success(self, client):
        """Test stopping bot successfully"""
        with patch('api.bot.bot_bp.bot_controller') as mock_controller:
            # Mock successful stop
            mock_controller.stop.return_value = (True, "Bot stopped successfully")
            
            response = client.post('/api/bot/stop')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'stopped successfully' in data['message'].lower()
            
            # Verify controller was called
            mock_controller.stop.assert_called_once()
    
    def test_stop_bot_not_running(self, client):
        """Test stopping bot when not running"""
        with patch('api.bot.bot_bp.bot_controller') as mock_controller:
            # Mock bot not running
            mock_controller.stop.return_value = (False, "Bot is not running")
            
            response = client.post('/api/bot/stop')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'not running' in data['error'].lower()
    
    def test_restart_bot_success(self, client):
        """Test restarting bot successfully"""
        with patch('api.bot.bot_bp.bot_controller') as mock_controller:
            # Mock successful restart
            mock_controller.restart.return_value = (True, "Bot restarted successfully")
            
            response = client.post('/api/bot/restart')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'restarted successfully' in data['message'].lower()
            
            # Verify controller was called
            mock_controller.restart.assert_called_once()
    
    def test_restart_bot_failure(self, client):
        """Test restarting bot failure"""
        with patch('api.bot.bot_bp.bot_controller') as mock_controller:
            # Mock restart failure
            mock_controller.restart.return_value = (False, "No configuration available")
            
            response = client.post('/api/bot/restart')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'configuration' in data['error'].lower()
    
    def test_get_bot_status(self, client):
        """Test getting bot status"""
        with patch('api.bot.bot_bp.bot_controller') as mock_controller:
            # Mock status
            mock_controller.get_status.return_value = {
                'running': True,
                'start_time': '2024-01-01T10:00:00',
                'uptime_seconds': 3600,
                'config_loaded': True,
                'broker_connected': True
            }
            
            response = client.get('/api/bot/status')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['status']['running'] is True
            assert data['status']['uptime_seconds'] == 3600


class TestBotControllerMethods:
    """Test BotController methods directly"""
    
    def test_start_method(self, mock_broker_adapter):
        """Test BotController.start method"""
        controller = BotController()
        
        config = {
            'strategy': 'trend_following',
            'timeframe': '5min',
            'instruments': [{'symbol': 'NIFTY', 'exchange': 'NSE'}]
        }
        
        with patch('services.bot_controller.IndianTradingBot') as MockBot:
            # Mock bot instance
            mock_bot = Mock()
            mock_bot.connect.return_value = True
            mock_bot.validate_instruments.return_value = True
            MockBot.return_value = mock_bot
            
            # Start bot
            success, message = controller.start(config, mock_broker_adapter)
            
            assert success is True
            assert 'started successfully' in message.lower()
            assert controller.is_running is True
            assert controller.config == config
    
    def test_start_already_running(self, mock_broker_adapter):
        """Test starting bot when already running"""
        controller = BotController()
        controller.is_running = True
        
        config = {'strategy': 'test'}
        success, message = controller.start(config, mock_broker_adapter)
        
        assert success is False
        assert 'already running' in message.lower()
    
    def test_stop_method(self, mock_broker_adapter):
        """Test BotController.stop method"""
        controller = BotController()
        
        # Setup running bot
        controller.is_running = True
        controller.bot = Mock()
        controller.bot.disconnect = Mock()
        controller.bot_thread = Mock()
        controller.bot_thread.is_alive.return_value = False
        
        # Stop bot
        success, message = controller.stop()
        
        assert success is True
        assert 'stopped' in message.lower()
        assert controller.is_running is False
        assert controller.bot is None
    
    def test_stop_not_running(self):
        """Test stopping bot when not running"""
        controller = BotController()
        controller.is_running = False
        
        success, message = controller.stop()
        
        assert success is False
        assert 'not running' in message.lower()
    
    def test_restart_method(self, mock_broker_adapter):
        """Test BotController.restart method"""
        controller = BotController()
        
        # Setup with config
        config = {'strategy': 'test', 'instruments': []}
        controller.config = config
        controller.broker_adapter = mock_broker_adapter
        controller.is_running = False
        
        with patch.object(controller, 'start') as mock_start:
            mock_start.return_value = (True, "Bot started successfully")
            
            success, message = controller.restart()
            
            assert success is True
            mock_start.assert_called_once_with(config, mock_broker_adapter)
    
    def test_restart_no_config(self):
        """Test restarting bot without config"""
        controller = BotController()
        controller.config = None
        controller.is_running = False
        
        success, message = controller.restart()
        
        assert success is False
        assert 'configuration' in message.lower()
    
    def test_get_status(self):
        """Test getting bot status"""
        controller = BotController()
        controller.is_running = True
        controller.config = {'strategy': 'test'}
        
        from datetime import datetime
        controller.start_time = datetime.now()
        
        status = controller.get_status()
        
        assert status['running'] is True
        assert status['config_loaded'] is True
        assert status['uptime_seconds'] is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
