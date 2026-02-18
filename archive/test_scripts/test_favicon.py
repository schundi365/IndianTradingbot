#!/usr/bin/env python3
"""
Test the favicon route specifically
"""

import requests
import time

def test_favicon():
    """Test the favicon endpoint"""
    base_url = "http://127.0.0.1:5000"
    
    print("🔍 Testing Favicon Route...")
    print("="*40)
    
    try:
        # Test favicon endpoint
        print("Testing /favicon.ico endpoint...")
        response = requests.get(f"{base_url}/favicon.ico", timeout=5)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'unknown')}")
        print(f"Content-Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            print("✅ Favicon endpoint is working!")
            if 'svg' in response.headers.get('Content-Type', ''):
                print("✅ Returning SVG favicon as expected")
            else:
                print("⚠️  Not returning SVG content type")
        else:
            print(f"❌ Favicon endpoint returned {response.status_code}")
            print("Response content:", response.text[:200])
            
    except Exception as e:
        print(f"❌ Error testing favicon: {e}")
    
    # Test if Flask routes are being registered
    try:
        print("\nTesting route registration...")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Main route working - Flask app is running")
        else:
            print(f"❌ Main route returned {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing main route: {e}")

if __name__ == "__main__":
    print("🚀 Favicon Route Test")
    print("="*40)
    
    # Wait for server to be ready
    time.sleep(1)
    
    test_favicon()
    
    print("="*40)
    print("💡 If favicon still shows 404:")
    print("  1. Check Flask route registration")
    print("  2. Restart the web dashboard")
    print("  3. Clear browser cache")
    print("="*40)