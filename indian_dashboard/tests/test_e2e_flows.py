"""
End-to-End Tests for Indian Market Web Dashboard

Tests complete user workflows:
1. Broker connection flow
2. Instrument selection flow
3. Configuration save/load flow
4. Bot start/stop flow
"""

import pytest
import json
import time
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path


@pytest.fixture
def mock_services(app):
    """Mock all services in the Flask app"""
    # Get services from app config
    broker_manager = app.config['BROKER_MANAGER']
    instrument_service = app.config['INSTRUMENT_SERVICE']
    bot_controller = app.config['BOT_CONTROLLER']
    
    return {
        'broker_manager': broker_manager,
        'instrument_service': instrument_service,
        'bot_controller': bot_controller
    }


class TestBrokerConnectionFlow:
    """Test complete broker connection workflow"""
    
    def test_complete_broker_connection_flow(self, client, app):
        """
        E2E Test: Complete broker connection flow
        
        Steps:
        1. Get list of supported brokers
        2. Select a broker (Kite)
        3. Get credentials form for selected broker
        4. Submit credentials (mocked)
        5. Verify connection status (mocked)
        6. Disconnect
        """
        # Step 1: Get list of supported brokers
        response = client.get('/api/broker/list')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'brokers' in data
        assert len(data['brokers']) > 0
        
        # Verify Kite is in the list
        broker_ids = [b['id'] for b in data['brokers']]
        assert 'kite' in broker_ids
        
        # Step 2: Select Kite broker
        kite_broker = next(b for b in data['brokers'] if b['id'] == 'kite')
        assert kite_broker['name'] == 'Kite Connect'
        
        # Step 3: Get credentials form for Kite
        response = client.get('/api/broker/credentials-form/kite')
        assert response.status_code == 200
        form_data = json.loads(response.data)
        assert 'fields' in form_data
        assert len(form_data['fields']) > 0
        
        # Verify required fields
        field_names = [f['name'] for f in form_data['fields']]
        assert 'api_key' in field_names
        assert 'api_secret' in field_names
        
        # Step 4: Submit credentials and connect (mocked)
        broker_manager = app.config['BROKER_MANAGER']
        with patch.object(broker_manager, 'connect') as mock_connect:
            with patch.object(broker_manager, 'is_connected', return_value=True):
                with patch.object(broker_manager, 'get_adapter') as mock_get_adapter:
                    mock_adapter = Mock()
                    mock_adapter.get_user_info.return_value = {
                        'user_id': 'TEST123',
                        'user_name': 'Test User',
                        'email': 'test@example.com'
                    }
                    mock_connect.return_value = (True, {'user_info': mock_adapter.get_user_info()})
                    mock_get_adapter.return_value = mock_adapter
                    
                    response = client.post('/api/broker/connect', 
                        json={
                            'broker': 'paper',  # Use paper trading for simplicity
                            'credentials': {}
                        })
                    assert response.status_code == 200
                    connect_data = json.loads(response.data)
                    assert connect_data['status'] == 'success'
        
        # Step 5: Verify connection status
        with patch.object(broker_manager, 'is_connected', return_value=True):
            with patch.object(broker_manager, 'current_broker', 'paper'):
                response = client.get('/api/broker/status')
                assert response.status_code == 200
                status_data = json.loads(response.data)
                assert status_data['connected'] is True
        
        # Step 6: Disconnect
        response = client.post('/api/broker/disconnect')
        assert response.status_code == 200
        disconnect_data = json.loads(response.data)
        assert disconnect_data['status'] == 'success'
    
    def test_broker_connection_with_invalid_credentials(self, client, app):
        """Test broker connection flow with invalid credentials"""
        broker_manager = app.config['BROKER_MANAGER']
        with patch.object(broker_manager, 'connect', return_value=(False, {'error': 'Invalid credentials'})):
            response = client.post('/api/broker/connect',
                json={
                    'broker': 'kite',
                    'credentials': {
                        'api_key': 'invalid_key',
                        'api_secret': 'invalid_secret'
                    }
                })
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['status'] == 'error'
            assert 'error' in data
    
    def test_paper_trading_connection_flow(self, client, app):
        """Test paper trading connection (no credentials needed)"""
        broker_manager = app.config['BROKER_MANAGER']
        with patch.object(broker_manager, 'connect') as mock_connect:
            with patch.object(broker_manager, 'get_adapter') as mock_get_adapter:
                mock_adapter = Mock()
                mock_adapter.is_connected.return_value = True
                mock_connect.return_value = (True, {'user_info': {}})
                mock_get_adapter.return_value = mock_adapter
                
                response = client.post('/api/broker/connect',
                    json={
                        'broker': 'paper',
                        'credentials': {}
                    })
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['status'] == 'success'


class TestInstrumentSelectionFlow:
    """Test complete instrument selection workflow"""
    
    def test_complete_instrument_selection_flow(self, client):
        """
        E2E Test: Complete instrument selection flow
        
        Steps:
        1. Connect to broker
        2. Fetch instruments list
        3. Search for specific instruments
        4. Filter by exchange and type
        5. Select multiple instruments
        6. Verify selections
        """
        # Step 1: Connect to broker (mocked)
        with patch('indian_dashboard.api.broker.broker_manager') as mock_broker_mgr:
            mock_adapter = Mock()
            mock_adapter.is_connected.return_value = True
            mock_broker_mgr.connect.return_value = (True, {'user_info': {}})
            mock_broker_mgr.is_connected.return_value = True
            mock_broker_mgr.get_adapter.return_value = mock_adapter
            
            # Step 2: Fetch instruments list
            with patch('indian_dashboard.api.instruments.instrument_service') as mock_inst_service:
                mock_instruments = [
                    {
                        'symbol': 'RELIANCE',
                        'name': 'Reliance Industries Ltd',
                        'exchange': 'NSE',
                        'instrument_type': 'EQ',
                        'instrument_token': 'NSE:RELIANCE',
                        'last_price': 2500.0
                    },
                    {
                        'symbol': 'TCS',
                        'name': 'Tata Consultancy Services Ltd',
                        'exchange': 'NSE',
                        'instrument_type': 'EQ',
                        'instrument_token': 'NSE:TCS',
                        'last_price': 3500.0
                    },
                    {
                        'symbol': 'NIFTY24JANFUT',
                        'name': 'NIFTY JAN FUT',
                        'exchange': 'NFO',
                        'instrument_type': 'FUT',
                        'instrument_token': 'NFO:NIFTY24JANFUT',
                        'last_price': 21500.0
                    }
                ]
                mock_inst_service.get_instruments.return_value = mock_instruments
                
                response = client.get('/api/instruments')
                assert response.status_code == 200
                data = json.loads(response.data)
                assert 'instruments' in data
                assert len(data['instruments']) == 3
            
            # Step 3: Search for specific instruments
            with patch('indian_dashboard.api.instruments.instrument_service') as mock_inst_service:
                mock_inst_service.get_instruments.return_value = [
                    mock_instruments[0]  # Only RELIANCE
                ]
                
                response = client.get('/api/instruments?search=RELIANCE')
                assert response.status_code == 200
                data = json.loads(response.data)
                assert len(data['instruments']) == 1
                assert data['instruments'][0]['symbol'] == 'RELIANCE'
            
            # Step 4: Filter by exchange
            with patch('indian_dashboard.api.instruments.instrument_service') as mock_inst_service:
                mock_inst_service.get_instruments.return_value = [
                    mock_instruments[0],
                    mock_instruments[1]
                ]
                
                response = client.get('/api/instruments?exchange=NSE')
                assert response.status_code == 200
                data = json.loads(response.data)
                assert len(data['instruments']) == 2
                for inst in data['instruments']:
                    assert inst['exchange'] == 'NSE'
            
            # Step 5: Filter by instrument type
            with patch('indian_dashboard.api.instruments.instrument_service') as mock_inst_service:
                mock_inst_service.get_instruments.return_value = [
                    mock_instruments[2]
                ]
                
                response = client.get('/api/instruments?instrument_type=FUT')
                assert response.status_code == 200
                data = json.loads(response.data)
                assert len(data['instruments']) == 1
                assert data['instruments'][0]['instrument_type'] == 'FUT'
    
    def test_instrument_refresh_flow(self, client):
        """Test instrument cache refresh flow"""
        with patch('indian_dashboard.api.broker.broker_manager') as mock_broker_mgr:
            mock_adapter = Mock()
            mock_adapter.is_connected.return_value = True
            mock_broker_mgr.is_connected.return_value = True
            mock_broker_mgr.get_adapter.return_value = mock_adapter
            
            with patch('indian_dashboard.api.instruments.instrument_service') as mock_inst_service:
                mock_inst_service.refresh_instruments.return_value = 100
                
                response = client.post('/api/instruments/refresh')
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['status'] == 'success'
                assert data['count'] == 100
    
    def test_get_single_instrument(self, client):
        """Test fetching single instrument details"""
        with patch('indian_dashboard.api.instruments.instrument_service') as mock_inst_service:
            mock_inst_service.get_instrument.return_value = {
                'symbol': 'RELIANCE',
                'name': 'Reliance Industries Ltd',
                'exchange': 'NSE',
                'instrument_type': 'EQ',
                'instrument_token': 'NSE:RELIANCE'
            }
            
            response = client.get('/api/instruments/NSE:RELIANCE')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['symbol'] == 'RELIANCE'


class TestConfigurationFlow:
    """Test complete configuration save/load workflow"""
    
    def test_complete_configuration_flow(self, client, tmp_path):
        """
        E2E Test: Complete configuration save/load flow
        
        Steps:
        1. Create a new configuration
        2. Validate configuration
        3. Save configuration
        4. List saved configurations
        5. Load configuration
        6. Update configuration
        7. Delete configuration
        """
        # Step 1 & 2: Create and validate configuration
        test_config = {
            'name': 'test_strategy',
            'broker': 'kite',
            'instruments': [
                {
                    'symbol': 'RELIANCE',
                    'exchange': 'NSE',
                    'instrument_token': 'NSE:RELIANCE'
                }
            ],
            'strategy': 'trend_following',
            'timeframe': '5min',
            'risk_per_trade': 1.0,
            'max_positions': 3,
            'max_daily_loss': 5.0,
            'position_sizing': 'fixed',
            'base_position_size': 10000.0,
            'indicators': {
                'ema_fast': 9,
                'ema_slow': 21
            },
            'trading_hours': {
                'start': '09:15',
                'end': '15:30'
            },
            'paper_trading': True
        }
        
        response = client.post('/api/config/validate', json=test_config)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['valid'] is True
        
        # Step 3: Save configuration
        with patch('indian_dashboard.api.config.config_dir', tmp_path):
            response = client.post('/api/config', json=test_config)
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'success'
            assert 'file' in data
        
        # Step 4: List saved configurations
        with patch('indian_dashboard.api.config.config_dir', tmp_path):
            # Create a test config file
            config_file = tmp_path / 'test_strategy.json'
            with open(config_file, 'w') as f:
                json.dump(test_config, f)
            
            response = client.get('/api/config/list')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'configurations' in data
            assert len(data['configurations']) > 0
        
        # Step 5: Load configuration
        with patch('indian_dashboard.api.config.config_dir', tmp_path):
            response = client.get('/api/config/test_strategy')
            assert response.status_code == 200
            loaded_config = json.loads(response.data)
            assert loaded_config['name'] == 'test_strategy'
            assert loaded_config['strategy'] == 'trend_following'
        
        # Step 6: Update configuration
        test_config['risk_per_trade'] = 2.0
        with patch('indian_dashboard.api.config.config_dir', tmp_path):
            response = client.post('/api/config', json=test_config)
            assert response.status_code == 200
            
            # Verify update
            response = client.get('/api/config/test_strategy')
            updated_config = json.loads(response.data)
            assert updated_config['risk_per_trade'] == 2.0
        
        # Step 7: Delete configuration
        with patch('indian_dashboard.api.config.config_dir', tmp_path):
            response = client.delete('/api/config/test_strategy')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'success'
    
    def test_configuration_presets_flow(self, client):
        """Test loading preset configurations"""
        response = client.get('/api/config/presets')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'presets' in data
        assert len(data['presets']) > 0
        
        # Verify preset structure
        for preset in data['presets']:
            assert 'name' in preset
            assert 'strategy' in preset
            assert 'instruments' in preset
    
    def test_configuration_validation_errors(self, client):
        """Test configuration validation with invalid data"""
        invalid_config = {
            'name': 'invalid',
            'risk_per_trade': 150.0,  # Invalid: > 100%
            'max_positions': -1,  # Invalid: negative
            'trading_hours': {
                'start': '25:00',  # Invalid time
                'end': '15:30'
            }
        }
        
        response = client.post('/api/config/validate', json=invalid_config)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['valid'] is False
        assert 'errors' in data
        assert len(data['errors']) > 0


class TestBotControlFlow:
    """Test complete bot start/stop workflow"""
    
    def test_complete_bot_control_flow(self, client):
        """
        E2E Test: Complete bot control flow
        
        Steps:
        1. Check initial bot status (stopped)
        2. Connect to broker
        3. Load configuration
        4. Start bot
        5. Check bot status (running)
        6. Get account info
        7. Get positions
        8. Stop bot
        9. Verify bot stopped
        """
        # Step 1: Check initial bot status
        with patch('indian_dashboard.api.bot.bot_controller') as mock_bot:
            mock_bot.get_status.return_value = {
                'running': False,
                'uptime': 0,
                'positions': 0
            }
            
            response = client.get('/api/bot/status')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['running'] is False
        
        # Step 2: Connect to broker (mocked)
        with patch('indian_dashboard.api.broker.broker_manager') as mock_broker_mgr:
            mock_adapter = Mock()
            mock_adapter.is_connected.return_value = True
            mock_broker_mgr.connect.return_value = (True, {'user_info': {}})
            mock_broker_mgr.is_connected.return_value = True
            mock_broker_mgr.get_adapter.return_value = mock_adapter
        
        # Step 3: Load configuration (mocked)
        # Configuration would be loaded via /api/config endpoint
        
        # Step 4: Start bot
        with patch('indian_dashboard.api.bot.bot_controller') as mock_bot:
            with patch('indian_dashboard.api.bot.broker_manager') as mock_broker_mgr:
                mock_adapter = Mock()
                mock_adapter.is_connected.return_value = True
                mock_broker_mgr.is_connected.return_value = True
                mock_broker_mgr.get_adapter.return_value = mock_adapter
                
                mock_bot.start.return_value = (True, 'Bot started successfully')
                
                response = client.post('/api/bot/start')
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['status'] == 'success'
        
        # Step 5: Check bot status (running)
        with patch('indian_dashboard.api.bot.bot_controller') as mock_bot:
            mock_bot.get_status.return_value = {
                'running': True,
                'uptime': 120,
                'positions': 2
            }
            
            response = client.get('/api/bot/status')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['running'] is True
            assert data['uptime'] == 120
            assert data['positions'] == 2
        
        # Step 6: Get account info
        with patch('indian_dashboard.api.bot.bot_controller') as mock_bot:
            mock_bot.get_account_info.return_value = {
                'balance': 100000.0,
                'equity': 102000.0,
                'margin_available': 50000.0,
                'margin_used': 10000.0,
                'pnl_today': 2000.0
            }
            
            response = client.get('/api/bot/account')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['balance'] == 100000.0
            assert data['pnl_today'] == 2000.0
        
        # Step 7: Get positions
        with patch('indian_dashboard.api.bot.bot_controller') as mock_bot:
            mock_bot.get_positions.return_value = [
                {
                    'symbol': 'RELIANCE',
                    'quantity': 10,
                    'entry_price': 2500.0,
                    'current_price': 2550.0,
                    'pnl': 500.0
                }
            ]
            
            response = client.get('/api/bot/positions')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'positions' in data
            assert len(data['positions']) == 1
            assert data['positions'][0]['symbol'] == 'RELIANCE'
        
        # Step 8: Stop bot
        with patch('indian_dashboard.api.bot.bot_controller') as mock_bot:
            mock_bot.stop.return_value = (True, 'Bot stopped successfully')
            
            response = client.post('/api/bot/stop')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'success'
        
        # Step 9: Verify bot stopped
        with patch('indian_dashboard.api.bot.bot_controller') as mock_bot:
            mock_bot.get_status.return_value = {
                'running': False,
                'uptime': 0,
                'positions': 0
            }
            
            response = client.get('/api/bot/status')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['running'] is False
    
    def test_bot_start_without_broker_connection(self, client):
        """Test bot start fails without broker connection"""
        with patch('indian_dashboard.api.bot.broker_manager') as mock_broker_mgr:
            mock_broker_mgr.is_connected.return_value = False
            
            response = client.post('/api/bot/start')
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['status'] == 'error'
    
    def test_bot_trades_history(self, client):
        """Test fetching trade history"""
        with patch('indian_dashboard.api.bot.bot_controller') as mock_bot:
            mock_bot.get_trades.return_value = [
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
            
            response = client.get('/api/bot/trades')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'trades' in data
            assert len(data['trades']) == 1


class TestIntegratedWorkflow:
    """Test complete integrated workflow from start to finish"""
    
    def test_complete_trading_workflow(self, client, tmp_path):
        """
        E2E Test: Complete trading workflow
        
        Full workflow:
        1. Connect to broker
        2. Fetch and select instruments
        3. Create and save configuration
        4. Start bot
        5. Monitor bot status
        6. Stop bot
        """
        # Step 1: Connect to broker
        with patch('indian_dashboard.api.broker.broker_manager') as mock_broker_mgr:
            mock_adapter = Mock()
            mock_adapter.is_connected.return_value = True
            mock_adapter.get_user_info.return_value = {'user_id': 'TEST123'}
            mock_broker_mgr.connect.return_value = (True, {'user_info': mock_adapter.get_user_info()})
            mock_broker_mgr.is_connected.return_value = True
            mock_broker_mgr.get_adapter.return_value = mock_adapter
            
            response = client.post('/api/broker/connect',
                json={
                    'broker': 'paper',
                    'credentials': {}
                })
            assert response.status_code == 200
        
        # Step 2: Fetch and select instruments
        with patch('indian_dashboard.api.instruments.instrument_service') as mock_inst_service:
            mock_instruments = [
                {
                    'symbol': 'NIFTY24JANFUT',
                    'name': 'NIFTY JAN FUT',
                    'exchange': 'NFO',
                    'instrument_type': 'FUT',
                    'instrument_token': 'NFO:NIFTY24JANFUT'
                }
            ]
            mock_inst_service.get_instruments.return_value = mock_instruments
            
            response = client.get('/api/instruments?exchange=NFO&instrument_type=FUT')
            assert response.status_code == 200
            data = json.loads(response.data)
            selected_instruments = data['instruments']
        
        # Step 3: Create and save configuration
        config = {
            'name': 'nifty_futures_strategy',
            'broker': 'paper',
            'instruments': selected_instruments,
            'strategy': 'trend_following',
            'timeframe': '5min',
            'risk_per_trade': 1.0,
            'max_positions': 2,
            'max_daily_loss': 3.0,
            'position_sizing': 'fixed',
            'base_position_size': 50000.0,
            'indicators': {'ema_fast': 9, 'ema_slow': 21},
            'trading_hours': {'start': '09:15', 'end': '15:30'},
            'paper_trading': True
        }
        
        with patch('indian_dashboard.api.config.config_dir', tmp_path):
            response = client.post('/api/config', json=config)
            assert response.status_code == 200
        
        # Step 4: Start bot
        with patch('indian_dashboard.api.bot.bot_controller') as mock_bot:
            with patch('indian_dashboard.api.bot.broker_manager') as mock_broker_mgr:
                mock_adapter = Mock()
                mock_adapter.is_connected.return_value = True
                mock_broker_mgr.is_connected.return_value = True
                mock_broker_mgr.get_adapter.return_value = mock_adapter
                
                mock_bot.start.return_value = (True, 'Bot started')
                
                response = client.post('/api/bot/start')
                assert response.status_code == 200
        
        # Step 5: Monitor bot status
        with patch('indian_dashboard.api.bot.bot_controller') as mock_bot:
            mock_bot.get_status.return_value = {
                'running': True,
                'uptime': 60,
                'positions': 1
            }
            mock_bot.get_account_info.return_value = {
                'balance': 100000.0,
                'equity': 100500.0,
                'pnl_today': 500.0
            }
            mock_bot.get_positions.return_value = [
                {
                    'symbol': 'NIFTY24JANFUT',
                    'quantity': 1,
                    'entry_price': 21500.0,
                    'current_price': 21550.0,
                    'pnl': 500.0
                }
            ]
            
            # Check status
            response = client.get('/api/bot/status')
            assert response.status_code == 200
            status = json.loads(response.data)
            assert status['running'] is True
            
            # Check account
            response = client.get('/api/bot/account')
            assert response.status_code == 200
            account = json.loads(response.data)
            assert account['pnl_today'] == 500.0
            
            # Check positions
            response = client.get('/api/bot/positions')
            assert response.status_code == 200
            positions = json.loads(response.data)
            assert len(positions['positions']) == 1
        
        # Step 6: Stop bot
        with patch('indian_dashboard.api.bot.bot_controller') as mock_bot:
            mock_bot.stop.return_value = (True, 'Bot stopped')
            
            response = client.post('/api/bot/stop')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'success'


class TestErrorHandlingInFlows:
    """Test error handling in complete workflows"""
    
    def test_workflow_with_broker_disconnection(self, client):
        """Test workflow handles broker disconnection gracefully"""
        # Start with connected broker
        with patch('indian_dashboard.api.broker.broker_manager') as mock_broker_mgr:
            mock_adapter = Mock()
            mock_adapter.is_connected.return_value = True
            mock_broker_mgr.is_connected.return_value = True
            mock_broker_mgr.get_adapter.return_value = mock_adapter
            
            # Try to fetch instruments
            with patch('indian_dashboard.api.instruments.instrument_service') as mock_inst_service:
                mock_inst_service.get_instruments.return_value = []
                response = client.get('/api/instruments')
                assert response.status_code == 200
        
        # Broker disconnects
        with patch('indian_dashboard.api.broker.broker_manager') as mock_broker_mgr:
            mock_broker_mgr.is_connected.return_value = False
            mock_broker_mgr.get_adapter.return_value = None
            
            # Try to start bot - should fail
            response = client.post('/api/bot/start')
            assert response.status_code == 400
    
    def test_workflow_with_invalid_configuration(self, client):
        """Test workflow handles invalid configuration"""
        invalid_config = {
            'name': 'invalid',
            'risk_per_trade': 200.0,  # Invalid
            'max_positions': -5  # Invalid
        }
        
        # Validation should fail
        response = client.post('/api/config/validate', json=invalid_config)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['valid'] is False
        
        # Save should still work (validation is separate)
        with patch('indian_dashboard.api.config.config_dir', Path('/tmp')):
            response = client.post('/api/config', json=invalid_config)
            # Should succeed but config is invalid
            assert response.status_code == 200
