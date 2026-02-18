#!/usr/bin/env python3
"""
Check Dashboard API for MACD histogram value
"""

import requests
import json

try:
    response = requests.get("http://localhost:5000/api/config", timeout=5)
    if response.status_code == 200:
        config = response.json()
        macd_value = config.get('macd_min_histogram', 'NOT_FOUND')
        print(f"Dashboard API MACD histogram: {macd_value}")
        
        # Show full config for debugging
        print("\nFull config from API:")
        print(json.dumps(config, indent=2))
    else:
        print(f"API returned status: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"Error connecting to dashboard API: {e}")