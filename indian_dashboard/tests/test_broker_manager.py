"""
Unit tests for BrokerManager service
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.broker_manager import BrokerManager


class TestBrokerManager:
    """Test BrokerManager service"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.manager = BrokerManager()
    
    def test_get_supported_brokers(self):
        """Test getting supported brokers"""
        brokers = self.manager.get_supported_brokers()
        
        assert isinstance(brokers, list)
        assert len(brokers) > 0
        
        # Check broker structure
        for broker in brokers:
            assert 'id' in broker
            assert 'name' in broker
            assert 'logo' in broker
            assert 'oauth_enabled' in broker
    
    def test_get_credentials_form(self):
        """Test getting credentials form"""
        # Test Kite form
        kite_form = self.manager.get_credentials_form('kite')
        assert isinstance(kite_form, list)
        assert len(kite_form) > 0
        
        # Test paper trading (no credentials)
        paper_form = self.manager.get_credentials_form('paper')
        assert isinstance(paper_form, list)
        assert len(paper_form) == 0
        
        # Test unknown broker
        unknown_form = self.manager.get_credentials_form('unknown')
        assert isinstance(unknown_form, list)
        assert len(unknown_form) == 0
    
    def test_is_connected_when_not_connected(self):
        """Test is_connected when no broker connected"""
        assert self.manager.is_connected() is False
    
    def test_get_status_when_not_connected(self):
        """Test get_status when no broker connected"""
        status = self.manager.get_status()
        
        assert status['connected'] is False
        assert status['broker'] is None
        assert status['user_info'] == {}
        assert status['connection_time'] is None
    
    def test_get_adapter_when_not_connected(self):
        """Test get_adapter when no broker connected"""
        adapter = self.manager.get_adapter()
        assert adapter is None
    
    def test_get_broker_type_when_not_connected(self):
        """Test get_broker_type when no broker connected"""
        broker_type = self.manager.get_broker_type()
        assert broker_type is None
    
    def test_disconnect_when_not_connected(self):
        """Test disconnect when no broker connected"""
        success, message = self.manager.disconnect()
        assert success is False
        assert "No broker connected" in message
    
    def test_test_connection_when_not_connected(self):
        """Test test_connection when no broker connected"""
        success, message = self.manager.test_connection()
        assert success is False
        assert "No broker connected" in message
    
    @patch('services.broker_manager.PaperTradingAdapter')
    def test_connect_paper_trading(self, mock_adapter_class):
        """Test connecting to paper trading"""
        # Mock adapter
        mock_adapter = Mock()
        mock_adapter.connect.return_value = True
        mock_adapter.is_connected.return_value = True
        mock_adapter_class.return_value = mock_adapter
        
        # Connect
        success, result = self.manager.connect('paper', {})
        
        assert success is True
        assert 'user_info' in result
        assert self.manager.is_connected() is True
        assert self.manager.get_broker_type() == 'paper'
    
    @patch('services.broker_manager.PaperTradingAdapter')
    def test_connect_failure(self, mock_adapter_class):
        """Test connection failure"""
        # Mock adapter that fails to connect
        mock_adapter = Mock()
        mock_adapter.connect.return_value = False
        mock_adapter_class.return_value = mock_adapter
        
        # Connect
        success, result = self.manager.connect('paper', {})
        
        assert success is False
        assert 'error' in result
        assert self.manager.is_connected() is False
    
    def test_connect_unsupported_broker(self):
        """Test connecting to unsupported broker"""
        success, result = self.manager.connect('unsupported', {})
        
        assert success is False
        assert 'error' in result
        assert 'Unsupported broker' in result['error']
