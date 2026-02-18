# ⚠️ IMPORTANT: Port Changed to 5001

## What Changed

The Kite login redirect port has been changed from **5000** to **5001** to avoid conflicts with your existing bot.

**Old:** `http://127.0.0.1:5000/`  
**New:** `http://127.0.0.1:5001/`

---

## 🔧 Required Action: Update Kite Connect App Settings

You **MUST** update the redirect URL in your Kite Connect app settings, or authentication will fail.

### Step-by-Step Instructions

#### 1. Login to Kite Connect
Go to: https://kite.trade/

#### 2. Open Your App Settings
- Click on your app name
- Go to "App settings" or "Edit app"

#### 3. Update Redirect URL
Find the **"Redirect URL"** field and change it to:
```
http://127.0.0.1:5001/
```

**Important:** 
- Include the trailing slash `/`
- Use `127.0.0.1` (not `localhost`)
- Port must be `5001`

#### 4. Save Changes
Click "Update" or "Save" to apply the changes.

#### 5. Test Authentication
```bash
python kite_login.py
```

---

## 🎯 Quick Verification

After updating, verify the settings:

### In kite_login.py:
```python
# Should show port 5001
print(f"📋 Redirect URL: http://127.0.0.1:5001/")
```

### In Kite Connect App:
- Redirect URL: `http://127.0.0.1:5001/`

### When Running:
```bash
python kite_login.py
```
Should output:
```
📋 Redirect URL: http://127.0.0.1:5001/
Starting local server and opening browser...
```

---

## 🚨 Common Issues

### Issue 1: "Redirect URL mismatch"

**Error:** 
```
Invalid redirect_uri
```

**Solution:**
- Double-check the redirect URL in Kite Connect app settings
- Ensure it's exactly: `http://127.0.0.1:5001/`
- Include the trailing slash
- Save the changes

### Issue 2: "Port already in use"

**Error:**
```
Address already in use
```

**Solution:**
- Check if another process is using port 5001
- Change to a different port (e.g., 5002, 5003)
- Update both kite_login.py and Kite Connect app settings

### Issue 3: Browser doesn't redirect

**Symptoms:**
- Login successful on Kite
- Browser shows "Cannot connect" or "Connection refused"

**Solution:**
- Verify kite_login.py is running
- Check the port in the browser URL matches 5001
- Ensure firewall isn't blocking port 5001

---

## 🔄 If You Need a Different Port

If port 5001 is also in use, you can change it to any available port:

### 1. Edit kite_login.py

Find and replace all instances of `5001` with your desired port (e.g., `5002`):

```python
# Line ~40: Comment
"""
Kite redirects here after login:
  http://127.0.0.1:5002/?request_token=xxxxx&status=success
"""

# Line ~100: Print statement
print(f"📋 Redirect URL: http://127.0.0.1:5002/")

# Line ~115: Flask server
app.run(
    host="127.0.0.1",
    port=5002,  # Change this
    debug=False,
    use_reloader=False
)
```

### 2. Update Kite Connect App

Update the redirect URL to match:
```
http://127.0.0.1:5002/
```

---

## 📋 Port Configuration Summary

| Component | Port | Status |
|-----------|------|--------|
| Your existing bot | 5000 | ✅ Running |
| Kite login (new) | 5001 | ✅ Updated |
| Available for use | 5002+ | 🟢 Free |

---

## ✅ Checklist

Before running `python kite_login.py`:

- [ ] Port changed to 5001 in kite_login.py
- [ ] Redirect URL updated in Kite Connect app settings
- [ ] Redirect URL is exactly: `http://127.0.0.1:5001/`
- [ ] Changes saved in Kite Connect app
- [ ] Port 5001 is not in use by another process
- [ ] Ready to test authentication

---

## 🎉 You're Ready!

Once you've updated the redirect URL in your Kite Connect app settings, you can run:

```bash
python kite_login.py
```

The authentication will now use port 5001, avoiding conflicts with your existing bot on port 5000.

---

## 📞 Need Help?

### Check Port Usage
```bash
# Windows
netstat -ano | findstr :5001

# Linux/Mac
lsof -i :5001
```

### Test Port Availability
```bash
# Try to start a simple server on port 5001
python -m http.server 5001
# Press Ctrl+C to stop
```

### Verify Kite Connect Settings
1. Login to https://kite.trade/
2. Check your app settings
3. Verify redirect URL is correct
4. Save changes if needed

---

*Last Updated: February 17, 2026*  
*Port Changed: 5000 → 5001*
