import requests
import json
import time

def start_bot():
    url = "http://127.0.0.1:8080/api/bot/start"
    config = {
        "symbols": ["RELIANCE", "TCS", "INFY"],
        "timeframe": 15,
        "paper_trading": True,
        "allow_after_hours": True,
        "risk_percent": 1.0,
        "strategy": "trend_following"
    }
    
    payload = {"config": config}
    
    try:
        print(f"Starting bot with config: {json.dumps(config, indent=2)}")
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    if start_bot():
        print("Bot started successfully. Waiting for some cycles...")
        time.sleep(30)
        # Check logs
        import os
        os.system("python check_detailed_logs.py")
    else:
        print("Failed to start bot.")
