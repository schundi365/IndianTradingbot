# Fix: Invalid API Key Error

## Error Message
```json
{"status":"error","message":"Invalid `api_key`.","data":null,"error_type":"InputException"}
```

## What This Means
The configuration file still has the placeholder API key `"YOUR_KITE_API_KEY_HERE"` instead of your actual Kite Connect API key.

---

## ✅ Quick Fix (2 Minutes)

### Step 1: Get Your Kite API Key

1. Go to: https://kite.trade/
2. Login to your Zerodha account
3. Click on "Create new app" or use existing app
4. Copy your **API Key** (looks like: `xxxxxxxxxxxxxx`)

**Note:** You need a Zerodha trading account to get an API key.

### Step 2: Update Configuration File

Open the configuration file you're using (e.g., `config_test_paper_trading.json`):

**Before (with placeholder):**
```json
{
  "kite_api_key": "YOUR_KITE_API_KEY_HERE",
  ...
}
```

**After (with your actual key):**
```json
{
  "kite_api_key": "your_actual_api_key_here",
  ...
}
```

### Step 3: Save and Retry

Save the file and run your command again:

```bash
python kite_login.py
```

---

## 📝 Update All Configuration Files

If you plan to use multiple configurations, update the API key in all of them:

```bash
# Windows PowerShell
Get-ChildItem -Filter "config_*.json" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $content = $content -replace '"YOUR_KITE_API_KEY_HERE"', '"your_actual_api_key_here"'
    Set-Content $_.FullName $content
}
```

Or manually edit each file:
- `config_nifty_futures.json`
- `config_banknifty_futures.json`
- `config_equity_intraday.json`
- `config_options_trading.json`
- `config_test_paper_trading.json`

---

## 🔐 Don't Have a Kite API Key?

### Option 1: Get Kite Connect API Key (Recommended)

**Requirements:**
- Active Zerodha trading account
- One-time setup fee: ₹2,000 (for API access)

**Steps:**
1. Visit: https://kite.trade/
2. Login with Zerodha credentials
3. Create a new app
4. Get your API key and API secret
5. Use API key in configuration

### Option 2: Use Paper Trading Without Real API

If you don't have an API key yet, you can still test the bot logic without connecting to Kite:

**Create a mock configuration:**

```json
{
  "_comment": "Mock configuration for testing without Kite API",
  "broker": "mock",
  "paper_trading": true,
  "symbols": ["NIFTY24JANFUT"],
  "timeframe": 30,
  "risk_percent": 0.5,
  ...
}
```

**Note:** This won't fetch real market data but will test the bot's logic.

---

## 🔍 Verify Your API Key

After updating, verify the API key is correct:

```bash
# Check if API key is updated
python -c "import json; print(json.load(open('config_test_paper_trading.json'))['kite_api_key'])"
```

Should output your actual API key, not `"YOUR_KITE_API_KEY_HERE"`.

---

## 🚨 Common Mistakes

### Mistake 1: Using API Secret Instead of API Key
❌ Wrong: Using the API Secret (longer string)
✅ Correct: Use the API Key (shorter string)

### Mistake 2: Extra Quotes or Spaces
❌ Wrong: `"kite_api_key": " your_key "`
✅ Correct: `"kite_api_key": "your_key"`

### Mistake 3: Not Saving the File
❌ Wrong: Editing but not saving
✅ Correct: Save the file after editing (Ctrl+S)

### Mistake 4: Editing Wrong File
❌ Wrong: Editing one config but running another
✅ Correct: Edit the config file you're actually using

---

## 📋 Complete Setup Checklist

- [ ] Have Zerodha trading account
- [ ] Registered for Kite Connect (₹2,000 fee paid)
- [ ] Created app on https://kite.trade/
- [ ] Copied API Key (not API Secret)
- [ ] Opened correct configuration file
- [ ] Replaced `"YOUR_KITE_API_KEY_HERE"` with actual key
- [ ] Saved the file
- [ ] Verified API key is updated
- [ ] Ready to run `python kite_login.py`

---

## 🎯 Next Steps After Fixing

Once you've updated the API key:

### 1. Authenticate
```bash
python kite_login.py
```
This will:
- Open browser for Kite login
- Generate access token
- Save to `kite_token.json`

### 2. Test Configuration
```bash
python test_configuration.py --config config_test_paper_trading.json
```

### 3. Start Paper Trading
```bash
python run_bot.py --config config_test_paper_trading.json
```

---

## 💡 Pro Tips

### Tip 1: Keep API Key Secure
- Don't commit API key to Git
- Don't share configuration files with API key
- Add `config_*.json` to `.gitignore`

### Tip 2: Use Environment Variables (Advanced)
Instead of hardcoding API key in config:

```json
{
  "kite_api_key": "${KITE_API_KEY}",
  ...
}
```

Then set environment variable:
```bash
# Windows
set KITE_API_KEY=your_actual_api_key

# Linux/Mac
export KITE_API_KEY=your_actual_api_key
```

### Tip 3: Create a Separate Config for Testing
Keep your production config separate:

```bash
# Copy test config
cp config_test_paper_trading.json my_config.json

# Edit my_config.json with your API key
# Keep original configs as templates
```

---

## 🆘 Still Having Issues?

### Issue: "Invalid API Key" even after updating

**Possible causes:**
1. API key is incorrect (typo)
2. API key is expired or revoked
3. Kite Connect subscription not active

**Solution:**
1. Login to https://kite.trade/
2. Verify your app is active
3. Regenerate API key if needed
4. Copy the new key carefully

### Issue: "API key not found in config"

**Possible causes:**
1. Wrong configuration file
2. JSON syntax error

**Solution:**
```bash
# Validate JSON syntax
python -m json.tool config_test_paper_trading.json
```

### Issue: Browser doesn't open during login

**Possible causes:**
1. No default browser set
2. Running on server without GUI

**Solution:**
- Manually open the URL shown in terminal
- Complete authentication in browser
- Copy the request token from URL

---

## 📞 Need Help?

### Quick Checks
1. **Verify API key:** Login to https://kite.trade/ and check your app
2. **Check config file:** Ensure API key is updated and saved
3. **Validate JSON:** Use `python -m json.tool config_file.json`
4. **Check subscription:** Ensure Kite Connect is active

### Documentation
- **Kite Connect Docs:** https://kite.trade/docs/connect/v3/
- **API Key Setup:** https://kite.trade/docs/connect/v3/user/#api-key
- **Testing Guide:** `TESTING_GUIDE.md`
- **Quick Start:** `QUICK_START_TESTING.md`

---

## ✅ Success Checklist

After fixing the API key error, you should be able to:

- [ ] Run `python kite_login.py` without errors
- [ ] See browser open for Kite authentication
- [ ] Complete login and see success message
- [ ] Find `kite_token.json` file created
- [ ] Run `python test_configuration.py` successfully
- [ ] Start paper trading without authentication errors

---

## 🎉 You're Ready!

Once the API key is updated and authentication works, you can proceed with testing:

1. ✅ API key updated in configuration
2. ✅ Authentication successful (`kite_token.json` created)
3. ✅ Configuration validated
4. 🚀 Ready to start paper trading!

**Next:** Follow the `QUICK_START_TESTING.md` guide to begin testing.

---

*Last Updated: February 17, 2026*
