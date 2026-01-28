#!/usr/bin/env python3
"""
Cross-Platform Dashboard Launcher
Works on Windows, macOS, and Linux
"""

import os
import sys
import platform
import subprocess
import webbrowser
import time

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
    required = ['flask', 'MetaTrader5', 'pandas', 'numpy']
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
    print("GEM TRADING DASHBOARD - CROSS-PLATFORM LAUNCHER")
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
    print(f"   • http://localhost:5000")
    print(f"   • http://127.0.0.1:5000")
    if local_ip != "localhost":
        print(f"   • http://{local_ip}:5000 (network access)")
    print()
    
    print("⚙️  Starting server...")
    print("   (This may take a few seconds)")
    print()
    
    # Start the dashboard
    try:
        # Import here to avoid issues if dependencies missing
        import web_dashboard
        
        # Open browser after short delay
        def open_browser():
            time.sleep(2)
            webbrowser.open('http://localhost:5000')
        
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
        web_dashboard.app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("SERVER STOPPED")
        print("=" * 70)
        print("\n✅ Dashboard shut down successfully")
        
    except Exception as e:
        print(f"\n❌ Error starting dashboard: {str(e)}")
        print("\n📋 Troubleshooting:")
        print("   1. Make sure MT5 is installed")
        print("   2. Check that port 5000 is not in use")
        print("   3. Verify all dependencies are installed")
        print("   4. Check trading_bot.log for details")
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
