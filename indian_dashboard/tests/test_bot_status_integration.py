"""
Integration tests for Bot Status Card (Task 8.1)
Tests the bot status card functionality including:
- Running/stopped status display
- Uptime display
- Broker connection status
- Start/stop/restart buttons
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from indian_dashboard.services.bot_controller import BotController
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta


class TestBotStatusCard:
    """Test bot status card functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.bot_controller = BotController()
        self.mock_broker_adapter = Mock()
        self.mock_broker_adapter.is_connected.return_value = True
        self.mock_broker_adapter.connect.return_value = True
        
    def test_bot_status_stopped_initially(self):
        """Test that bot status is stopped initially"""
        status = self.bot_controller.get_status()
        
        assert status['running'] == False
        assert status['start_time'] is None
        assert status['uptime_seconds'] is None
        assert status['config_loaded'] == False
        assert status['broker_connected'] == False
    
    def test_bot_status_running_after_start(self):
        """Test that bot status shows running after start"""
        config = {
            'instruments': [{'symbol': 'SBIN', 'exchange': 'NSE'}],
            'strategy': 'trend_following',
            'timeframe': '5minute'
        }
        
        with patch('indian_dashboard.services.bot_controller.IndianTradingBot') as MockBot:
            mock_bot_instance = Mock()
            mock_bot_instance.connect.return_value = True
            mock_bot_instance.validate_instruments.return_value = True
            MockBot.return_value = mock_bot_instance
            
            success, message = self.bot_controller.start(config, self.mock_broker_adapter)
            
            assert success == True
            assert 'started successfully' in message.lower()
            
            status = self.bot_controller.get_status()
            assert status['running'] == True
            assert status['start_time'] is not None
            assert status['config_loaded'] == True
            assert status['broker_connected'] == True
    
    def test_bot_status_uptime_calculation(self):
        """Test that uptime is calculated correctly"""
        config = {
            'instruments': [{'symbol': 'SBIN', 'exchange': 'NSE'}],
            'strategy': 'trend_following',
            'timeframe': '5minute'
        }
        
        with patch('indian_dashboard.services.bot_controller.IndianTradingBot') as MockBot:
            mock_bot_instance = Mock()
            mock_bot_instance.connect.return_value = True
            mock_bot_instance.validate_instruments.return_value = True
            MockBot.return_value = mock_bot_instance
            
            # Start bot
            self.bot_controller.start(config, self.mock_broker_adapter)
            
            # Set start time to 1 hour ago
            self.bot_controller.start_time = datetime.now() - timedelta(hours=1)
            
            status = self.bot_controller.get_status()
            
            # Uptime should be approximately 3600 seconds (1 hour)
            assert status['uptime_seconds'] is not None
            assert 3590 <= status['uptime_seconds'] <= 3610  # Allow 10 second tolerance
    
    def test_bot_status_stopped_after_stop(self):
        """Test that bot status shows stopped after stop"""
        config = {
            'instruments': [{'symbol': 'SBIN', 'exchange': 'NSE'}],
            'strategy': 'trend_following',
            'timeframe': '5minute'
        }
        
        with patch('indian_dashboard.services.bot_controller.IndianTradingBot') as MockBot:
            mock_bot_instance = Mock()
            mock_bot_instance.connect.return_value = True
            mock_bot_instance.validate_instruments.return_value = True
            mock_bot_instance.disconnect.return_value = None
            MockBot.return_value = mock_bot_instance
            
            # Start bot
            self.bot_controller.start(config, self.mock_broker_adapter)
            
            # Stop bot
            success, message = self.bot_controller.stop()
            
            assert success == True
            assert 'stopped' in message.lower()
            
            status = self.bot_controller.get_status()
            assert status['running'] == False
            assert status['start_time'] is None
            assert status['uptime_seconds'] is None
    
    def test_bot_status_broker_connection_status(self):
        """Test that broker connection status is reflected correctly"""
        # Test with connected broker
        self.mock_broker_adapter.is_connected.return_value = True
        status = self.bot_controller.get_status()
        
        # When bot is not running, broker_connected should be False
        assert status['broker_connected'] == False
        
        # Start bot with connected broker
        config = {
            'instruments': [{'symbol': 'SBIN', 'exchange': 'NSE'}],
            'strategy': 'trend_following',
            'timeframe': '5minute'
        }
        
        with patch('indian_dashboard.services.bot_controller.IndianTradingBot') as MockBot:
            mock_bot_instance = Mock()
            mock_bot_instance.connect.return_value = True
            mock_bot_instance.validate_instruments.return_value = True
            MockBot.return_value = mock_bot_instance
            
            self.bot_controller.start(config, self.mock_broker_adapter)
            
            status = self.bot_controller.get_status()
            assert status['broker_connected'] == True
    
    def test_bot_restart_functionality(self):
        """Test that bot can be restarted"""
        config = {
            'instruments': [{'symbol': 'SBIN', 'exchange': 'NSE'}],
            'strategy': 'trend_following',
            'timeframe': '5minute'
        }
        
        with patch('indian_dashboard.services.bot_controller.IndianTradingBot') as MockBot:
            mock_bot_instance = Mock()
            mock_bot_instance.connect.return_value = True
            mock_bot_instance.validate_instruments.return_value = True
            mock_bot_instance.disconnect.return_value = None
            MockBot.return_value = mock_bot_instance
            
            # Start bot
            self.bot_controller.start(config, self.mock_broker_adapter)
            
            # Restart bot
            success, message = self.bot_controller.restart()
            
            assert success == True
            
            status = self.bot_controller.get_status()
            assert status['running'] == True
    
    def test_bot_cannot_start_without_broker(self):
        """Test that bot cannot start without broker connection"""
        config = {
            'instruments': [{'symbol': 'SBIN', 'exchange': 'NSE'}],
            'strategy': 'trend_following',
            'timeframe': '5minute'
        }
        
        # Broker not connected
        self.mock_broker_adapter.is_connected.return_value = False
        
        success, message = self.bot_controller.start(config, self.mock_broker_adapter)
        
        assert success == False
        assert 'not connected' in message.lower()
    
    def test_bot_cannot_start_if_already_running(self):
        """Test that bot cannot start if already running"""
        config = {
            'instruments': [{'symbol': 'SBIN', 'exchange': 'NSE'}],
            'strategy': 'trend_following',
            'timeframe': '5minute'
        }
        
        with patch('indian_dashboard.services.bot_controller.IndianTradingBot') as MockBot:
            mock_bot_instance = Mock()
            mock_bot_instance.connect.return_value = True
            mock_bot_instance.validate_instruments.return_value = True
            MockBot.return_value = mock_bot_instance
            
            # Start bot
            self.bot_controller.start(config, self.mock_broker_adapter)
            
            # Try to start again
            success, message = self.bot_controller.start(config, self.mock_broker_adapter)
            
            assert success == False
            assert 'already running' in message.lower()
    
    def test_bot_cannot_stop_if_not_running(self):
        """Test that bot cannot stop if not running"""
        success, message = self.bot_controller.stop()
        
        assert success == False
        assert 'not running' in message.lower()
    
    def test_get_positions_count(self):
        """Test getting positions count for status display"""
        # Mock positions
        self.mock_broker_adapter.get_positions.return_value = [
            {'symbol': 'SBIN', 'quantity': 10},
            {'symbol': 'RELIANCE', 'quantity': 5}
        ]
        
        config = {
            'instruments': [{'symbol': 'SBIN', 'exchange': 'NSE'}],
            'strategy': 'trend_following',
            'timeframe': '5minute'
        }
        
        with patch('indian_dashboard.services.bot_controller.IndianTradingBot') as MockBot:
            mock_bot_instance = Mock()
            mock_bot_instance.connect.return_value = True
            mock_bot_instance.validate_instruments.return_value = True
            MockBot.return_value = mock_bot_instance
            
            self.bot_controller.start(config, self.mock_broker_adapter)
            
            positions = self.bot_controller.get_positions()
            
            assert len(positions) == 2
            assert positions[0]['symbol'] == 'SBIN'
            assert positions[1]['symbol'] == 'RELIANCE'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
