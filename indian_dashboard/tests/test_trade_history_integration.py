"""
Integration tests for Trade History functionality
"""

import pytest
import json
from datetime import datetime, timedelta


def test_trades_endpoint_returns_trades(client, mock_broker_manager, mock_bot_controller):
    """Test that /api/bot/trades endpoint returns trade data"""
    # Mock trades data
    mock_trades = [
        {
            'timestamp': datetime.now().isoformat(),
            'symbol': 'RELIANCE',
            'transaction_type': 'BUY',
            'quantity': 10,
            'price': 2500.50,
            'exit_price': 2550.75,
            'pnl': 502.50
        },
        {
            'timestamp': (datetime.now() - timedelta(days=1)).isoformat(),
            'symbol': 'TCS',
            'transaction_type': 'SELL',
            'quantity': 5,
            'price': 3200.00,
            'exit_price': 3150.00,
            'pnl': 250.00
        }
    ]
    
    mock_bot_controller.get_trades.return_value = mock_trades
    
    # Make request
    response = client.get('/api/bot/trades')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['success'] is True
    assert 'trades' in data
    assert len(data['trades']) == 2
    assert data['count'] == 2


def test_trades_endpoint_with_date_filter(client, mock_broker_manager, mock_bot_controller):
    """Test that /api/bot/trades endpoint filters by date"""
    # Mock trades data
    mock_trades = [
        {
            'timestamp': datetime.now().isoformat(),
            'symbol': 'RELIANCE',
            'transaction_type': 'BUY',
            'quantity': 10,
            'price': 2500.50
        }
    ]
    
    mock_bot_controller.get_trades.return_value = mock_trades
    
    # Make request with date filters
    from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    to_date = datetime.now().strftime('%Y-%m-%d')
    
    response = client.get(f'/api/bot/trades?from_date={from_date}&to_date={to_date}')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['success'] is True
    # Verify that get_trades was called with date parameters
    mock_bot_controller.get_trades.assert_called_once_with(from_date, to_date)


def test_trades_endpoint_empty_trades(client, mock_broker_manager, mock_bot_controller):
    """Test that /api/bot/trades endpoint handles empty trades"""
    mock_bot_controller.get_trades.return_value = []
    
    response = client.get('/api/bot/trades')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['success'] is True
    assert data['trades'] == []
    assert data['count'] == 0


def test_trades_endpoint_error_handling(client, mock_broker_manager, mock_bot_controller):
    """Test that /api/bot/trades endpoint handles errors gracefully"""
    mock_bot_controller.get_trades.side_effect = Exception('Database error')
    
    response = client.get('/api/bot/trades')
    
    assert response.status_code == 500
    data = json.loads(response.data)
    
    assert data['success'] is False
    assert 'error' in data


def test_trade_data_structure(client, mock_broker_manager, mock_bot_controller):
    """Test that trade data has correct structure"""
    mock_trades = [
        {
            'timestamp': datetime.now().isoformat(),
            'symbol': 'RELIANCE',
            'transaction_type': 'BUY',
            'quantity': 10,
            'price': 2500.50,
            'exit_price': 2550.75,
            'pnl': 502.50
        }
    ]
    
    mock_bot_controller.get_trades.return_value = mock_trades
    
    response = client.get('/api/bot/trades')
    data = json.loads(response.data)
    
    trade = data['trades'][0]
    
    # Verify all required fields are present
    assert 'timestamp' in trade
    assert 'symbol' in trade
    assert 'transaction_type' in trade
    assert 'quantity' in trade
    assert 'price' in trade
    assert 'exit_price' in trade
    assert 'pnl' in trade


def test_trade_sorting_by_date(client, mock_broker_manager, mock_bot_controller):
    """Test that trades can be sorted by date"""
    now = datetime.now()
    mock_trades = [
        {
            'timestamp': (now - timedelta(days=2)).isoformat(),
            'symbol': 'RELIANCE',
            'transaction_type': 'BUY',
            'quantity': 10,
            'price': 2500.50
        },
        {
            'timestamp': now.isoformat(),
            'symbol': 'TCS',
            'transaction_type': 'SELL',
            'quantity': 5,
            'price': 3200.00
        },
        {
            'timestamp': (now - timedelta(days=1)).isoformat(),
            'symbol': 'INFY',
            'transaction_type': 'BUY',
            'quantity': 15,
            'price': 1500.00
        }
    ]
    
    mock_bot_controller.get_trades.return_value = mock_trades
    
    response = client.get('/api/bot/trades')
    data = json.loads(response.data)
    
    # Verify trades are returned (sorting will be done on frontend)
    assert len(data['trades']) == 3


def test_trade_pnl_calculation(client, mock_broker_manager, mock_bot_controller):
    """Test that P&L is correctly included in trade data"""
    mock_trades = [
        {
            'timestamp': datetime.now().isoformat(),
            'symbol': 'RELIANCE',
            'transaction_type': 'BUY',
            'quantity': 10,
            'price': 2500.00,
            'exit_price': 2550.00,
            'pnl': 500.00  # (2550 - 2500) * 10
        },
        {
            'timestamp': datetime.now().isoformat(),
            'symbol': 'TCS',
            'transaction_type': 'SELL',
            'quantity': 5,
            'price': 3200.00,
            'exit_price': 3150.00,
            'pnl': 250.00  # (3200 - 3150) * 5
        }
    ]
    
    mock_bot_controller.get_trades.return_value = mock_trades
    
    response = client.get('/api/bot/trades')
    data = json.loads(response.data)
    
    # Verify P&L values
    assert data['trades'][0]['pnl'] == 500.00
    assert data['trades'][1]['pnl'] == 250.00


def test_trade_pagination_support(client, mock_broker_manager, mock_bot_controller):
    """Test that API returns all trades for frontend pagination"""
    # Generate 50 mock trades
    mock_trades = []
    for i in range(50):
        mock_trades.append({
            'timestamp': (datetime.now() - timedelta(days=i)).isoformat(),
            'symbol': f'STOCK{i}',
            'transaction_type': 'BUY' if i % 2 == 0 else 'SELL',
            'quantity': 10,
            'price': 1000.00 + i
        })
    
    mock_bot_controller.get_trades.return_value = mock_trades
    
    response = client.get('/api/bot/trades')
    data = json.loads(response.data)
    
    # Verify all trades are returned (pagination handled on frontend)
    assert len(data['trades']) == 50
    assert data['count'] == 50


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
