#!/usr/bin/env python3
"""
Test Dashboard Connection

Quick test to verify the web dashboard is accessible and working.
"""

import requests
import time

def test_dashboard_connection():
    """Test if the dashboard is accessible"""
    print("🌐 Testing Web Dashboard Connection...")
    print("="*50)
    
    dashboard_url = "http://127.0.0.1:5000"
    
    try:
        # Test main dashboard page
        print(f"📡 Connecting to {dashboard_url}...")
        response = requests.get(dashboard_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Dashboard is accessible!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response Size: {len(response.content)} bytes")
            
            # Check if it contains expected content
            if "GEM Trading Bot" in response.text or "Dashboard" in response.text:
                print("✅ Dashboard content looks correct")
            else:
                print("⚠️ Dashboard content may be incomplete")
                
        else:
            print(f"❌ Dashboard returned status code: {response.status_code}")
            return False
            
        # Test API endpoints
        print("\n🔍 Testing API endpoints...")
        
        api_endpoints = [
            "/api/bot/status",
            "/api/config",
            "/api/analysis/performance"
        ]
        
        for endpoint in api_endpoints:
            try:
                api_response = requests.get(f"{dashboard_url}{endpoint}", timeout=5)
                if api_response.status_code == 200:
                    print(f"✅ {endpoint} - OK")
                else:
                    print(f"⚠️ {endpoint} - Status: {api_response.status_code}")
            except Exception as e:
                print(f"❌ {endpoint} - Error: {str(e)[:50]}...")
        
        print("\n🎉 Dashboard Connection Test Complete!")
        print(f"🌐 Access your dashboard at: {dashboard_url}")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to dashboard!")
        print("   Dashboard may not be running or port 5000 is blocked")
        return False
    except requests.exceptions.Timeout:
        print("❌ Dashboard connection timed out!")
        print("   Dashboard may be starting up or overloaded")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Dashboard Connection Test")
    print("="*50)
    
    # Give dashboard a moment to fully start
    print("⏳ Waiting for dashboard to fully initialize...")
    time.sleep(3)
    
    success = test_dashboard_connection()
    
    if success:
        print("\n✅ DASHBOARD IS WORKING!")
        print("You can now access the web interface.")
    else:
        print("\n❌ DASHBOARD CONNECTION FAILED!")
        print("Check if the dashboard process is running.")