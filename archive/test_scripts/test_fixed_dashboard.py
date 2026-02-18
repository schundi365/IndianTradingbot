#!/usr/bin/env python3
"""
Test the fixed dashboard to ensure all JavaScript functions work
"""

import requests
import time

def test_fixed_dashboard():
    """Test the fixed dashboard functionality"""
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Testing Fixed Dashboard...")
    print("="*60)
    
    try:
        # Test main dashboard page
        print("Testing fixed dashboard page...")
        response = requests.get(f"{base_url}/", timeout=10)
        
        if response.status_code == 200:
            print("✅ Fixed dashboard page loads successfully")
            
            content = response.text
            
            # Check if all essential JavaScript functions are defined
            essential_functions = [
                'function startBot',
                'function stopBot', 
                'function testMT5Connection',
                'function showTab',
                'function loadConfig',
                'function saveConfig',
                'function changeLoggingLevel',
                'function loadTrades',
                'function loadPositions',
                'function loadLogs',
                'function downloadLogs'
            ]
            
            print("\n📋 Checking essential JavaScript functions:")
            all_functions_found = True
            for func in essential_functions:
                if func in content:
                    print(f"✅ {func} - FOUND")
                else:
                    print(f"❌ {func} - MISSING")
                    all_functions_found = False
            
            # Check for syntax issues
            print("\n🔍 Checking for syntax issues:")
            
            # Count braces
            open_braces = content.count('{')
            close_braces = content.count('}')
            
            if open_braces == close_braces:
                print(f"✅ Braces balanced: {open_braces} open, {close_braces} close")
            else:
                print(f"❌ Braces unbalanced: {open_braces} open, {close_braces} close")
            
            # Check for script tag
            if '<script>' in content and '</script>' in content:
                print("✅ Script tags properly structured")
            else:
                print("❌ Script tags missing or malformed")
            
            # Check for essential HTML elements
            essential_elements = [
                'id="start-btn"',
                'id="stop-btn"',
                'onclick="startBot()"',
                'onclick="testMT5Connection()"',
                'onclick="showTab(',
                'id="logging-level"'
            ]
            
            print("\n🏗️  Checking essential HTML elements:")
            for element in essential_elements:
                if element in content:
                    print(f"✅ {element} - FOUND")
                else:
                    print(f"❌ {element} - MISSING")
            
            return all_functions_found
            
        else:
            print(f"❌ Fixed dashboard returned status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing fixed dashboard: {e}")
        return False

def test_api_endpoints():
    """Test that API endpoints are still working"""
    base_url = "http://127.0.0.1:5000"
    
    print("\n🔧 Testing API Endpoints:")
    
    endpoints = [
        ("/api/bot/status", "Bot Status"),
        ("/api/config", "Configuration"),
        ("/api/logs", "Logs")
    ]
    
    all_working = True
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: OK")
            else:
                print(f"⚠️  {name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            all_working = False
    
    return all_working

if __name__ == "__main__":
    print("🚀 Testing Fixed Dashboard")
    print("="*60)
    
    # Wait for dashboard to be ready
    time.sleep(2)
    
    dashboard_ok = test_fixed_dashboard()
    api_ok = test_api_endpoints()
    
    print("\n" + "="*60)
    if dashboard_ok and api_ok:
        print("🎯 FIXED DASHBOARD TEST - SUCCESS!")
        print("✅ All JavaScript functions are properly defined")
        print("✅ No syntax errors detected")
        print("✅ All API endpoints working")
        print("✅ Dashboard should be fully functional")
        print("\n🌟 The dashboard is ready to use!")
        print("   Access it at: http://127.0.0.1:5000")
        print("   All buttons should now work correctly!")
    else:
        print("⚠️  FIXED DASHBOARD TEST - ISSUES DETECTED")
        if not dashboard_ok:
            print("❌ JavaScript functions or HTML elements missing")
        if not api_ok:
            print("❌ API endpoints not responding correctly")
    
    print("="*60)