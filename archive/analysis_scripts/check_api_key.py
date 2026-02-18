#!/usr/bin/env python3
"""
API Key Diagnostic Script

Checks if your API key is properly configured.
"""

import sys
import os

print("\n" + "="*70)
print("API KEY DIAGNOSTIC")
print("="*70 + "\n")

# Check which kite_login.py is being used
print("1. Checking kite_login.py location...")
try:
    import kite_login
    print(f"   ✅ Found: {kite_login.__file__}")
except ImportError as e:
    print(f"   ❌ Cannot import kite_login: {e}")
    sys.exit(1)

# Check API key
print("\n2. Checking API_KEY...")
api_key = kite_login.API_KEY
if api_key == "your_api_key_here":
    print(f"   ❌ API_KEY is still placeholder: {api_key}")
    print("   → You need to update API_KEY in kite_login.py")
elif len(api_key) < 10:
    print(f"   ⚠️  API_KEY seems too short: {api_key}")
    print("   → Check if you copied the full API key")
else:
    print(f"   ✅ API_KEY is set: {api_key[:4]}...{api_key[-4:]}")

# Check API secret
print("\n3. Checking API_SECRET...")
api_secret = kite_login.API_SECRET
if api_secret == "your_api_secret_here":
    print(f"   ❌ API_SECRET is still placeholder: {api_secret}")
    print("   → You need to update API_SECRET in kite_login.py")
elif len(api_secret) < 10:
    print(f"   ⚠️  API_SECRET seems too short: {api_secret}")
    print("   → Check if you copied the full API secret")
else:
    print(f"   ✅ API_SECRET is set: {api_secret[:4]}...{api_secret[-4:]}")

# Test KiteConnect initialization
print("\n4. Testing KiteConnect initialization...")
try:
    from kiteconnect import KiteConnect
    kite = KiteConnect(api_key=api_key)
    print(f"   ✅ KiteConnect initialized successfully")
    print(f"   → API Key being used: {api_key[:4]}...{api_key[-4:]}")
except Exception as e:
    print(f"   ❌ Error initializing KiteConnect: {e}")

# Check if API key has spaces or special characters
print("\n5. Checking for common issues...")
issues = []
if ' ' in api_key:
    issues.append("API_KEY contains spaces")
if '\n' in api_key or '\r' in api_key:
    issues.append("API_KEY contains newlines")
if api_key.startswith('"') or api_key.endswith('"'):
    issues.append("API_KEY has extra quotes")

if ' ' in api_secret:
    issues.append("API_SECRET contains spaces")
if '\n' in api_secret or '\r' in api_secret:
    issues.append("API_SECRET contains newlines")
if api_secret.startswith('"') or api_secret.endswith('"'):
    issues.append("API_SECRET has extra quotes")

if issues:
    print("   ⚠️  Issues found:")
    for issue in issues:
        print(f"      • {issue}")
else:
    print("   ✅ No common issues found")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

if api_key != "your_api_key_here" and api_secret != "your_api_secret_here" and not issues:
    print("\n✅ Configuration looks good!")
    print("\nNext steps:")
    print("   1. Make sure redirect URL in Kite app is: http://127.0.0.1:5001/")
    print("   2. Run: python kite_login.py")
    print("   3. Login in the browser that opens")
else:
    print("\n❌ Configuration has issues!")
    print("\nWhat to do:")
    if api_key == "your_api_key_here":
        print("   1. Open kite_login.py in your project directory")
        print(f"      Location: {kite_login.__file__}")
        print("   2. Find line: API_KEY = \"your_api_key_here\"")
        print("   3. Replace with your actual API key from https://kite.trade/")
    if api_secret == "your_api_secret_here":
        print("   4. Find line: API_SECRET = \"your_api_secret_here\"")
        print("   5. Replace with your actual API secret from https://kite.trade/")
    if issues:
        print("   6. Fix the issues listed above")
    print("   7. Save the file and run this script again")

print("\n" + "="*70 + "\n")
