#!/usr/bin/env python3
"""
Indian Market Dashboard Launcher
Cross-platform launcher for the Indian Market Trading Dashboard
"""

import os
import sys
import platform
import webbrowser
import time

# Fix for Unicode characters on Windows
if sys.platform == "win32":
    try:
        import codecs
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, Exception):
        pass

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} detected")
        print("⚠️  Python 3.8 or higher is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required = ['flask', 'kiteconnect', 'pandas', 'numpy', 'cryptography']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("\n📦 Install with:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    print("✅ All dependencies installed")
    return True

def get_local_ip():
    """Get local IP address for network access"""
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

def main():
    """Main launcher function"""
    print("=" * 70)
    print("INDIAN MARKET TRADING DASHBOARD - LAUNCHER")
    print("=" * 70)
    print()
    
    # Detect OS
    os_name = platform.system()
    print(f"🖥️  Operating System: {os_name} ({platform.platform()})")
    print()
    
    # Check Python version
    if not check_python_version():
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    if not check_dependencies():
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    print()
    print("=" * 70)
    print("STARTING DASHBOARD SERVER")
    print("=" * 70)
    print()
    
    # Get IP address
    local_ip = get_local_ip()
    
    print("🌐 Dashboard will be available at:")
    print(f"   • http://localhost:8080")
    print(f"   • http://127.0.0.1:8080")
    if local_ip != "localhost":
        print(f"   • http://{local_ip}:8080 (network access)")
    print()
    
    print("⚙️  Starting server...")
    print("   (This may take a few seconds)")
    print()
    
    # Start the dashboard
    try:
        # Add project root and dashboard directory to path
        # This is needed for both 'import indian_dashboard' and internal sibling imports
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        dash_dir = os.path.join(root_dir, 'indian_dashboard')
        sys.path.insert(0, root_dir)
        sys.path.insert(0, dash_dir)
        
        # Import the dashboard
        from indian_dashboard import app
        
        # Open browser after short delay
        def open_browser():
            time.sleep(2)
            webbrowser.open('http://localhost:8080')
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        print("✅ Server starting...")
        print("🌐 Opening browser...")
        print()
        print("=" * 70)
        print("Press Ctrl+C to stop the server")
        print("=" * 70)
        print()
        
        # Run the Flask app
        app.run(debug=False, host='0.0.0.0', port=8080, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("SERVER STOPPED")
        print("=" * 70)
        print("\n✅ Dashboard shut down successfully")
        
    except Exception as e:
        print(f"\n❌ Error starting dashboard: {str(e)}")
        print("\n📋 Troubleshooting:")
        print("   1. Check that port 8080 is not in use")
        print("   2. Verify all dependencies are installed")
        print("   3. Check dashboard.log for details")
        print(f"\n   Error details: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
