#!/bin/bash
# Indian Market Web Dashboard - Startup Script (Unix/Linux/macOS)

set -e  # Exit on error

echo "=========================================="
echo "Indian Market Web Dashboard"
echo "=========================================="
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}Error: Python $REQUIRED_VERSION or higher is required${NC}"
    echo "Current version: $PYTHON_VERSION"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION detected"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "Virtual environment not found. Creating..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import flask" 2>/dev/null; then
    echo ""
    echo "Dependencies not found. Installing..."
    pip install -r requirements.txt
    echo -e "${GREEN}✓${NC} Dependencies installed"
else
    echo -e "${GREEN}✓${NC} Dependencies already installed"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo ""
    echo -e "${YELLOW}WARNING: .env file not found!${NC}"
    
    if [ -f ".env.example" ]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
        echo -e "${GREEN}✓${NC} .env file created"
        echo ""
        echo -e "${YELLOW}IMPORTANT: Please edit .env file and set your secret keys!${NC}"
        echo "Generate keys with:"
        echo "  Flask Secret: python -c \"import secrets; print(secrets.token_hex(32))\""
        echo "  Encryption Key: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        echo ""
        read -p "Press Enter to continue..."
    else
        echo -e "${YELLOW}No .env.example found. Using default configuration.${NC}"
    fi
fi

# Create required directories
echo "Ensuring required directories exist..."
mkdir -p ../data/cache
mkdir -p ../data/credentials
mkdir -p ../configs
mkdir -p ../logs
echo -e "${GREEN}✓${NC} Directories created"

# Start the dashboard
echo ""
echo "=========================================="
echo "Starting dashboard..."
echo "Access at: http://127.0.0.1:8080"
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

# Use run_dashboard.py if available, otherwise use indian_dashboard.py
if [ -f "run_dashboard.py" ]; then
    python run_dashboard.py "$@"
else
    python indian_dashboard.py "$@"
fi
