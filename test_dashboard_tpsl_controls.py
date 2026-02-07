"""
Test Dashboard TP/SL Controls
==============================
Verify that the new pip-based TP/SL controls work correctly
"""

import json
import requests
import time

DASHBOARD_URL = "http://localhost:5000"

def test_config_api():
    """Test the configuration API with pip-based TP/SL settings"""
    
    print("="*70)
    print("TESTING DASHBOARD TP/SL CONTROLS")
    print("="*70)
    
    # Test 1: Get current config
    print("\n1. Getting current configuration...")
    try:
        response = requests.get(f"{DASHBOARD_URL}/api/config", timeout=5)
        if response.status_code == 200:
            config = response.json()
            print("✓ Current config retrieved")
            print(f"  use_pip_based_sl: {config.get('use_pip_based_sl', 'NOT SET')}")
            print(f"  sl_pips: {config.get('sl_pips', 'NOT SET')}")
            print(f"  use_pip_based_tp: {config.get('use_pip_based_tp', 'NOT SET')}")
            print(f"  tp_pips: {config.get('tp_pips', 'NOT SET')}")
        else:
            print(f"❌ Failed to get config: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Dashboard not running. Start it with: python web_dashboard.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Try to save inconsistent config (should fail)
    print("\n2. Testing inconsistent method validation...")
    test_config = config.copy()
    test_config['use_pip_based_sl'] = False  # ATR-based
    test_config['use_pip_based_tp'] = True   # Pip-based
    
    response = requests.post(f"{DASHBOARD_URL}/api/config", json=test_config, timeout=5)
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 'error':
            print("✓ Inconsistent methods correctly rejected")
            print(f"  Error message: {result['message']}")
        else:
            print("❌ Inconsistent methods should have been rejected!")
            return False
    else:
        print(f"❌ Unexpected response: {response.status_code}")
        return False
    
    # Test 3: Save valid pip-based config
    print("\n3. Testing valid pip-based configuration...")
    test_config = config.copy()
    test_config['use_pip_based_sl'] = True
    test_config['sl_pips'] = 50
    test_config['use_pip_based_tp'] = True
    test_config['tp_pips'] = 100
    
    response = requests.post(f"{DASHBOARD_URL}/api/config", json=test_config, timeout=5)
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 'success':
            print("✓ Valid pip-based config saved successfully")
            print(f"  Message: {result['message']}")
        else:
            print(f"❌ Failed to save: {result.get('message', 'Unknown error')}")
            return False
    else:
        print(f"❌ Unexpected response: {response.status_code}")
        return False
    
    # Test 4: Verify config was saved
    print("\n4. Verifying saved configuration...")
    response = requests.get(f"{DASHBOARD_URL}/api/config", timeout=5)
    if response.status_code == 200:
        config = response.json()
        if (config.get('use_pip_based_sl') == True and 
            config.get('sl_pips') == 50 and
            config.get('use_pip_based_tp') == True and
            config.get('tp_pips') == 100):
            print("✓ Configuration verified in API")
            print(f"  SL: {config['sl_pips']} pips")
            print(f"  TP: {config['tp_pips']} pips")
        else:
            print("❌ Configuration not saved correctly")
            return False
    
    # Test 5: Check bot_config.json
    print("\n5. Verifying bot_config.json...")
    try:
        with open('bot_config.json', 'r') as f:
            file_config = json.load(f)
        
        if (file_config.get('use_pip_based_sl') == True and 
            file_config.get('sl_pips') == 50 and
            file_config.get('use_pip_based_tp') == True and
            file_config.get('tp_pips') == 100):
            print("✓ Configuration verified in bot_config.json")
        else:
            print("❌ bot_config.json not updated correctly")
            return False
    except Exception as e:
        print(f"❌ Error reading bot_config.json: {e}")
        return False
    
    # Test 6: Test range validation
    print("\n6. Testing range validation...")
    test_config = config.copy()
    test_config['use_pip_based_sl'] = True
    test_config['sl_pips'] = 5  # Too low
    
    response = requests.post(f"{DASHBOARD_URL}/api/config", json=test_config, timeout=5)
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 'error' and 'between 10 and 500' in result['message']:
            print("✓ Range validation working (SL too low rejected)")
        else:
            print("❌ Range validation should have rejected SL=5")
            return False
    
    # Test 7: Test TP > SL validation
    print("\n7. Testing TP > SL validation...")
    test_config = config.copy()
    test_config['use_pip_based_sl'] = True
    test_config['sl_pips'] = 100
    test_config['use_pip_based_tp'] = True
    test_config['tp_pips'] = 50  # Less than SL
    
    response = requests.post(f"{DASHBOARD_URL}/api/config", json=test_config, timeout=5)
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 'error' and 'must be greater than' in result['message']:
            print("✓ TP > SL validation working")
        else:
            print("❌ Should have rejected TP < SL")
            return False
    
    print("\n" + "="*70)
    print("✓ ALL TESTS PASSED")
    print("="*70)
    print("\nDashboard TP/SL controls are working correctly!")
    print("\nNext steps:")
    print("1. Open dashboard: http://localhost:5000")
    print("2. Go to Configuration tab")
    print("3. Scroll to 'TP/SL Calculation Method' section")
    print("4. Test the controls manually")
    print("5. Save and restart bot")
    
    return True

def check_dashboard_running():
    """Check if dashboard is running"""
    try:
        response = requests.get(DASHBOARD_URL, timeout=2)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    if not check_dashboard_running():
        print("="*70)
        print("DASHBOARD NOT RUNNING")
        print("="*70)
        print("\nPlease start the dashboard first:")
        print("  python web_dashboard.py")
        print("\nThen run this test again.")
    else:
        test_config_api()
