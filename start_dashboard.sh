#!/bin/bash
# ================================================================
# GEM Trading Dashboard - Unix/Linux/macOS Launcher
# ================================================================

echo ""
echo "================================================================"
echo "GEM TRADING DASHBOARD"
echo "================================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found!"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✅ Python $PYTHON_VERSION detected"
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Check dependencies
echo "📦 Checking dependencies..."
python3 -c "import flask, MetaTrader5, pandas, numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies!"
    echo ""
    echo "Install with:"
    echo "  pip3 install -r requirements.txt"
    echo ""
    exit 1
fi

echo "✅ All dependencies installed"
echo ""

# Start dashboard
echo "================================================================"
echo "STARTING DASHBOARD SERVER"
echo "================================================================"
echo ""
echo "🌐 Dashboard will be available at:"
echo "   • http://localhost:5000"
echo "   • http://127.0.0.1:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================================================"
echo ""

# Run Python launcher
python3 start_dashboard.py
