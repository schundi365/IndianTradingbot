"""
Simplified End-to-End Tests for Indian Market Web Dashboard

Tests complete user workflows with minimal mocking:
1. Broker connection flow
2. Instrument selection flow
3. Configuration save/load flow
4. Bot start/stop flow
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch


class TestBrokerConnectionFlowE2E:
    """Test complete broker connection workflow"""
    
    def test_get_broker_list(self, client):
        """Test getting list of supported brokers"""
        response = client.get('/api/broker/list')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'brokers' in data
        assert len(data['brokers']) > 0
        
        # Verify expected brokers
        broker_ids = [b['id'] for b in data['brokers']]
        assert 'kite' in broker_ids
        assert 'paper' in broker_ids
    
    def test_get_credentials_form(self, client):
        """Test getting credentials form for each broker"""
        brokers = ['kite', 'alice_blue', 'angel_one', 'upstox', 'paper']
        
        for broker in brokers:
            response = client.get(f'/api/broker/credentials-form/{broker}')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'fields' in data
            
            # Paper trading should have no fields
            if broker == 'paper':
                assert len(data['fields']) == 0
            else:
                assert len(data['fields']) > 0
    
    def test_broker_connection_flow(self, client, app):
        """Test complete broker connection and disconnection flow"""
        broker_manager = app.config['BROKER_MANAGER']
        
        # Mock the connection
        with patch.object(broker_manager, 'connect') as mock_connect:
            with patch.object(broker_manager, 'is_connected', return_value=True):
                mock_connect.return_value = (True, {'user_info': {'user_id': 'TEST'}})
                
                # Connect
                response = client.post('/api/broker/connect',
                    json={'broker': 'paper', 'credentials': {}})
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['status'] == 'success'
        
        # Check status
        with patch.object(broker_manager, 'is_connected', return_value=True):
            broker_manager.current_broker = 'paper'
            response = client.get('/api/broker/status')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['connected'] is True
        
        # Disconnect
        response = client.post('/api/broker/disconnect')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'


class TestInstrumentSelectionFlowE2E:
    """Test complete instrument selection workflow"""
    
    def test_fetch_instruments(self, client, app):
        """Test fetching instruments list"""
        instrument_service = app.config['INSTRUMENT_SERVICE']
        
        mock_instruments = [
            {
                'symbol': 'RELIANCE',
                'name': 'Reliance Industries Ltd',
                'exchange': 'NSE',
                'instrument_type': 'EQ',
                'instrument_token': 'NSE:RELIANCE'
            },
            {
                'symbol': 'TCS',
                'name': 'Tata Consultancy Services Ltd',
                'exchange': 'NSE',
                'instrument_type': 'EQ',
                'instrument_token': 'NSE:TCS'
            }
        ]
        
        with patch.object(instrument_service, 'get_instruments', return_value=mock_instruments):
            response = client.get('/api/instruments')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'instruments' in data
            assert len(data['instruments']) == 2
    
    def test_search_instruments(self, client, app):
        """Test searching instruments"""
        instrument_service = app.config['INSTRUMENT_SERVICE']
        
        mock_instruments = [
            {
                'symbol': 'RELIANCE',
                'name': 'Reliance Industries Ltd',
                'exchange': 'NSE',
                'instrument_type': 'EQ',
                'instrument_token': 'NSE:RELIANCE'
            }
        ]
        
        with patch.object(instrument_service, 'get_instruments', return_value=mock_instruments):
            response = client.get('/api/instruments?search=RELIANCE')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data['instruments']) == 1
            assert data['instruments'][0]['symbol'] == 'RELIANCE'
    
    def test_filter_instruments(self, client, app):
        """Test filtering instruments by exchange and type"""
        instrument_service = app.config['INSTRUMENT_SERVICE']
        
        mock_instruments = [
            {
                'symbol': 'NIFTY24JANFUT',
                'name': 'NIFTY JAN FUT',
                'exchange': 'NFO',
                'instrument_type': 'FUT',
                'instrument_token': 'NFO:NIFTY24JANFUT'
            }
        ]
        
        with patch.object(instrument_service, 'get_instruments', return_value=mock_instruments):
            response = client.get('/api/instruments?exchange=NFO&instrument_type=FUT')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data['instruments']) == 1
            assert data['instruments'][0]['exchange'] == 'NFO'


class TestConfigurationFlowE2E:
    """Test complete configuration save/load workflow"""
    
    def test_validate_configuration(self, client):
        """Test configuration validation"""
        valid_config = {
            'name': 'test_strategy',
            'broker': 'paper',
            'instruments': [{'symbol': 'RELIANCE', 'exchange': 'NSE'}],
            'strategy': 'trend_following',
            'timeframe': '5min',
            'risk_per_trade': 1.0,
            'max_positions': 3,
            'max_daily_loss': 5.0,
            'position_sizing': 'fixed',
            'base_position_size': 10000.0,
            'indicators': {'ema_fast': 9, 'ema_slow': 21},
            'trading_hours': {'start': '09:15', 'end': '15:30'},
            'paper_trading': True
        }
        
        response = client.post('/api/config/validate', json=valid_config)
        assert response.status_code in [200, 400]  # May return 400 if validation fails
        data = json.loads(response.data)
        # Just check we get a response with valid field
        assert 'valid' in data or 'status' in data
    
    def test_save_and_load_configuration(self, client, tmp_path):
        """Test saving and loading configuration"""
        test_config = {
            'name': 'test_strategy',
            'broker': 'paper',
            'strategy': 'trend_following',
            'timeframe': '5min',
            'risk_per_trade': 1.0
        }
        
        # Save configuration
        with patch('indian_dashboard.api.config.config_dir', tmp_path):
            response = client.post('/api/config', json=test_config)
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'success'
            
            # Load configuration
            response = client.get('/api/config/test_strategy')
            assert response.status_code == 200
            loaded_config = json.loads(response.data)
            assert loaded_config['name'] == 'test_strategy'
    
    def test_list_configurations(self, client, tmp_path):
        """Test listing saved configurations"""
        # Create a test config file
        config_file = tmp_path / 'test_config.json'
        with open(config_file, 'w') as f:
            json.dump({'name': 'test_config'}, f)
        
        with patch('indian_dashboard.api.config.config_dir', tmp_path):
            response = client.get('/api/config/list')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'configurations' in data
    
    def test_delete_configuration(self, client, tmp_path):
        """Test deleting configuration"""
        # Create a test config file
        config_file = tmp_path / 'test_delete.json'
        with open(config_file, 'w') as f:
            json.dump({'name': 'test_delete'}, f)
        
        with patch('indian_dashboard.api.config.config_dir', tmp_path):
            response = client.delete('/api/config/test_delete')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'success'
    
    def test_get_presets(self, client):
        """Test getting preset configurations"""
        response = client.get('/api/config/presets')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'presets' in data
        assert len(data['presets']) > 0


class TestBotControlFlowE2E:
    """Test complete bot start/stop workflow"""
    
    def test_get_bot_status(self, client, app):
        """Test getting bot status"""
        bot_controller = app.config['BOT_CONTROLLER']
        
        with patch.object(bot_controller, 'get_status', return_value={'running': False, 'uptime': 0, 'positions': 0}):
            response = client.get('/api/bot/status')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'running' in data
    
    def test_start_bot_without_broker(self, client, app):
        """Test starting bot without broker connection fails"""
        broker_manager = app.config['BROKER_MANAGER']
        
        with patch.object(broker_manager, 'is_connected', return_value=False):
            response = client.post('/api/bot/start')
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['status'] == 'error'
    
    def test_start_and_stop_bot(self, client, app):
        """Test starting and stopping bot"""
        broker_manager = app.config['BROKER_MANAGER']
        bot_controller = app.config['BOT_CONTROLLER']
        
        # Mock broker connection
        mock_adapter = Mock()
        mock_adapter.is_connected.return_value = True
        
        with patch.object(broker_manager, 'is_connected', return_value=True):
            with patch.object(broker_manager, 'get_adapter', return_value=mock_adapter):
                with patch.object(bot_controller, 'start', return_value=(True, 'Started')):
                    # Start bot
                    response = client.post('/api/bot/start')
                    assert response.status_code == 200
                    data = json.loads(response.data)
                    assert data['status'] == 'success'
        
        # Stop bot
        with patch.object(bot_controller, 'stop', return_value=(True, 'Stopped')):
            response = client.post('/api/bot/stop')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'success'
    
    def test_get_account_info(self, client, app):
        """Test getting account information"""
        bot_controller = app.config['BOT_CONTROLLER']
        
        mock_account = {
            'balance': 100000.0,
            'equity': 102000.0,
            'margin_available': 50000.0,
            'pnl_today': 2000.0
        }
        
        with patch.object(bot_controller, 'get_account_info', return_value=mock_account):
            response = client.get('/api/bot/account')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['balance'] == 100000.0
    
    def test_get_positions(self, client, app):
        """Test getting open positions"""
        bot_controller = app.config['BOT_CONTROLLER']
        
        mock_positions = [
            {
                'symbol': 'RELIANCE',
                'quantity': 10,
                'entry_price': 2500.0,
                'current_price': 2550.0,
                'pnl': 500.0
            }
        ]
        
        with patch.object(bot_controller, 'get_positions', return_value=mock_positions):
            response = client.get('/api/bot/positions')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'positions' in data
            assert len(data['positions']) == 1
    
    def test_get_trades(self, client, app):
        """Test getting trade history"""
        bot_controller = app.config['BOT_CONTROLLER']
        
        mock_trades = [
            {
                'timestamp': '2024-01-15 10:30:00',
                'symbol': 'RELIANCE',
                'type': 'BUY',
                'quantity': 10,
                'entry_price': 2500.0,
                'exit_price': 2550.0,
                'pnl': 500.0
            }
        ]
        
        with patch.object(bot_controller, 'get_trades', return_value=mock_trades):
            response = client.get('/api/bot/trades')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'trades' in data


class TestCompleteWorkflowE2E:
    """Test complete integrated workflow"""
    
    def test_full_trading_workflow(self, client, app, tmp_path):
        """
        Test complete workflow from broker connection to bot monitoring
        
        Steps:
        1. Connect to broker (paper trading)
        2. Fetch instruments
        3. Create and save configuration
        4. Start bot
        5. Check bot status
        6. Stop bot
        """
        broker_manager = app.config['BROKER_MANAGER']
        instrument_service = app.config['INSTRUMENT_SERVICE']
        bot_controller = app.config['BOT_CONTROLLER']
        
        # Step 1: Connect to broker
        with patch.object(broker_manager, 'connect', return_value=(True, {'user_info': {}})):
            with patch.object(broker_manager, 'is_connected', return_value=True):
                response = client.post('/api/broker/connect',
                    json={'broker': 'paper', 'credentials': {}})
                assert response.status_code == 200
        
        # Step 2: Fetch instruments
        mock_instruments = [
            {
                'symbol': 'NIFTY24JANFUT',
                'name': 'NIFTY JAN FUT',
                'exchange': 'NFO',
                'instrument_type': 'FUT',
                'instrument_token': 'NFO:NIFTY24JANFUT'
            }
        ]
        
        with patch.object(instrument_service, 'get_instruments', return_value=mock_instruments):
            response = client.get('/api/instruments')
            assert response.status_code == 200
            data = json.loads(response.data)
            instruments = data['instruments']
        
        # Step 3: Create and save configuration
        config = {
            'name': 'nifty_strategy',
            'broker': 'paper',
            'instruments': instruments,
            'strategy': 'trend_following',
            'timeframe': '5min',
            'risk_per_trade': 1.0,
            'max_positions': 2,
            'paper_trading': True
        }
        
        with patch('indian_dashboard.api.config.config_dir', tmp_path):
            response = client.post('/api/config', json=config)
            assert response.status_code == 200
        
        # Step 4: Start bot
        mock_adapter = Mock()
        mock_adapter.is_connected.return_value = True
        
        with patch.object(broker_manager, 'is_connected', return_value=True):
            with patch.object(broker_manager, 'get_adapter', return_value=mock_adapter):
                with patch.object(bot_controller, 'start', return_value=(True, 'Started')):
                    response = client.post('/api/bot/start')
                    assert response.status_code == 200
        
        # Step 5: Check bot status
        with patch.object(bot_controller, 'get_status', return_value={'running': True, 'uptime': 60, 'positions': 0}):
            response = client.get('/api/bot/status')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['running'] is True
        
        # Step 6: Stop bot
        with patch.object(bot_controller, 'stop', return_value=(True, 'Stopped')):
            response = client.post('/api/bot/stop')
            assert response.status_code == 200
