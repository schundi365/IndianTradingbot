"""
Integration test for broker status display
Tests the complete flow from backend to frontend
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.broker_manager import BrokerManager


def test_broker_status_structure():
    """Test that broker status returns all required fields"""
    broker_manager = BrokerManager()
    
    # Test disconnected status
    status = broker_manager.get_status()
    
    assert 'connected' in status
    assert 'broker' in status
    assert 'user_info' in status
    assert 'connection_time' in status
    assert 'access_token' in status
    assert 'token_expiry' in status
    
    assert status['connected'] == False
    assert status['broker'] is None
    assert status['user_info'] == {}
    assert status['connection_time'] is None
    
    print("✓ Disconnected status structure is correct")


def test_broker_status_after_connection():
    """Test broker status after simulated connection"""
    broker_manager = BrokerManager()
    
    # Simulate connection by setting internal state
    broker_manager.current_broker_type = 'kite'
    broker_manager.connection_time = datetime.now()
    broker_manager.user_info = {
        'user_id': 'TEST123',
        'user_name': 'Test User',
        'email': 'test@example.com',
        'broker': 'ZERODHA'
    }
    
    # Mock the is_connected method to return True
    class MockAdapter:
        def is_connected(self):
            return True
    
    broker_manager.current_broker = MockAdapter()
    
    # Get status
    status = broker_manager.get_status()
    
    # Verify all required fields are present
    assert status['connected'] == True
    assert status['broker'] == 'kite'
    assert status['user_info']['user_id'] == 'TEST123'
    assert status['user_info']['user_name'] == 'Test User'
    assert status['user_info']['email'] == 'test@example.com'
    assert status['connection_time'] is not None
    
    print("✓ Connected status structure is correct")
    print(f"  - Broker: {status['broker']}")
    print(f"  - User ID: {status['user_info']['user_id']}")
    print(f"  - User Name: {status['user_info']['user_name']}")
    print(f"  - Connection Time: {status['connection_time']}")


def test_broker_status_with_token():
    """Test broker status with OAuth token information"""
    broker_manager = BrokerManager()
    
    # Simulate OAuth connection
    broker_manager.current_broker_type = 'kite'
    broker_manager.connection_time = datetime.now()
    broker_manager.user_info = {
        'user_id': 'OAUTH123',
        'user_name': 'OAuth User'
    }
    broker_manager.access_token = 'test_access_token_12345'
    broker_manager.token_expiry = (datetime.now() + timedelta(hours=12)).strftime('%Y-%m-%d %H:%M:%S')
    
    # Mock adapter
    class MockAdapter:
        def is_connected(self):
            return True
    
    broker_manager.current_broker = MockAdapter()
    
    # Get status
    status = broker_manager.get_status()
    
    # Verify token fields
    assert status['access_token'] == 'test_access_token_12345'
    assert status['token_expiry'] is not None
    
    print("✓ OAuth token information is included in status")
    print(f"  - Access Token: {status['access_token'][:20]}...")
    print(f"  - Token Expiry: {status['token_expiry']}")


def test_connection_time_format():
    """Test that connection time is in ISO format"""
    broker_manager = BrokerManager()
    
    # Set connection time
    now = datetime.now()
    broker_manager.current_broker_type = 'kite'
    broker_manager.connection_time = now
    broker_manager.user_info = {'user_id': 'TEST'}
    
    # Mock adapter
    class MockAdapter:
        def is_connected(self):
            return True
    
    broker_manager.current_broker = MockAdapter()
    
    # Get status
    status = broker_manager.get_status()
    
    # Verify ISO format
    connection_time_str = status['connection_time']
    assert connection_time_str is not None
    
    # Parse back to datetime to verify format
    parsed_time = datetime.fromisoformat(connection_time_str)
    assert parsed_time.year == now.year
    assert parsed_time.month == now.month
    assert parsed_time.day == now.day
    
    print("✓ Connection time is in ISO format")
    print(f"  - Connection Time: {connection_time_str}")


def test_user_info_fields():
    """Test that all user info fields are properly included"""
    broker_manager = BrokerManager()
    
    # Set comprehensive user info
    broker_manager.current_broker_type = 'kite'
    broker_manager.connection_time = datetime.now()
    broker_manager.user_info = {
        'user_id': 'USER123',
        'user_name': 'Full Name',
        'email': 'user@example.com',
        'broker': 'ZERODHA',
        'phone': '+91-9876543210'
    }
    
    # Mock adapter
    class MockAdapter:
        def is_connected(self):
            return True
    
    broker_manager.current_broker = MockAdapter()
    
    # Get status
    status = broker_manager.get_status()
    
    # Verify all user info fields
    user_info = status['user_info']
    assert user_info['user_id'] == 'USER123'
    assert user_info['user_name'] == 'Full Name'
    assert user_info['email'] == 'user@example.com'
    assert user_info['broker'] == 'ZERODHA'
    assert user_info['phone'] == '+91-9876543210'
    
    print("✓ All user info fields are preserved")
    print(f"  - Fields: {list(user_info.keys())}")


if __name__ == '__main__':
    print("Testing Broker Status Display Integration\n")
    print("=" * 60)
    
    try:
        test_broker_status_structure()
        print()
        
        test_broker_status_after_connection()
        print()
        
        test_broker_status_with_token()
        print()
        
        test_connection_time_format()
        print()
        
        test_user_info_fields()
        print()
        
        print("=" * 60)
        print("\n✅ All broker status display tests passed!")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
