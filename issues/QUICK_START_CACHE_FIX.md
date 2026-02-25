# Quick Start - Fix Tips Box and Styling Issues

## The Problem
Tips box text is unreadable (brown text on yellow background) due to browser cache preventing CSS changes from loading.

## The Solution (Choose ONE)

### ⚡ FASTEST: Use Incognito Mode (30 seconds)
1. Keep Flask server running (or restart it: `python indian_dashboard/run_dashboard.py`)
2. Press `Ctrl+Shift+N` (Chrome/Edge) to open Incognito window
3. Go to `http://127.0.0.1:8080`
4. ✓ Done! Styles will be correct

### 🤖 AUTOMATED: Run Restart Script (1 minute)
1. Double-click `restart_dashboard.bat`
2. Wait for Flask to start (5 seconds)
3. Open Incognito window (`Ctrl+Shift+N`)
4. Go to `http://127.0.0.1:8080`
5. ✓ Done!

### 🔧 MANUAL: Clear Cache (2 minutes)
1. Stop Flask server (`Ctrl+C` in terminal)
2. In browser: `Ctrl+Shift+Delete`
3. Select "All time" and "Cached images and files"
4. Click "Clear data"
5. Restart Flask: `python indian_dashboard/run_dashboard.py`
6. Hard refresh page: `Ctrl+F5`
7. ✓ Done!

## What You Should See

### ✓ Tips Box
- Light yellow background
- **BLACK text** (clearly readable)
- Yellow left border

### ✓ Instrument Tags
- BLACK background
- WHITE symbol text
- YELLOW exchange text

## Still Not Working?

### Check Console (F12)
Should see these messages:
```
🔄 Forcing cache clear and style application...
✓ Styles forcefully applied
✓ Mutation observer set up for dynamic elements
```

### Try This
1. Close ALL browser windows
2. Reopen browser
3. Use Incognito mode
4. Go to dashboard

### Last Resort
1. Try different browser (Chrome → Edge or vice versa)
2. Check Flask is running: `http://127.0.0.1:8080/api/cache-version`
3. Should return: `{"version": "1739923200"}` (some timestamp)

## Need More Help?
Read `CACHE_CLEARING_GUIDE.md` for detailed instructions and troubleshooting.

## Test First
Open `test_styles.html` in browser to verify styles work correctly before testing dashboard.
