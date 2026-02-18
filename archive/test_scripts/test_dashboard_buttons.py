#!/usr/bin/env python3
"""
Test script to check dashboard button functionality
"""

import requests
import json
import time

def test_dashboard_endpoints():
    """Test all dashboard API endpoints"""
    base_url = "http://127.0.0.1:5000"
    
    endpoints = [
        "/",  # Main dashboard
        "/api/config",  # Configuration
        "/api/bot/status",  # Bot status
        "/api/mt5/test",  # MT5 connection test
        "/api/trades/history",  # Trade history
        "/api/trades/open",  # Open positions
        "/api/analysis/performance",  # Performance analysis
        "/api/logs",  # System logs
    ]
    
    print("🔍 Testing Dashboard Endpoints...")
    print("=" * 50)
    
    for endpoint in endpoints:
        try:
            url = base_url + endpoint
            response = requests.get(url, timeout=10)
            
            if endpoint == "/":
                # For main page, just check if HTML is returned
                status = "✅ OK" if response.status_code == 200 and "html" in response.text.lower() else "❌ FAILED"
                print(f"{endpoint:<25} {response.status_code} {status}")
            else:
                # For API endpoints, check JSON response
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"{endpoint:<25} {response.status_code} ✅ OK")
                    except json.JSONDecodeError:
                        print(f"{endpoint:<25} {response.status_code} ⚠️  Non-JSON response")
                else:
                    print(f"{endpoint:<25} {response.status_code} ❌ FAILED")
                    
        except requests.exceptions.RequestException as e:
            print(f"{endpoint:<25} ❌ CONNECTION ERROR: {str(e)}")
        except Exception as e:
            print(f"{endpoint:<25} ❌ ERROR: {str(e)}")
    
    print("=" * 50)
    print("✅ Dashboard endpoint testing complete!")

def test_button_functions():
    """Test specific button functionality"""
    base_url = "http://127.0.0.1:5000"
    
    print("\n🔘 Testing Button Functions...")
    print("=" * 50)
    
    # Test MT5 connection
    try:
        response = requests.get(f"{base_url}/api/mt5/test", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"MT5 Test Button:          ✅ {'Connected' if data.get('connected') else 'Not Connected'}")
        else:
            print(f"MT5 Test Button:          ❌ HTTP {response.status_code}")
    except Exception as e:
        print(f"MT5 Test Button:          ❌ {str(e)}")
    
    # Test configuration loading
    try:
        response = requests.get(f"{base_url}/api/config", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"Config Load Button:       ✅ {len(data)} config items loaded")
        else:
            print(f"Config Load Button:       ❌ HTTP {response.status_code}")
    except Exception as e:
        print(f"Config Load Button:       ❌ {str(e)}")
    
    # Test bot status
    try:
        response = requests.get(f"{base_url}/api/bot/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"Bot Status Button:        ✅ Running: {data.get('running', False)}")
        else:
            print(f"Bot Status Button:        ❌ HTTP {response.status_code}")
    except Exception as e:
        print(f"Bot Status Button:        ❌ {str(e)}")
    
    print("=" * 50)

def check_javascript_functions():
    """Check if JavaScript functions are properly defined in the HTML"""
    print("\n📜 Checking JavaScript Functions...")
    print("=" * 50)
    
    try:
        response = requests.get("http://127.0.0.1:5000", timeout=10)
        if response.status_code == 200:
            html_content = response.text
            
            # List of critical JavaScript functions
            critical_functions = [
                "startBot",
                "stopBot", 
                "restartBot",
                "testMT5Connection",
                "showTab",
                "toggleAccordion",
                "loadPreset",
                "refreshDashboard",
                "refreshConfig",
                "selectSymbolGroup",
                "checkSymbolDataAvailability"
            ]
            
            missing_functions = []
            for func in critical_functions:
                if f"function {func}" in html_content:
                    print(f"{func:<25} ✅ Found")
                else:
                    print(f"{func:<25} ❌ Missing")
                    missing_functions.append(func)
            
            if missing_functions:
                print(f"\n⚠️  Missing functions: {', '.join(missing_functions)}")
            else:
                print(f"\n✅ All critical JavaScript functions found!")
                
        else:
            print(f"❌ Failed to load dashboard HTML: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking JavaScript: {str(e)}")
    
    print("=" * 50)

if __name__ == "__main__":
    print("🚀 DASHBOARD BUTTON DIAGNOSTIC TEST")
    print("=" * 60)
    
    # Wait a moment for server to be ready
    time.sleep(1)
    
    test_dashboard_endpoints()
    test_button_functions()
    check_javascript_functions()
    
    print("\n💡 TROUBLESHOOTING TIPS:")
    print("=" * 60)
    print("1. If endpoints are failing: Check if dashboard server is running")
    print("2. If JavaScript functions are missing: Check browser console for errors")
    print("3. If buttons don't respond: Clear browser cache and refresh")
    print("4. If MT5 test fails: Make sure MT5 is running and logged in")
    print("5. Try accessing: http://127.0.0.1:5000 in your browser")
    print("=" * 60)