# 🚀 Complete Setup Guide - Fix API Key Error

## Current Error
```json
{"status":"error","message":"Invalid `api_key`.","data":null,"error_type":"InputException"}
```

This error occurs because you need to update your API credentials in **TWO places**.

---

## ✅ Step-by-Step Setup (5 Minutes)

### Step 1: Get Your Kite Connect Credentials (2 minutes)

1. **Go to:** https://kite.trade/
2. **Login** with your Zerodha account
3. **Create or open your app**
4. **Copy TWO things:**
   - **API Key** (shorter string, like: `abc123xyz456`)
   - **API Secret** (longer string, like: `abc123xyz456def789ghi012`)

**Important:** You need BOTH the API Key AND API Secret!

---

### Step 2: Update kite_login.py (1 minute)

Open `kite_login.py` and find these lines (around line 37-39):

**Before:**
```python
API_KEY    = "your_api_key_here"      # From https://developers.kite.trade
API_SECRET = "your_api_secret_here"   # From https://developers.kite.trade
```

**After:**
```python
API_KEY    = "your_actual_api_key"      # From https://developers.kite.trade
API_SECRET = "your_actual_api_secret"   # From https://developers.kite.trade
```

**Save the file!**

---

### Step 3: Update Configuration Files (1 minute)

You have two options:

#### Option A: Automated (Recommended)
```bash
python update_api_key.py
```
- Enter your API Key when prompted
- Script updates all config files automatically

#### Option B: Manual
Edit each config file and replace:
```json
"kite_api_key": "YOUR_KITE_API_KEY_HERE"
```
With:
```json
"kite_api_key": "your_actual_api_key"
```

Files to update:
- `config_nifty_futures.json`
- `config_banknifty_futures.json`
- `config_equity_intraday.json`
- `config_options_trading.json`
- `config_test_paper_trading.json`

---

### Step 4: Update Kite Connect Redirect URL (1 minute)

Since we changed the port to 5001:

1. **Go to:** https://kite.trade/
2. **Open your app** settings
3. **Change Redirect URL to:** `http://127.0.0.1:5001/`
4. **Save** the changes

**Important:** Include the trailing slash `/`

---

### Step 5: Test Authentication (30 seconds)

```bash
python kite_login.py
```

**Expected output:**
```
==============================================================
ZERODHA KITE CONNECT - LOGIN
==============================================================

📋 API Key: abc123xy...
📋 Redirect URL: http://127.0.0.1:5001/

Starting local server and opening browser...
🌐 Opening browser → https://kite.zerodha.com/connect/login?...
⏳ Waiting for you to log in on the browser...
```

**Then:**
1. Browser opens automatically
2. Login with Zerodha credentials + TOTP
3. You'll see "✅ Login Successful!"
4. Token saved to `kite_token.json`

---

## 🎯 Quick Checklist

Before running `python kite_login.py`:

- [ ] Have Zerodha trading account
- [ ] Registered for Kite Connect (₹2,000 fee paid)
- [ ] Created app on https://kite.trade/
- [ ] Copied BOTH API Key and API Secret
- [ ] Updated `kite_login.py` with API Key and API Secret
- [ ] Updated config files with API Key (using `update_api_key.py`)
- [ ] Updated redirect URL to `http://127.0.0.1:5001/` in Kite app
- [ ] Saved all changes

---

## 🔍 Verify Your Setup

### Check kite_login.py
```bash
# Should show your actual API key (first 8 chars)
python -c "import kite_login; print(kite_login.API_KEY[:8])"
```

Should output something like: `abc123xy` (NOT `your_api`)

### Check Configuration Files
```bash
# Should show your actual API key
python -c "import json; print(json.load(open('config_test_paper_trading.json'))['kite_api_key'][:8])"
```

Should output something like: `abc123xy` (NOT `YOUR_KIT`)

---

## 🚨 Common Mistakes

### Mistake 1: Only Updated Config Files
❌ Wrong: Only updated config files, forgot `kite_login.py`
✅ Correct: Update BOTH `kite_login.py` AND config files

### Mistake 2: Used API Secret Instead of API Key
❌ Wrong: Put API Secret in config files
✅ Correct: Use API Key in config files, API Secret only in `kite_login.py`

### Mistake 3: Didn't Update Redirect URL
❌ Wrong: Redirect URL still points to port 5000
✅ Correct: Redirect URL is `http://127.0.0.1:5001/`

### Mistake 4: Forgot to Save Files
❌ Wrong: Edited but didn't save (Ctrl+S)
✅ Correct: Save all files after editing

---

## 📋 What Goes Where

| Credential | kite_login.py | Config Files | Kite App Settings |
|------------|---------------|--------------|-------------------|
| API Key | ✅ Yes | ✅ Yes | ✅ Yes (in app) |
| API Secret | ✅ Yes | ❌ No | ✅ Yes (in app) |
| Redirect URL | ✅ Yes (port 5001) | ❌ No | ✅ Yes (port 5001) |

---

## 🎬 Complete Example

### 1. Your Kite Connect App Settings
```
App Name: My Trading Bot
API Key: abc123xyz456
API Secret: abc123xyz456def789ghi012
Redirect URL: http://127.0.0.1:5001/
```

### 2. Your kite_login.py (lines 37-39)
```python
API_KEY    = "abc123xyz456"
API_SECRET = "abc123xyz456def789ghi012"
TOKEN_FILE = "kite_token.json"
```

### 3. Your config_test_paper_trading.json
```json
{
  "broker": "kite",
  "kite_api_key": "abc123xyz456",
  "kite_token_file": "kite_token.json",
  ...
}
```

---

## 🔧 Automated Setup Script

I've created a script to help you update everything:

```bash
python update_api_key.py
```

This will:
1. Ask for your API Key
2. Update all configuration files
3. Show you what to update in `kite_login.py`
4. Remind you to update Kite Connect app settings

---

## ✅ After Setup is Complete

Once everything is updated:

```bash
# 1. Authenticate (creates daily token)
python kite_login.py

# 2. Verify token was created
dir kite_token.json  # Windows
ls kite_token.json   # Linux/Mac

# 3. Test configuration
python test_configuration.py --config config_test_paper_trading.json

# 4. Start paper trading
python run_bot.py --config config_test_paper_trading.json
```

---

## 🆘 Still Getting Errors?

### Error: "Invalid api_key"

**Possible causes:**
1. API Key is incorrect (typo)
2. API Key not updated in `kite_login.py`
3. API Key not updated in config files
4. Using API Secret instead of API Key

**Solution:**
```bash
# Check kite_login.py
python -c "import kite_login; print('API Key:', kite_login.API_KEY[:8] + '...')"

# Check config file
python -c "import json; c=json.load(open('config_test_paper_trading.json')); print('Config API Key:', c['kite_api_key'][:8] + '...')"

# Both should show your actual API key, not placeholders
```

### Error: "Invalid redirect_uri"

**Possible causes:**
1. Redirect URL not updated in Kite Connect app
2. Redirect URL doesn't match (port mismatch)
3. Missing trailing slash

**Solution:**
1. Login to https://kite.trade/
2. Edit your app
3. Set redirect URL to exactly: `http://127.0.0.1:5001/`
4. Save changes

### Error: "Invalid api_secret"

**Possible causes:**
1. API Secret is incorrect
2. API Secret not updated in `kite_login.py`

**Solution:**
1. Check API Secret in `kite_login.py`
2. Verify it matches your Kite Connect app
3. Copy-paste carefully (no extra spaces)

---

## 📞 Need Help?

### Quick Diagnostics
```bash
# 1. Check if kite_login.py has real credentials
python -c "import kite_login; print('Has real key:', kite_login.API_KEY != 'your_api_key_here')"

# 2. Check if config has real credentials
python -c "import json; c=json.load(open('config_test_paper_trading.json')); print('Has real key:', c['kite_api_key'] != 'YOUR_KITE_API_KEY_HERE')"

# 3. Validate JSON syntax
python -m json.tool config_test_paper_trading.json > nul

# All should return True or no errors
```

### Documentation
- **This Guide:** `COMPLETE_SETUP_GUIDE.md`
- **Port Change:** `PORT_CHANGE_NOTICE.md`
- **API Key Fix:** `FIX_API_KEY_ERROR.md`
- **Quick Start:** `QUICK_START_TESTING.md`

---

## 🎉 Success Indicators

You'll know setup is complete when:

✅ `python kite_login.py` opens browser  
✅ You can login to Kite successfully  
✅ Browser shows "Login Successful!"  
✅ `kite_token.json` file is created  
✅ No "Invalid api_key" errors  
✅ No "Invalid redirect_uri" errors  

---

## 🚀 You're Almost There!

The configurations are deployed and ready. You just need to:

1. ✅ Update API credentials in `kite_login.py`
2. ✅ Update API key in config files
3. ✅ Update redirect URL in Kite Connect app
4. 🚀 Run `python kite_login.py` and start testing!

**Total time: ~5 minutes**

---

*Last Updated: February 17, 2026*  
*Port: 5001 (changed from 5000)*
