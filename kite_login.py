"""
kite_login.py
=============
Handles Zerodha Kite Connect OAuth login for a bot running on your PC.

HOW IT WORKS:
  1. Opens browser → Kite login page
  2. You log in with Zerodha credentials + TOTP
  3. Kite redirects to http://127.0.0.1:5001/?request_token=xxxxx
  4. This script catches that token automatically
  5. Exchanges it for an access_token
  6. Saves access_token to kite_token.json
  7. Your trading bot reads kite_token.json to authenticate

SETUP:
  pip install kiteconnect flask pyotp

USAGE:
  1. Set API_KEY and API_SECRET below
  2. Run: python kite_login.py
  3. Browser opens → log in → done!
  4. Then run your trading bot
"""

import os
import json
import webbrowser
import threading
import time
from datetime import datetime
from pathlib import Path

from kiteconnect import KiteConnect
from flask import Flask, request

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ─── YOUR CREDENTIALS ────────────────────────────────────────────────────────
# Load from environment variables, or fallback to hardcoded defaults
API_KEY    = os.getenv("KITE_API_KEY", "l2b10dmr6dfo1bqb")
API_SECRET = os.getenv("KITE_API_SECRET", "iayptx4r7931x3v36rkj135p3afk2nr8")
TOKEN_FILE = "kite_token.json"        # Where to save the access token
# ─────────────────────────────────────────────────────────────────────────────

app = Flask(__name__)
kite = KiteConnect(api_key=API_KEY)
_token_received = threading.Event()


@app.route("/")
def catch_redirect():
    """
    Kite redirects here after login:
      http://127.0.0.1:5001/?request_token=xxxxx&status=success
    """
    request_token = request.args.get("request_token")
    status        = request.args.get("status")

    if status != "success" or not request_token:
        error = request.args.get("message", "Unknown error")
        return f"<h2>❌ Login failed: {error}</h2>", 400

    try:
        # Exchange request_token for access_token
        data = kite.generate_session(request_token, api_secret=API_SECRET)
        access_token = data["access_token"]
        kite.set_access_token(access_token)

        # Save token to file
        token_data = {
            "access_token": access_token,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().isoformat()
        }
        with open(TOKEN_FILE, "w") as f:
            json.dump(token_data, f, indent=2)

        print(f"\n✅ Login successful!")
        print(f"   Access token saved to {TOKEN_FILE}")
        print(f"   Token (first 10 chars): {access_token[:10]}...")
        print(f"\n   You can now run your trading bot!")

        _token_received.set()  # Signal main thread we're done

        return """
        <html>
        <body style="font-family:Arial; text-align:center; padding:50px;">
            <h1>✅ Login Successful!</h1>
            <p>Access token has been saved.</p>
            <p>You can close this browser tab and run your trading bot.</p>
            <script>setTimeout(() => window.close(), 3000);</script>
        </body>
        </html>
        """

    except Exception as e:
        print(f"\n❌ Error generating session: {e}")
        return f"<h2>❌ Error: {e}</h2>", 500


def open_browser_after_delay(url, delay=1.5):
    """Opens browser after Flask server is ready"""
    time.sleep(delay)
    print(f"\n🌐 Opening browser → {url}")
    webbrowser.open(url)


def login():
    """Main login function"""
    print("=" * 60)
    print("ZERODHA KITE CONNECT - LOGIN")
    print("=" * 60)

    # Check if today's token already exists
    token_path = Path(TOKEN_FILE)
    if token_path.exists():
        with open(TOKEN_FILE) as f:
            saved = json.load(f)
        if saved.get("date") == datetime.now().strftime("%Y-%m-%d"):
            print(f"\n✅ Already logged in today!")
            print(f"   Using saved token from {TOKEN_FILE}")
            print(f"   Token valid until 6:00 AM tomorrow.")
            return saved["access_token"]

    print(f"\n📋 API Key: {API_KEY[:8]}...")
    print(f"📋 Redirect URL: http://127.0.0.1:5001/")
    print(f"\nStarting local server and opening browser...")

    # Generate login URL
    login_url = kite.login_url()

    # Open browser after server starts
    browser_thread = threading.Thread(
        target=open_browser_after_delay,
        args=(login_url,),
        daemon=True
    )
    browser_thread.start()

    # Start Flask server (runs until token received)
    server_thread = threading.Thread(
        target=lambda: app.run(
            host="127.0.0.1",
            port=5001,
            debug=False,
            use_reloader=False
        ),
        daemon=True
    )
    server_thread.start()

    print("\n⏳ Waiting for you to log in on the browser...")
    print("   (Log in with your Zerodha credentials + TOTP)")

    # Wait for login to complete (timeout 5 minutes)
    if _token_received.wait(timeout=300):
        with open(TOKEN_FILE) as f:
            return json.load(f)["access_token"]
    else:
        print("\n❌ Login timed out after 5 minutes")
        return None


def get_access_token():
    """
    Use this in your trading bot to get a valid access token.
    Automatically handles login if no valid token exists.
    """
    token_path = Path(TOKEN_FILE)

    # Check if we have today's token
    if token_path.exists():
        with open(TOKEN_FILE) as f:
            saved = json.load(f)
        if saved.get("date") == datetime.now().strftime("%Y-%m-%d"):
            return saved["access_token"]

    # No valid token — need to log in
    print("No valid token found. Starting login process...")
    return login()


if __name__ == "__main__":
    token = login()
    if token:
        print(f"\n🎉 Ready to trade!")
        print(f"   Run your bot: python kite_trading_bot.py")
