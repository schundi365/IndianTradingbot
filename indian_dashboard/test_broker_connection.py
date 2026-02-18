"""
Test script for broker connection functionality
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from services.broker_manager import BrokerManager

def test_broker_manager():
    """Test BrokerManager functionality"""
    print("Testing BrokerManager...")
    
    # Create broker manager
    manager = BrokerManager()
    
    # Test 1: Get supported brokers
    print("\n1. Testing get_supported_brokers()...")
    brokers = manager.get_supported_brokers()
    print(f"   Found {len(brokers)} supported brokers:")
    for broker in brokers:
        print(f"   - {broker['name']} (ID: {broker['id']})")
    
    # Test 2: Get credentials form
    print("\n2. Testing get_credentials_form()...")
    for broker in brokers:
        form = manager.get_credentials_form(broker['id'])
        print(f"   {broker['name']} requires {len(form)} fields:")
        for field in form:
            print(f"     - {field.get('label', field.get('name'))}")
    
    # Test 3: Test connection status
    print("\n3. Testing get_status()...")
    status = manager.get_status()
    print(f"   Connected: {status['connected']}")
    print(f"   Broker: {status['broker']}")
    
    # Test 4: Test connection (should fail without credentials)
    print("\n4. Testing test_connection()...")
    success, message = manager.test_connection()
    print(f"   Success: {success}")
    print(f"   Message: {message}")
    
    print("\n✅ All tests completed!")

if __name__ == '__main__':
    test_broker_manager()
