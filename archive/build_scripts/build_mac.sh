#!/bin/bash
# ================================================================
# GEM Trading Bot - macOS Standalone Build Script
# ================================================================

echo ""
echo "================================================================"
echo "GEM TRADING BOT - macOS BUILD"
echo "================================================================"
echo ""
echo "This will create a standalone macOS application (.app)"
echo "Users can run it without installing Python or dependencies."
echo ""
echo "Build time: 5-10 minutes"
echo "Final size: ~150-200 MB"
echo ""
read -p "Press Enter to continue..."

# Check Python version
echo ""
echo "Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "ERROR: Python not found! Please install Python 3.8 or higher."
    exit 1
fi

# Install/upgrade PyInstaller
echo ""
echo "Step 1: Installing PyInstaller..."
pip3 install --upgrade pyinstaller
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install PyInstaller"
    exit 1
fi

# Clean previous builds
echo ""
echo "Step 2: Cleaning previous builds..."
rm -rf build
rm -rf dist
rm -f GEM_Trading_Bot.spec

# Create build directories
mkdir -p build
mkdir -p dist

# Build application
echo ""
echo "Step 3: Building macOS application..."
echo "This may take 5-10 minutes, please wait..."
echo ""

pyinstaller \
    --name="GEM_Trading_Bot" \
    --onefile \
    --windowed \
    --add-data="templates:templates" \
    --add-data="src:src" \
    --hidden-import=MetaTrader5 \
    --hidden-import=pandas \
    --hidden-import=numpy \
    --hidden-import=flask \
    --hidden-import=werkzeug \
    --hidden-import=jinja2 \
    --hidden-import=click \
    --hidden-import=itsdangerous \
    --hidden-import=markupsafe \
    --hidden-import=logging \
    --hidden-import=threading \
    --hidden-import=datetime \
    --collect-all=flask \
    --collect-all=werkzeug \
    --collect-all=jinja2 \
    --osx-bundle-identifier=com.gemtrading.bot \
    web_dashboard.py

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Build failed!"
    echo "Check the error messages above."
    exit 1
fi

# Create distribution package
echo ""
echo "Step 4: Creating distribution package..."

mkdir -p "dist/GEM_Trading_Bot_macOS"

# Copy application
if [ -d "dist/GEM_Trading_Bot.app" ]; then
    cp -R "dist/GEM_Trading_Bot.app" "dist/GEM_Trading_Bot_macOS/"
else
    cp "dist/GEM_Trading_Bot" "dist/GEM_Trading_Bot_macOS/"
fi

# Copy documentation
cp "USER_GUIDE.md" "dist/GEM_Trading_Bot_macOS/" 2>/dev/null || true
cp "QUICK_START_CARD.md" "dist/GEM_Trading_Bot_macOS/" 2>/dev/null || true
cp "INSTALLATION_GUIDE_FOR_USERS.md" "dist/GEM_Trading_Bot_macOS/" 2>/dev/null || true
cp "TROUBLESHOOTING.md" "dist/GEM_Trading_Bot_macOS/" 2>/dev/null || true
cp "README.md" "dist/GEM_Trading_Bot_macOS/" 2>/dev/null || true

# Create README for distribution
echo "Creating distribution README..."
cat > "dist/GEM_Trading_Bot_macOS/README.txt" << 'EOF'
# GEM Trading Bot - macOS Edition

## Quick Start

1. Make sure MT5 is installed and running
2. Double-click GEM_Trading_Bot.app (or run ./GEM_Trading_Bot)
3. Open browser to http://localhost:5000
4. Configure and start trading!

## First Time Setup

If you see "App can't be opened because it is from an unidentified developer":

1. Right-click (or Control-click) the app
2. Select "Open" from the menu
3. Click "Open" in the dialog
4. The app will now run

Alternatively, go to System Preferences > Security & Privacy > General
and click "Open Anyway"

## Documentation

- USER_GUIDE.md - Complete user manual
- QUICK_START_CARD.md - Quick reference
- INSTALLATION_GUIDE_FOR_USERS.md - Setup instructions
- TROUBLESHOOTING.md - Common issues and solutions

## System Requirements

- macOS 10.14 (Mojave) or higher
- MT5 installed (Wine or native if available)
- 4GB RAM minimum
- Internet connection

## Support

For help, check TROUBLESHOOTING.md or contact support.

## Version

Version: 2.0
Build Date: $(date)

EOF

# Get file size
echo ""
echo "================================================================"
echo "BUILD COMPLETE!"
echo "================================================================"
echo ""

if [ -d "dist/GEM_Trading_Bot.app" ]; then
    echo "Application: dist/GEM_Trading_Bot.app"
    du -sh "dist/GEM_Trading_Bot.app"
else
    echo "Executable: dist/GEM_Trading_Bot"
    ls -lh "dist/GEM_Trading_Bot" | awk '{print "File Size: " $5}'
fi

echo ""
echo "Distribution package: dist/GEM_Trading_Bot_macOS/"
echo ""
echo "Package contents:"
ls -1 "dist/GEM_Trading_Bot_macOS"
echo ""
echo "================================================================"
echo "NEXT STEPS"
echo "================================================================"
echo ""
echo "1. TEST THE APPLICATION:"
echo "   cd dist"
if [ -d "dist/GEM_Trading_Bot.app" ]; then
    echo "   open GEM_Trading_Bot.app"
else
    echo "   ./GEM_Trading_Bot"
fi
echo ""
echo "2. VERIFY IT WORKS:"
echo "   - Opens browser to http://localhost:5000"
echo "   - Dashboard loads correctly"
echo "   - Can connect to MT5"
echo ""
echo "3. CREATE DMG FOR DISTRIBUTION:"
echo "   hdiutil create -volname \"GEM Trading Bot\" -srcfolder dist/GEM_Trading_Bot_macOS -ov -format UDZO GEM_Trading_Bot_v2.0_macOS.dmg"
echo ""
echo "   OR create ZIP:"
echo "   cd dist"
echo "   zip -r GEM_Trading_Bot_v2.0_macOS.zip GEM_Trading_Bot_macOS"
echo ""
echo "4. DISTRIBUTE:"
echo "   - Upload to file sharing service"
echo "   - Share download link with users"
echo "   - Include installation instructions"
echo ""
echo "================================================================"
echo ""
