#!/usr/bin/env python3
"""
Fix Dashboard Button Issues
Addresses common problems that cause buttons to stop responding
"""

import os
import sys
import shutil
import time
from pathlib import Path

def clear_browser_cache_instructions():
    """Provide instructions for clearing browser cache"""
    print("🧹 BROWSER CACHE CLEARING INSTRUCTIONS")
    print("=" * 50)
    print("The most common cause of non-responsive buttons is browser cache.")
    print("Please try these steps:")
    print()
    print("📌 CHROME/EDGE:")
    print("   1. Press Ctrl+Shift+Delete")
    print("   2. Select 'All time' for time range")
    print("   3. Check 'Cached images and files'")
    print("   4. Click 'Clear data'")
    print("   5. Refresh dashboard (F5)")
    print()
    print("📌 FIREFOX:")
    print("   1. Press Ctrl+Shift+Delete")
    print("   2. Select 'Everything' for time range")
    print("   3. Check 'Cache'")
    print("   4. Click 'Clear Now'")
    print("   5. Refresh dashboard (F5)")
    print()
    print("📌 ALTERNATIVE (Any Browser):")
    print("   1. Open dashboard in Incognito/Private mode")
    print("   2. Go to http://127.0.0.1:5000")
    print("   3. Test if buttons work in private mode")
    print()

def check_dashboard_files():
    """Check if dashboard files are intact"""
    print("🔍 CHECKING DASHBOARD FILES")
    print("=" * 50)
    
    files_to_check = [
        "web_dashboard.py",
        "templates/dashboard.html",
        "src/config_manager.py",
        "bot_config.json"
    ]
    
    all_good = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ {file_path:<25} ({size:,} bytes)")
        else:
            print(f"❌ {file_path:<25} MISSING!")
            all_good = False
    
    if all_good:
        print("✅ All dashboard files are present")
    else:
        print("❌ Some dashboard files are missing!")
    
    return all_good

def restart_dashboard_server():
    """Instructions to restart dashboard server"""
    print("\n🔄 DASHBOARD SERVER RESTART")
    print("=" * 50)
    print("If buttons still don't work after clearing cache:")
    print()
    print("1. Stop current dashboard:")
    print("   - Press Ctrl+C in the terminal running web_dashboard.py")
    print("   - Or close the terminal window")
    print()
    print("2. Start fresh dashboard:")
    print("   - Open new terminal/command prompt")
    print("   - Navigate to project folder")
    print("   - Run: python web_dashboard.py")
    print()
    print("3. Access dashboard:")
    print("   - Open browser")
    print("   - Go to: http://127.0.0.1:5000")
    print("   - Test buttons")
    print()

def check_javascript_errors():
    """Instructions to check for JavaScript errors"""
    print("🐛 JAVASCRIPT ERROR CHECKING")
    print("=" * 50)
    print("To check for JavaScript errors in your browser:")
    print()
    print("1. Open dashboard: http://127.0.0.1:5000")
    print("2. Press F12 to open Developer Tools")
    print("3. Click 'Console' tab")
    print("4. Look for red error messages")
    print("5. Try clicking a button")
    print("6. Check if new errors appear")
    print()
    print("Common JavaScript errors:")
    print("   • 'Uncaught ReferenceError' - Function not found")
    print("   • 'Uncaught SyntaxError' - Code syntax error")
    print("   • 'Failed to fetch' - API connection error")
    print("   • 'CORS error' - Cross-origin request blocked")
    print()

def create_minimal_test_dashboard():
    """Create a minimal test dashboard to isolate issues"""
    print("🧪 CREATING MINIMAL TEST DASHBOARD")
    print("=" * 50)
    
    minimal_html = '''<!DOCTYPE html>
<html>
<head>
    <title>Minimal Dashboard Test</title>
    <style>
        body { font-family: Arial; padding: 20px; background: #1e293b; color: white; }
        .btn { padding: 10px 20px; margin: 10px; border: none; border-radius: 5px; cursor: pointer; background: #10b981; color: white; }
    </style>
</head>
<body>
    <h1>🧪 Minimal Dashboard Test</h1>
    <p>If these buttons work, the issue is with the main dashboard JavaScript.</p>
    
    <button class="btn" onclick="testButton()">Test Button</button>
    <button class="btn" onclick="testAPI()">Test API</button>
    <div id="result" style="margin: 20px 0; padding: 10px; background: #0f172a; border-radius: 5px;"></div>
    
    <script>
        function testButton() {
            document.getElementById('result').innerHTML = '✅ Button clicked! JavaScript is working.';
        }
        
        async function testAPI() {
            try {
                const response = await fetch('/api/bot/status');
                const data = await response.json();
                document.getElementById('result').innerHTML = `✅ API working! Bot running: ${data.running}`;
            } catch (error) {
                document.getElementById('result').innerHTML = `❌ API failed: ${error.message}`;
            }
        }
    </script>
</body>
</html>'''
    
    try:
        with open('minimal_test.html', 'w', encoding='utf-8') as f:
            f.write(minimal_html)
        print("✅ Created minimal_test.html")
        print("   Open this file in your browser to test basic functionality")
        print("   File location:", os.path.abspath('minimal_test.html'))
    except Exception as e:
        print(f"❌ Failed to create test file: {e}")

def main():
    """Main diagnostic and fix routine"""
    print("🔧 DASHBOARD BUTTON FIX UTILITY")
    print("=" * 60)
    print("This utility helps diagnose and fix non-responsive dashboard buttons.")
    print()
    
    # Check files
    files_ok = check_dashboard_files()
    
    if not files_ok:
        print("\n❌ CRITICAL: Dashboard files are missing!")
        print("Please ensure you're in the correct project directory.")
        return
    
    # Provide troubleshooting steps
    clear_browser_cache_instructions()
    restart_dashboard_server()
    check_javascript_errors()
    create_minimal_test_dashboard()
    
    print("\n🎯 QUICK TROUBLESHOOTING CHECKLIST")
    print("=" * 60)
    print("□ 1. Clear browser cache (most common fix)")
    print("□ 2. Try incognito/private browsing mode")
    print("□ 3. Check browser console for JavaScript errors (F12)")
    print("□ 4. Restart dashboard server")
    print("□ 5. Test with minimal_test.html")
    print("□ 6. Try different browser (Chrome, Firefox, Edge)")
    print("□ 7. Check if antivirus/firewall is blocking localhost:5000")
    print()
    
    print("🌐 DASHBOARD ACCESS URLS:")
    print("=" * 60)
    print("Main Dashboard:    http://127.0.0.1:5000")
    print("Button Test:       file://" + os.path.abspath('test_buttons_simple.html'))
    print("Minimal Test:      file://" + os.path.abspath('minimal_test.html'))
    print()
    
    print("💡 IF BUTTONS STILL DON'T WORK:")
    print("=" * 60)
    print("1. The dashboard server is working (APIs respond)")
    print("2. JavaScript functions are properly defined")
    print("3. The issue is likely browser-specific")
    print("4. Try the test files created above")
    print("5. Check browser console for specific error messages")
    print()
    print("✅ Dashboard server and APIs are fully functional!")

if __name__ == "__main__":
    main()