@echo off
REM Indian Market Web Dashboard - Startup Script (Windows)

echo ==========================================
echo Indian Market Web Dashboard
echo ==========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Virtual environment not found. Creating...
    python -m venv venv
    echo Virtual environment created.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import flask" 2>nul
if errorlevel 1 (
    echo Dependencies not found. Installing...
    pip install -r requirements.txt
    echo Dependencies installed.
)

REM Check if .env file exists
if not exist ".env" (
    echo.
    echo WARNING: .env file not found!
    echo Creating .env from .env.example...
    copy .env.example .env
    echo.
    echo IMPORTANT: Please edit .env file and set your secret keys!
    echo Generate keys with:
    echo   Flask Secret: python -c "import secrets; print(secrets.token_hex(32))"
    echo   Encryption Key: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    echo.
    pause
)

REM Create required directories
echo Ensuring required directories exist...
if not exist "data\cache\" mkdir data\cache
if not exist "data\credentials\" mkdir data\credentials
if not exist "configs\" mkdir configs
if not exist "logs\" mkdir logs

REM Start the dashboard
echo.
echo Starting dashboard...
echo Access at: http://127.0.0.1:8080
echo Press Ctrl+C to stop
echo.

python indian_dashboard.py %*
